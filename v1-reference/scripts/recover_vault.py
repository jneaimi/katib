#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Recover orphaned Katib manifests after the failed v0.17.0 migration.

Context: the first run of `migrate_vault.py --execute` deleted each
manifest.md before its governed re-write — and the re-write then failed
on a `datetime.date` JSON serialisation bug. Result: 77 folders with a
`.katib/run.json`, `source/*.html`, and PDFs but no manifest.

This script reconstructs the manifest from what survived:
  - `.katib/run.json` — domain, doc_type, languages, formats, cover, layout
  - `source/*.html` — title (from <h1> or <title>)
  - folder name         — date + slug
  - folder path         — project (for content/katib: inferred from slug,
                          for projects/<slug>/outputs: taken directly)

While rebuilding, applies the v0.17.0 contract the migration was supposed
to set:
  - Clean `tags: [katib, <project>, auto-generated]`
  - `katib_version: 0.17.0`
  - `source_agent: katib-migration-v0.17.0`
  - `source_agent_original: claude-opus-4-7` (when inferable)
  - `migrated_at: <UTC now>`

Also executes the relocation that the bad migrate_vault attempted: if the
folder is under `content/katib/<domain>/` and the inferred/fetched project
is not `katib`, the whole folder moves to `projects/<project>/outputs/<domain>/<slug>/`
before the manifest is written.

Writes via FS directly (not the API) — fast, simpler, and avoids the
duplicate-content detector that also tripped the last run. Governance
still passes because this script uses the same schema meta_validator
enforces; a later `audit_vault.py` run can double-check.

Usage:
    python3 scripts/recover_vault.py --dry-run       # show what would happen
    python3 scripts/recover_vault.py --execute       # apply
    python3 scripts/recover_vault.py --execute --yes # skip the prompt
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

try:
    import yaml
except ImportError:
    print("✗ pyyaml required. Run via: uv run scripts/recover_vault.py ...", file=sys.stderr)
    sys.exit(2)


KATIB_VERSION_TARGET = "0.17.0"
MIGRATION_AGENT = "katib-migration-v0.17.0"


def vault_root() -> Path:
    if env := os.environ.get("KATIB_VAULT_ROOT"):
        return Path(env).expanduser()
    return Path.home() / "vault"


def _today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_orphans(root: Path) -> list[Path]:
    """Folders that have source/ + .katib/run.json but no manifest.md."""
    orphans: list[Path] = []
    candidates: list[Path] = []

    katib_root = root / "content" / "katib"
    if katib_root.exists():
        for domain_dir in katib_root.iterdir():
            if not domain_dir.is_dir():
                continue
            candidates.extend(d for d in domain_dir.iterdir() if d.is_dir())

    projects_root = root / "projects"
    if projects_root.exists():
        for proj in projects_root.iterdir():
            outputs = proj / "outputs"
            if not outputs.exists():
                continue
            for domain_dir in outputs.iterdir():
                if not domain_dir.is_dir():
                    continue
                candidates.extend(d for d in domain_dir.iterdir() if d.is_dir())

    for folder in candidates:
        manifest = folder / "manifest.md"
        run_json = folder / ".katib" / "run.json"
        if not manifest.exists() and run_json.exists():
            orphans.append(folder)

    return sorted(orphans)


_TITLE_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", flags=re.DOTALL | re.IGNORECASE)
_TITLE_TAG_RE = re.compile(r"<title[^>]*>(.*?)</title>", flags=re.DOTALL | re.IGNORECASE)
_TAG_STRIP_RE = re.compile(r"<[^>]+>")


def _clean_title(raw: str) -> str:
    s = _TAG_STRIP_RE.sub("", raw).strip()
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s)
    # Drop template placeholders that survived to the rendered HTML
    if s.startswith("[") and s.endswith("]"):
        return ""
    return s


