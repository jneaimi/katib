#!/usr/bin/env python3
"""Katib vault-API client.

Phase 2 of the vault-integration migration (ADR §20). Replaces direct
filesystem writes of `manifest.md` with governed API calls to Soul Hub's
`POST /api/vault/notes`. Falls back to filesystem when the API is
unreachable — with a `katib-fallback` tag so the vault watcher + a later
reconcile job can identify unreconciled writes.

Contract (verified against soul-hub/src/routes/api/vault/notes):
    POST {SOUL_HUB_URL}/api/vault/notes
    body: {"zone": <folder>, "filename": <name>.md, "meta": {...}, "content": "..."}
    201 → {"success": true, "path": "<full-path>"}
    400 → {"success": false, "error": "<reason>", "field"?: "<name>"}
    409 → {"success": false, "error": "File already exists: ..."}
    413 → {"success": false, "error": "Note exceeds maximum size ..."}
    429 → {"success": false, "error": "Rate limit exceeded ..."}

No auth required. Base URL defaults to http://localhost:2400, override via
SOUL_HUB_URL env var.

Env:
    SOUL_HUB_URL        Base URL (default: http://localhost:2400)
    KATIB_VAULT_MODE    api (default) | strict | fs
                        - api:    prefer API, fall back to FS on network failure
                        - strict: API only, fail hard on any connection issue
                        - fs:     skip API entirely (legacy/offline behaviour)
    KATIB_VAULT_TIMEOUT Request timeout in seconds (default: 5)
"""
from __future__ import annotations

import json
import os
import socket
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "http://localhost:2400"
DEFAULT_TIMEOUT = 5.0


class VaultError(Exception):
    """Base class — anything vault-client raises is one of these."""


class VaultGovernanceError(VaultError):
    """400-class response from the API — the payload broke a governance rule.

    This is never recoverable via fallback; the caller should surface it and
    let the human fix the metadata.
    """

    def __init__(self, message: str, *, status: int, field: str | None = None, payload: dict | None = None):
        super().__init__(message)
        self.status = status
        self.field = field
        self.payload = payload or {}


class VaultConflictError(VaultError):
    """409 — file already exists or duplicate-content detector flagged it.

    Also never recoverable via fallback — a re-run with a different slug
    (or an explicit PUT for updates) is the right answer.
    """

    def __init__(self, message: str, *, payload: dict | None = None):
        super().__init__(message)
        self.payload = payload or {}


class VaultNetworkError(VaultError):
    """Soul Hub unreachable. Callers in mode=api should fall back to FS."""


@dataclass
class VaultWriteResult:
    """Outcome of a create_note call.

    `backend` is one of:
      - "api"      : wrote via Soul Hub POST /api/vault/notes
      - "fallback" : FS write after api mode couldn't reach Soul Hub
      - "fs"       : FS write because mode=fs (no API attempt)
    """
    ok: bool
    backend: str
    path: Path
    status: int | None = None
    error: str | None = None


def _base_url() -> str:
    return os.environ.get("SOUL_HUB_URL", DEFAULT_BASE_URL).rstrip("/")


def _timeout() -> float:
    try:
        return float(os.environ.get("KATIB_VAULT_TIMEOUT", DEFAULT_TIMEOUT))
    except ValueError:
        return DEFAULT_TIMEOUT


def _mode() -> str:
    mode = os.environ.get("KATIB_VAULT_MODE", "api").lower().strip()
    if mode not in ("api", "strict", "fs"):
        print(f"⚠ unknown KATIB_VAULT_MODE={mode!r}, defaulting to 'api'", file=sys.stderr)
        return "api"
    return mode


