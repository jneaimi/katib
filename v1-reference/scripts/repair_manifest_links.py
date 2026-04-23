#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Repair stale paths left behind by pre-v0.18.2 renders.

Two bugs that escaped Phase 4's migration:

1. `manifest.py` hardcoded `~/vault/content/katib/<domain>/<slug>/` in the
   `## Re-render` section of every manifest body, regardless of whether
   the folder actually lived there. Every --project=<other> render + every
   Phase-4 relocated folder got a rebuild command pointing at a path that
   doesn't exist.

2. `content/index.md` (Katib's build-log index) appended bullets that
   referenced `content/katib/...` paths. When Phase 4 relocated folders
   to `projects/<slug>/outputs/...`, the bullets were left pointing at
   the old location — broken wikilinks in Obsidian.

This script walks every katib manifest, computes the correct rebuild
path from the folder's actual location, and rewrites the body if it
doesn't match. It also sweeps `content/index.md` for broken
`[[content/katib/.../manifest]]` wikilinks and repoints them to wherever
the folder landed.

Usage:
    python3 scripts/repair_manifest_links.py                   # dry-run
    python3 scripts/repair_manifest_links.py --execute         # apply
    python3 scripts/repair_manifest_links.py --execute --yes   # skip prompt

Exit:
  0 — nothing to repair OR all repairs succeeded
  1 — at least one write failed
  2 — vault root missing
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from audit_vault import find_manifests, default_vault_root  # noqa: E402


_REBUILD_BLOCK_RE = re.compile(
    r"(## Re-render\s*\n+```bash\s*\n/katib rebuild )([^\n]+?)(/?\s*\n```)",
    re.MULTILINE,
)

_WIKILINK_RE = re.compile(r"\[\[(content/katib/([^/\]|]+)/([^/\]|]+)/manifest)(\|[^\]]*)?\]\]")


def compute_correct_rebuild(folder: Path) -> str:
    """`~/vault/...` form when under $HOME, else absolute path."""
    home = Path.home()
    try:
        return "~/" + str(folder.relative_to(home))
    except ValueError:
        return str(folder)


def repair_manifest_body(manifest_path: Path) -> tuple[bool, str | None]:
    """Rewrite the rebuild path if it's wrong. Returns (changed, new_path or None)."""
    raw = manifest_path.read_text(encoding="utf-8")
    m = _REBUILD_BLOCK_RE.search(raw)
    if not m:
        return False, None  # no rebuild block — nothing to fix

    current_path = m.group(2).strip().rstrip("/")
    correct_path = compute_correct_rebuild(manifest_path.parent)
    if current_path == correct_path:
        return False, None

    # Preserve trailing slash iff original had one
    trailing_slash = "/" if m.group(3).startswith("/") else ""
    new_block = f"{m.group(1)}{correct_path}{trailing_slash}\n```"
    new_raw = _REBUILD_BLOCK_RE.sub(lambda _: new_block, raw, count=1)

    # Atomic temp-file-then-replace — the pattern migrate_vault.py locked in
    tmp = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    tmp.write_text(new_raw, encoding="utf-8")
    tmp.replace(manifest_path)
    return True, correct_path


def find_relocated_target(slug_dated: str, vault_root: Path) -> Path | None:
    """Given '2026-04-22-foo', find where that folder actually lives now.

    Walks content/katib/<domain>/<slug_dated>/ and projects/*/outputs/<domain>/<slug_dated>/.
    Returns the first match with a manifest.md, else None.
    """
    # Try content/katib first (the legacy zone still lives for project=katib)
    ck = vault_root / "content" / "katib"
    if ck.exists():
        for candidate in ck.rglob(slug_dated):
            if (candidate / "manifest.md").exists():
                return candidate

    projects = vault_root / "projects"
    if projects.exists():
        for proj in projects.iterdir():
            outputs = proj / "outputs"
            if not outputs.exists():
                continue
            for candidate in outputs.rglob(slug_dated):
                if (candidate / "manifest.md").exists():
                    return candidate
    return None


def repair_index_wikilinks(vault_root: Path) -> tuple[int, int]:
    """Find broken `[[content/katib/<domain>/<slug>/manifest]]` links in
    content/index.md and repoint them to wherever the folder landed.

    Returns (fixed, still_broken).
    """
    index_path = vault_root / "content" / "index.md"
    if not index_path.exists():
        return 0, 0

    raw = index_path.read_text(encoding="utf-8")
    fixed = 0
    still_broken = 0

    def _repointer(match: "re.Match[str]") -> str:
        nonlocal fixed, still_broken
        old_target = match.group(1)  # "content/katib/tutorial/2026-04-22-foo/manifest"
        alias = match.group(4) or ""
        # Check if the old target actually exists
        old_file = vault_root / (old_target + ".md")
        if old_file.exists():
            return match.group(0)  # still valid, leave alone

        slug_dated = match.group(3)
        relocated = find_relocated_target(slug_dated, vault_root)
        if relocated is None:
            still_broken += 1
            return match.group(0)  # can't find where it went — leave for human review

        new_target = str(relocated.relative_to(vault_root)) + "/manifest"
        fixed += 1
        return f"[[{new_target}{alias}]]"

    new_raw = _WIKILINK_RE.sub(_repointer, raw)

    if new_raw != raw:
        tmp = index_path.with_suffix(".md.tmp")
        tmp.write_text(new_raw, encoding="utf-8")
        tmp.replace(index_path)

    return fixed, still_broken


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair stale rebuild paths + broken index wikilinks")
    parser.add_argument("--vault-root", default=None,
                        help="Vault root (default: $KATIB_VAULT_ROOT or ~/vault)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually write. Without this, just lists candidates.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")
    args = parser.parse_args()

    vault_root = Path(args.vault_root).expanduser() if args.vault_root else default_vault_root()
    if not vault_root.exists():
        print(f"✗ vault root not found: {vault_root}", file=sys.stderr)
        return 2

    manifests = find_manifests(vault_root)

    # === Pass 1 (dry-run): find manifests whose rebuild path is stale ===
    stale = []
    for m in manifests:
        raw = m.read_text(encoding="utf-8")
        block = _REBUILD_BLOCK_RE.search(raw)
        if not block:
            continue
        current = block.group(2).strip().rstrip("/")
        correct = compute_correct_rebuild(m.parent)
        if current != correct:
            stale.append((m, current, correct))

    # === Pass 2: count broken wikilinks in content/index.md ===
    index_path = vault_root / "content" / "index.md"
    broken_links = 0
    if index_path.exists():
        raw = index_path.read_text(encoding="utf-8")
        for link_m in _WIKILINK_RE.finditer(raw):
            old_file = vault_root / (link_m.group(1) + ".md")
            if not old_file.exists():
                broken_links += 1

    print(f"Found {len(stale)} manifest(s) with stale rebuild paths.")
    print(f"Found {broken_links} broken wikilink(s) in content/index.md.")

    if stale:
        print("\nSample rebuild path corrections:")
        for path, cur, correct in stale[:5]:
            print(f"  · {path.relative_to(vault_root)}")
            print(f"      was: {cur}")
            print(f"      new: {correct}")
        if len(stale) > 5:
            print(f"  … and {len(stale) - 5} more")

    if not stale and broken_links == 0:
        print("\nNothing to repair.")
        return 0

    if not args.execute:
        print("\nDry-run only. Pass --execute to write changes.")
        return 0

    if not args.yes:
        total = len(stale) + (1 if broken_links else 0)
        print(f"\n→ About to rewrite {len(stale)} manifest(s)"
              f"{' + content/index.md' if broken_links else ''}.")
        ans = input("Type 'yes' to proceed: ").strip().lower()
        if ans != "yes":
            print("aborted.")
            return 0

    # === Apply: manifest bodies ===
    manifest_failures = []
    for path, _, _ in stale:
        try:
            changed, new_path = repair_manifest_body(path)
            if changed:
                print(f"  ✓ {path.relative_to(vault_root)}  → {new_path}/")
        except Exception as e:
            manifest_failures.append((path, str(e)))
            print(f"  ✗ {path.relative_to(vault_root)}: {e}", file=sys.stderr)

    # === Apply: index wikilinks ===
    if broken_links:
        fixed, unresolved = repair_index_wikilinks(vault_root)
        print(f"\nindex.md: {fixed} wikilink(s) repointed, {unresolved} still unresolved")

    print()
    print(f"Repaired: {len(stale) - len(manifest_failures)}/{len(stale)} manifest(s)")
    if manifest_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