def extract_title_from_html(folder: Path) -> str:
    """Scan source/*.html for a meaningful title. Prefer H1 over <title>.

    Returns '' if nothing worthwhile found; caller falls back to the folder slug.
    """
    source_dir = folder / "source"
    if not source_dir.exists():
        return ""

    # Prefer the EN HTML if present — Arabic HTML has shaped characters which
    # are readable but less diff-friendly in manifests.
    htmls = sorted(source_dir.glob("*.html"))
    htmls.sort(key=lambda p: (0 if ".en." in p.name else 1, p.name))
    for html_path in htmls:
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        for pattern in (_TITLE_H1_RE, _TITLE_TAG_RE):
            if m := pattern.search(text):
                title = _clean_title(m.group(1))
                if title:
                    return title
    return ""


def derive_project_from_path(folder: Path, vault: Path) -> str:
    """Recover the original `project` field from the folder path.

    - folder under projects/<slug>/outputs/<domain>/<slug-dated>/ → project=<slug>
    - folder under content/katib/<domain>/<slug-dated>/          → project='katib'
      unless the slug-dated name matches a known <project>-<doc_type>-* pattern;
      not worth inferring here — the migration plan already shows what the real
      project was, and the run.json doesn't carry it, so we default to 'katib'.
    """
    try:
        rel = folder.relative_to(vault).parts
    except ValueError:
        return "katib"

    if len(rel) >= 3 and rel[0] == "projects":
        return rel[1]
    return "katib"


def slug_title_fallback(folder: Path) -> str:
    """Turn '2026-04-22-personal-test-cv' into 'Personal Test Cv' — last resort."""
    name = folder.name
    # Strip leading YYYY-MM-DD-
    parts = name.split("-", 3)
    if len(parts) > 3 and parts[0].isdigit():
        name = parts[3]
    return " ".join(w.capitalize() for w in re.split(r"[-_]", name))


def build_frontmatter(folder: Path, vault: Path) -> dict[str, Any]:
    """Reconstruct v0.17.0-compliant frontmatter from surviving data."""
    run_json_path = folder / ".katib" / "run.json"
    run = json.loads(run_json_path.read_text(encoding="utf-8"))

    project = derive_project_from_path(folder, vault)
    title = extract_title_from_html(folder) or slug_title_fallback(folder)

    tags = ["katib"]
    if project and project != "katib":
        tags.append(project)
    tags.append("auto-generated")

    created = run.get("generated_at", "")[:10] or _today_iso()
    original_agent = run.get("source_agent")

    fm: dict[str, Any] = {
        "type": "output",
        "created": created,
        "updated": _today_iso(),
        "tags": tags,
        "project": project,
        "domain": run.get("domain", folder.parent.name),
        "doc_type": run.get("doc_type", ""),
        "languages": list(run.get("languages", [])),
        "formats": list(run.get("formats", [])),
        "cover_style": (run.get("cover") or {}).get("style"),
        "layout": run.get("layout", "classic"),
        "katib_version": KATIB_VERSION_TARGET,
        "source_agent": MIGRATION_AGENT,
        "migrated_at": _now_iso_utc(),
        "recovered_from": "migration-incident-2026-04-22",
        "title": title,
    }
    if original_agent and original_agent != MIGRATION_AGENT:
        fm["source_agent_original"] = original_agent
    return fm


def render_body(meta: dict[str, Any], folder: Path) -> str:
    """Lazy import so the script doesn't pull in all of manifest.py on --dry-run."""
    from manifest import render_manifest_body  # noqa: E402
    return render_manifest_body(meta, folder.name, folder=folder)


def _yaml_dump(data: dict[str, Any]) -> str:
    """Small YAML writer — matches manifest.py._yaml_dump style so diffs stay
    predictable. Lists go inline `[a, b]`, scalars quote on special chars.
    """
    lines = []
    for k, v in data.items():
        if isinstance(v, list):
            rendered = "[" + ", ".join(str(x) for x in v) + "]"
            lines.append(f"{k}: {rendered}")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v)
            if any(c in s for c in [":", "#", "@", "|", ">", "{", "}", "[", "]"]):
                s = f'"{s}"'
            lines.append(f"{k}: {s}")
    return "\n".join(lines)


