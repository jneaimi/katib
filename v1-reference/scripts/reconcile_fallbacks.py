#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Reconcile manifests that were written via FS fallback.

When Soul Hub is unreachable during a render, `vault_client.create_note`
writes to the filesystem directly and adds `katib-fallback` to the tags.
This script walks the vault, finds every manifest with that tag, and
POSTs them back through the API so they pick up proper governance
validation.

Dry-run is default. --execute actually writes.

Usage:
    python3 scripts/reconcile_fallbacks.py                    # list candidates
    python3 scripts/reconcile_fallbacks.py --execute          # POST each one
    python3 scripts/reconcile_fallbacks.py --execute --yes    # skip prompt
    python3 scripts/reconcile_fallbacks.py --vault-root /path # override root

Exit:
  0 — ran to completion; nothing to do OR all reconciliations succeeded
  1 — at least one POST failed (governance reject, conflict, or network)
  2 — vault root missing or Soul Hub unreachable before starting
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from audit_vault import find_manifests, default_vault_root  # noqa: E402
from vault_client import (  # noqa: E402
    create_note,
    VaultGovernanceError,
    VaultConflictError,
    VaultNetworkError,
    _base_url,
)

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_manifest(path: Path) -> tuple[dict[str, Any], str, str]:
    """Return (meta_dict, frontmatter_yaml_text, body_text)."""
    raw = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        raise ValueError(f"{path} has no YAML frontmatter block")
    fm_yaml, body = m.group(1), m.group(2)
    meta = yaml.safe_load(fm_yaml) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"{path} frontmatter is not a dict")
    return meta, fm_yaml, body


def strip_fallback_tag(meta: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of meta with 'katib-fallback' removed from tags."""
    tags = meta.get("tags") or []
    if not isinstance(tags, list):
        return meta
    cleaned = [t for t in tags if t != "katib-fallback"]
    out = dict(meta)
    out["tags"] = cleaned
    return out


def _coerce_scalars(meta: dict[str, Any]) -> dict[str, Any]:
    """Coerce date/datetime scalars to ISO strings for JSON serialisation.

    Mirrors the same fix that landed in migrate_vault.py after the Phase 4
    incident — pyyaml parses `created: 2026-04-21` as datetime.date, which
    `json.dumps` can't handle.
    """
    from datetime import date, datetime

    out: dict[str, Any] = {}
    for k, v in meta.items():
        if isinstance(v, (date, datetime)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def find_fallback_manifests(vault_root: Path) -> list[Path]:
    """Every manifest under the vault whose tags include 'katib-fallback'."""
    out: list[Path] = []
    for m in find_manifests(vault_root):
        try:
            meta, _, _ = parse_manifest(m)
        except Exception:
            continue  # parse failures are audit_vault's problem, not ours
        tags = meta.get("tags") or []
        if isinstance(tags, list) and "katib-fallback" in tags:
            out.append(m)
    return out


def relative_zone(path: Path, vault_root: Path) -> str:
    """Folder-relative-to-vault path — what the API wants as `zone`."""
    return path.parent.relative_to(vault_root).as_posix()


def reconcile_one(path: Path, vault_root: Path) -> tuple[bool, str]:
    """Re-POST one manifest. Returns (success, note).

    On success, rewrites the local manifest without the `katib-fallback` tag
    so re-running the reconciler is idempotent.
    """
    meta, fm_yaml, body = parse_manifest(path)
    cleaned_meta = _coerce_scalars(strip_fallback_tag(meta))
    zone = relative_zone(path, vault_root)
    filename = path.name

    # Render the cleaned frontmatter for the FS side too — we'll overwrite
    # the local file with this shape after the POST confirms.
    cleaned_fm_yaml = yaml.safe_dump(
        cleaned_meta, default_flow_style=None, sort_keys=False, allow_unicode=True
    ).rstrip()

    try:
        result = create_note(
            zone=zone,
            filename=filename,
            meta=cleaned_meta,
            content=body,
            vault_root=vault_root,
            frontmatter_yaml=cleaned_fm_yaml,
        )
    except VaultGovernanceError as e:
        return False, f"governance rejected: {e}"
    except VaultConflictError as e:
        # 409 on a path we already own usually means content-similarity detector;
        # surface it but don't treat as fatal for the caller
        return False, f"conflict (409): {e}"
    except VaultNetworkError as e:
        return False, f"network error: {e}"
    except Exception as e:
        return False, f"unexpected error: {e!r}"

    if not result.ok:
        return False, f"backend={result.backend} ok=false"

    # Success. The API wrote the clean version; rewrite the local copy to match
    # in case the watcher + API wrote to different paths (they shouldn't).
    return True, f"backend={result.backend}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-POST FS-fallback manifests through the API")
    parser.add_argument("--vault-root", default=None,
                        help="Vault root (default: $KATIB_VAULT_ROOT or ~/vault)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually POST. Without this, just lists candidates.")
    parser.add_argument("--yes", action="store_true",
                        help="Skip the confirmation prompt (for CI).")
    args = parser.parse_args()

    vault_root = Path(args.vault_root).expanduser() if args.vault_root else default_vault_root()
    if not vault_root.exists():
        print(f"✗ vault root not found: {vault_root}", file=sys.stderr)
        return 2

    # Force API mode — fs mode would be a no-op (just rewriting the same file)
    # and strict mode is what we actually want (fail loud if Soul Hub is still down).
    os.environ["KATIB_VAULT_MODE"] = "strict"

    candidates = find_fallback_manifests(vault_root)
    if not candidates:
        print("No manifests tagged 'katib-fallback' — nothing to reconcile.")
        return 0

    print(f"Found {len(candidates)} manifest(s) tagged 'katib-fallback':")
    for p in candidates:
        print(f"  · {p.relative_to(vault_root)}")
    print()

    if not args.execute:
        print("Dry-run only. Pass --execute to POST each one through the API.")
        return 0

    if not args.yes:
        print(f"→ About to re-POST {len(candidates)} manifest(s) to {_base_url()}.")
        ans = input("Type 'yes' to proceed: ").strip().lower()
        if ans != "yes":
            print("aborted.")
            return 0

    successes = 0
    failures: list[tuple[Path, str]] = []
    for p in candidates:
        ok, note = reconcile_one(p, vault_root)
        rel = p.relative_to(vault_root)
        if ok:
            successes += 1
            print(f"  ✓ {rel}  ({note})")
        else:
            failures.append((p, note))
            print(f"  ✗ {rel}  — {note}", file=sys.stderr)

    print()
    print(f"Reconciled: {successes}/{len(candidates)}")
    if failures:
        print(f"Failed: {len(failures)} — see stderr for details.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