def _fs_write(
    vault_root: Path,
    zone: str,
    filename: str,
    frontmatter_yaml: str,
    body: str,
    *,
    fallback: bool = False,
) -> VaultWriteResult:
    """Direct filesystem write — legacy path, also used when API unreachable.

    When `fallback=True`, adds `katib-fallback` to the `tags:` line in the
    frontmatter so the vault watcher + a later reconcile job can spot
    unreconciled writes. We edit the rendered YAML text rather than the
    dict here because the caller has already serialised it.
    """
    target_dir = vault_root / zone
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / filename

    fm = frontmatter_yaml
    if fallback:
        fm = _inject_fallback_tag(fm)

    path.write_text(f"---\n{fm}\n---\n\n{body}", encoding="utf-8")
    return VaultWriteResult(
        ok=True,
        backend="fallback" if fallback else "fs",
        path=path,
    )


def _inject_fallback_tag(frontmatter_yaml: str) -> str:
    """Splice `katib-fallback` into the existing `tags: [...]` line.

    We keep the edit textual to avoid re-parsing YAML. If no tags: line is
    present (shouldn't happen — Phase 1 validator enforces it) we append one.
    """
    import re

    def _splice(match: "re.Match[str]") -> str:
        inner = match.group(1).strip()
        # Empty list: "tags: []"
        if not inner:
            return "tags: [katib-fallback]"
        # Already contains the tag — leave alone (keeps idempotence when the
        # caller retries a fallback write on the same folder).
        if "katib-fallback" in inner:
            return match.group(0)
        return f"tags: [{inner}, katib-fallback]"

    new, n = re.subn(r"^tags:\s*\[([^\]]*)\]\s*$", _splice, frontmatter_yaml, count=1, flags=re.MULTILINE)
    if n == 0:
        # No tags line — append one at the end of frontmatter.
        return frontmatter_yaml.rstrip() + "\ntags: [katib-fallback]"
    return new