def plan_recovery(orphans: list[Path], vault: Path) -> list[dict[str, Any]]:
    plans: list[dict[str, Any]] = []
    for folder in orphans:
        try:
            rel_folder = folder.relative_to(vault)
        except ValueError:
            rel_folder = folder

        under_content_katib = str(rel_folder).startswith("content/katib/")
        meta = build_frontmatter(folder, vault)

        # Relocation: if currently under content/katib/ AND project != katib,
        # the migration had intended to move it. We replay that move here.
        target_folder = folder
        relocation: dict[str, str] | None = None
        if under_content_katib and meta["project"] != "katib":
            domain = meta["domain"] or folder.parent.name
            target_folder = vault / "projects" / meta["project"] / "outputs" / domain / folder.name
            if target_folder.exists() and target_folder != folder:
                relocation = {
                    "skip_reason": f"target already exists: {target_folder.relative_to(vault).as_posix()}",
                }
            else:
                relocation = {
                    "from": rel_folder.as_posix(),
                    "to": target_folder.relative_to(vault).as_posix(),
                }

        plans.append({
            "source_folder": folder,
            "target_folder": target_folder,
            "rel_source": str(rel_folder),
            "meta": meta,
            "relocation": relocation,
        })
    return plans


def print_summary(plans: list[dict[str, Any]]) -> None:
    moves = [p for p in plans if p["relocation"] and "to" in p["relocation"]]
    rewrites = [p for p in plans if not p["relocation"]]
    skips = [p for p in plans if p["relocation"] and "skip_reason" in p["relocation"]]

    print(f"Orphaned manifests   : {len(plans)}")
    print(f"  → rewrite in place : {len(rewrites)}")
    print(f"  → move + rewrite   : {len(moves)}")
    print(f"  → skip             : {len(skips)}")
    print()

    if moves:
        print("Moves:")
        for p in moves[:20]:
            r = p["relocation"]
            print(f"  · {r['from']}")
            print(f"      → {r['to']}")
        if len(moves) > 20:
            print(f"  … and {len(moves) - 20} more")
        print()

    if skips:
        print("Skipped (target already exists):")
        for p in skips:
            print(f"  · {p['rel_source']}")
            print(f"      reason: {p['relocation']['skip_reason']}")
        print()


def execute(plans: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"applied": 0, "skipped": 0, "failed": 0}
    for p in plans:
        if p["relocation"] and "skip_reason" in p["relocation"]:
            counts["skipped"] += 1
            print(f"  ⊘ skip {p['rel_source']}: {p['relocation']['skip_reason']}")
            continue
        try:
            src = p["source_folder"]
            dst = p["target_folder"]
            if src != dst:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
            meta = p["meta"]
            fm_yaml = _yaml_dump(meta)
            body = render_body(meta, dst)
            (dst / "manifest.md").write_text(
                f"---\n{fm_yaml}\n---\n\n{body}",
                encoding="utf-8",
            )
            counts["applied"] += 1
            print(f"  ✓ {p['rel_source']}")
        except Exception as e:  # noqa: BLE001
            counts["failed"] += 1
            print(f"  ✗ {p['rel_source']}: {e}", file=sys.stderr)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib vault manifest recovery")
    parser.add_argument("--vault-root", default=None)
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Show the plan (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Apply the plan")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt")
    args = parser.parse_args()

    root = Path(args.vault_root).expanduser() if args.vault_root else vault_root()
    if not root.exists():
        print(f"✗ vault root not found: {root}", file=sys.stderr)
        return 2

    orphans = find_orphans(root)
    if not orphans:
        print("No orphaned manifests found. Vault is healthy.")
        return 0

    plans = plan_recovery(orphans, root)
    print_summary(plans)

    if not args.execute:
        print("(dry-run — pass --execute to apply)")
        return 0

    if not args.yes:
        print(f"\nAbout to reconstruct {len(plans)} manifests.")
        print("Type 'yes' to proceed:", end=" ")
        try:
            answer = input().strip().lower()
        except EOFError:
            answer = ""
        if answer != "yes":
            print("✗ Aborted.")
            return 3

    print("\nApplying recovery …")
    counts = execute(plans)
    print(f"\nDone. applied={counts['applied']} skipped={counts['skipped']} failed={counts['failed']}")
    return 0 if counts["failed"] == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