def _api_post(zone: str, filename: str, meta: dict[str, Any], content: str) -> tuple[int, dict[str, Any]]:
    """Raw POST. Returns (status_code, parsed_json_body). Raises VaultNetworkError on connection failures."""
    url = f"{_base_url()}/api/vault/notes"
    payload = json.dumps({
        "zone": zone,
        "filename": filename,
        "meta": meta,
        "content": content,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=_timeout()) as resp:
            body_bytes = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
        body_bytes = e.read()
    except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
        raise VaultNetworkError(f"cannot reach Soul Hub at {url}: {e}") from e

    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Non-JSON response — wrap it so callers still see the status.
        data = {"success": False, "error": f"non-JSON response (status {status})"}

    return status, data


def create_note(
    zone: str,
    filename: str,
    meta: dict[str, Any],
    content: str,
    *,
    vault_root: Path,
    frontmatter_yaml: str,
) -> VaultWriteResult:
    """Create a note — API first (respecting KATIB_VAULT_MODE), with FS fallback.

    Args:
      zone: folder path under the vault, e.g. "content/katib/business-proposal/2026-04-22-foo".
        Must NOT start with "/" and must not contain "..". This is what the API
        passes to GovernanceResolver.
      filename: just the filename (no slashes), e.g. "manifest.md".
      meta: frontmatter dict — must have `type`, `created`, `tags` at minimum
        plus whatever the zone's CLAUDE.md requires. Validate with meta_validator
        before calling.
      content: body text (no `---` delimiters — those are added by the server).
      vault_root: where FS writes land. Used for fs mode and for fallback in api mode.
      frontmatter_yaml: the frontmatter already rendered as YAML — used for FS
        writes so we don't re-implement the YAML writer here. The API path
        ignores this and uses `meta` directly.

    Returns:
      VaultWriteResult — backend field tells you which path was taken.

    Raises:
      VaultGovernanceError: API returned 400/413/429 — payload violated a rule.
      VaultConflictError:   API returned 409 — duplicate path or content.
      VaultNetworkError:    KATIB_VAULT_MODE=strict and API was unreachable.
    """
    mode = _mode()

    if mode == "fs":
        return _fs_write(vault_root, zone, filename, frontmatter_yaml, content, fallback=False)

    # mode in {"api", "strict"} — try the API first
    try:
        status, data = _api_post(zone, filename, meta, content)
    except VaultNetworkError:
        if mode == "strict":
            raise
        # mode=api: log + fall back to FS with the marker tag
        print(
            f"⚠ Soul Hub unreachable — falling back to FS write with 'katib-fallback' tag. "
            f"Run the vault reconcile job later to replay governance.",
            file=sys.stderr,
        )
        return _fs_write(vault_root, zone, filename, frontmatter_yaml, content, fallback=True)

    if status == 201 and data.get("success"):
        api_path = data.get("path") or f"{zone}/{filename}"
        return VaultWriteResult(
            ok=True,
            backend="api",
            path=vault_root / api_path,
            status=status,
        )

    # Non-2xx — figure out which exception to raise
    error_msg = data.get("error", f"HTTP {status} from vault API")

    if status == 409:
        raise VaultConflictError(error_msg, payload=data)

    # 400/413/429 all map to governance errors — same reaction from the caller
    # (fail loud, print the message, don't fall back).
    raise VaultGovernanceError(
        error_msg,
        status=status,
        field=data.get("field"),
        payload=data,
    )


def derive_zone_and_filename(slug_dir: Path, vault_root: Path, filename: str) -> tuple[str, str]:
    """Compute (zone, filename) for a POST body from a slug_dir path.

    Splits `slug_dir` relative to `vault_root`; the whole relative path becomes
    the zone and the passed-in filename is used as-is.

    e.g. slug_dir = ~/vault/content/katib/business-proposal/2026-04-22-proposal-foo/
         vault_root = ~/vault/
         filename   = "manifest.md"
         → zone = "content/katib/business-proposal/2026-04-22-proposal-foo"
           filename = "manifest.md"
    """
    try:
        rel = slug_dir.resolve().relative_to(vault_root.resolve())
    except ValueError as e:
        raise VaultError(
            f"slug_dir {slug_dir} is not under vault_root {vault_root} — "
            f"API writes require the destination to be inside the vault"
        ) from e
    return rel.as_posix(), filename


# ===================== CLI (debugging aid) =====================

def _cli() -> int:
    """python3 vault_client.py --zone ... --file ... --meta ... --content ...

    Useful for quick API probing during dev. Not in Katib's normal write path.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Katib vault-API client (debug CLI)")
    parser.add_argument("--zone", required=True)
    parser.add_argument("--filename", required=True)
    parser.add_argument("--meta", required=True, help="JSON object")
    parser.add_argument("--content", required=True)
    parser.add_argument("--vault-root", default=os.path.expanduser("~/vault"))
    parser.add_argument(
        "--frontmatter-yaml",
        default="",
        help="YAML string to write on FS fallback (defaults to a minimal rendering of --meta)",
    )

    args = parser.parse_args()

    try:
        meta = json.loads(args.meta)
    except json.JSONDecodeError as e:
        print(f"✗ invalid --meta JSON: {e}", file=sys.stderr)
        return 1

    # Render a minimal YAML if the caller didn't supply one — uses manifest.py's
    # writer to stay consistent with real renders.
    fm_yaml = args.frontmatter_yaml
    if not fm_yaml:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from manifest import _yaml_dump  # noqa: E402
        fm_yaml = _yaml_dump(meta)

    try:
        result = create_note(
            args.zone,
            args.filename,
            meta,
            args.content,
            vault_root=Path(args.vault_root),
            frontmatter_yaml=fm_yaml,
        )
    except VaultGovernanceError as e:
        print(f"✗ governance: [{e.status}] {e}", file=sys.stderr)
        if e.field:
            print(f"  field: {e.field}", file=sys.stderr)
        return 4
    except VaultConflictError as e:
        print(f"✗ conflict: {e}", file=sys.stderr)
        return 5
    except VaultNetworkError as e:
        print(f"✗ network: {e}", file=sys.stderr)
        return 6

    print(f"✓ {result.backend}: {result.path}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
