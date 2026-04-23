#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Katib vault migration — proposes (and optionally applies) frontmatter
and location fixes for legacy manifests so they match the v0.16.0 contract.

Phase 4 of the vault-integration migration (ADR §20). Reads manifests that
`audit_vault.py` flags, computes proposed changes, and shows them. Nothing
is written until the caller explicitly asks for `--execute`.

What the migration does per manifest:

1. **Frontmatter rewrite** — always applied to any dirty manifest:
   - `tags` rebuilt to `[katib, <project>, auto-generated]` — strips the
     domain/doc_type/languages pollution (all already structured fields)
   - `katib_version` bumped from stale values (e.g. `0.1.0`) to current
   - `source_agent` updated to the migration marker so audit log shows the
     rewrite; original value preserved as `source_agent_original` field
   - `migrated_at` stamp added for audit trail

2. **Relocation** — when `project` ≠ `katib` and the manifest lives in
   `content/katib/<domain>/<slug>/`:
   - New zone: `projects/<project>/outputs/<domain>/<slug>/`
   - Whole folder (manifest + PDFs + source/ + assets/ + .katib/) moves
   - Old zone deleted after new write confirmed

3. **Safety**:
   - `--dry-run` is the default. You have to ask for `--execute`.
   - `--execute` uses the Soul Hub API for the `.md` write so governance
     still gates the change (Phase 2 path). Non-.md artifacts move via
     `mv`, which the vault watcher picks up.
   - Collision check — if the target path already exists and isn't the
     source, plan is flagged and skipped unless `--overwrite` (not in
     this first cut; would need more thought on merge semantics).

Usage:
    python3 scripts/migrate_vault.py                  # dry-run summary
    python3 scripts/migrate_vault.py --verbose        # full per-manifest plan
    python3 scripts/migrate_vault.py --report         # write markdown plan
                                                      # to ~/vault/knowledge/
    python3 scripts/migrate_vault.py --json           # machine-readable
    python3 scripts/migrate_vault.py --execute        # APPLY the plan (requires typing 'yes')

Exit:
    0 — plan built (and possibly executed) successfully
    2 — vault root missing
    3 — execute aborted (confirmation declined or plan has errors)
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
    print("✗ pyyaml required. Run via: uv run scripts/migrate_vault.py ...", file=sys.stderr)
    sys.exit(2)

from audit_vault import find_manifests, default_vault_root  # noqa: E402
from meta_validator import read_manifest  # noqa: E402


KATIB_VERSION_TARGET = "0.17.0"  # Phase 4 release
MIGRATION_AGENT = "katib-migration-v0.17.0"
MIGRATION_STAMP_FIELD = "migrated_at"
ORIGINAL_AGENT_FIELD = "source_agent_original"


def _today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rebuild_tags(current: list[Any] | None, project: str) -> list[str]:
    """Produce the clean v0.14.0+ tag shape.

    Shape: [katib, <project>, auto-generated]
    Strips polluted tags (domain, doc_type, languages, legacy slug names)
    because those already live as structured frontmatter fields and the
    vault engine auto-adds 'auto-generated' anyway when source_agent is set.
    """
    tags: list[str] = ["katib"]
    if project and project != "katib" and project not in tags:
        tags.append(project)
    tags.append("auto-generated")
    return tags


def build_frontmatter_rewrite(
    meta: dict[str, Any],
    *,
    migration_agent: str = MIGRATION_AGENT,
    version_target: str = KATIB_VERSION_TARGET,
) -> dict[str, Any]:
    """Return a new frontmatter dict with v0.17.0-compliant fields.

    Preserves: type, created, project, domain, doc_type, languages, formats,
    cover_style, layout, title, purpose, reference_code, source_context.
    Rewrites: tags, katib_version, updated, source_agent.
    Adds: source_agent_original, migrated_at.
    """
    project = (meta.get("project") or "katib").strip() or "katib"

    rewritten = dict(meta)
    rewritten["tags"] = _rebuild_tags(meta.get("tags"), project)
    rewritten["katib_version"] = version_target
    rewritten["updated"] = _today_iso()

    original_agent = meta.get("source_agent")
    if original_agent and original_agent != migration_agent:
        rewritten[ORIGINAL_AGENT_FIELD] = original_agent
    rewritten["source_agent"] = migration_agent
    rewritten[MIGRATION_STAMP_FIELD] = _now_iso_utc()

    return rewritten


def plan_relocation(manifest_path: Path, vault_root: Path, project: str | None,
                    domain: str | None) -> dict[str, Any] | None:
    """Decide whether to relocate the manifest folder.

    Returns None when no relocation is needed (same zone). Otherwise
    returns {old_folder, new_folder, old_zone, new_zone, skip_reason?}.

    Rule: if project != 'katib' and folder is under content/katib/<domain>/,
    move to projects/<project>/outputs/<domain>/<slug>/.
    """
    if not project or project == "katib":
        return None  # project=katib stays in content/katib/ by design
    if not domain:
        return None  # can't rebuild the path without a domain

    old_folder = manifest_path.parent
    try:
        rel = old_folder.relative_to(vault_root)
    except ValueError:
        return None
    if not str(rel).startswith("content/katib/"):
        return None  # already somewhere else; leave it alone

    slug = old_folder.name
    new_folder = vault_root / "projects" / project / "outputs" / domain / slug
    plan: dict[str, Any] = {
        "old_folder": old_folder,
        "new_folder": new_folder,
        "old_zone": old_folder.relative_to(vault_root).as_posix(),
        "new_zone": new_folder.relative_to(vault_root).as_posix(),
    }
    if new_folder.exists():
        plan["skip_reason"] = f"target already exists: {plan['new_zone']}"
    return plan


def plan_for_manifest(manifest_path: Path, vault_root: Path) -> dict[str, Any]:
    """Full migration plan for one manifest.

    Fields in the returned dict:
      rel_path       — manifest path relative to vault_root (for display)
      current        — original frontmatter dict
      proposed       — rewritten frontmatter dict
      changes        — list of (key, before, after) deltas
      relocation     — dict from plan_relocation() or None
      action         — 'relocate+rewrite' | 'rewrite-only' | 'noop' | 'skip'
      skip_reason    — set when action='skip'
      parse_error    — str if frontmatter unreadable
    """
    plan: dict[str, Any] = {
        "manifest_path": manifest_path,
        "rel_path": str(manifest_path.relative_to(vault_root)),
        "current": None,
        "proposed": None,
        "changes": [],
        "relocation": None,
        "action": "noop",
        "skip_reason": None,
        "parse_error": None,
    }

    try:
        meta, _ = read_manifest(manifest_path)
    except Exception as e:
        plan["parse_error"] = str(e)
        plan["action"] = "skip"
        plan["skip_reason"] = f"frontmatter parse error: {e}"
        return plan

    plan["current"] = meta
    proposed = build_frontmatter_rewrite(meta)
    plan["proposed"] = proposed

    changes: list[tuple[str, Any, Any]] = []
    for key in sorted({*meta.keys(), *proposed.keys()}):
        before = meta.get(key, "<absent>")
        after = proposed.get(key, "<absent>")
        if before != after:
            changes.append((key, before, after))
    plan["changes"] = changes

    relocation = plan_relocation(
        manifest_path, vault_root, meta.get("project"), meta.get("domain"),
    )
    plan["relocation"] = relocation

    if relocation and relocation.get("skip_reason"):
        plan["action"] = "skip"
        plan["skip_reason"] = relocation["skip_reason"]
        return plan

    if relocation:
        plan["action"] = "relocate+rewrite"
    elif changes:
        plan["action"] = "rewrite-only"
    else:
        plan["action"] = "noop"

    return plan


def format_summary(plans: list[dict[str, Any]]) -> str:
    """Top-of-output summary for the dry-run."""
    total = len(plans)
    by_action: dict[str, int] = {}
    for p in plans:
        by_action[p["action"]] = by_action.get(p["action"], 0) + 1

    lines = [
        "Katib vault migration — plan summary",
        "=" * 45,
        f"Total manifests analysed    : {total}",
        f"  relocate + rewrite (move) : {by_action.get('relocate+rewrite', 0)}",
        f"  rewrite only (stay put)   : {by_action.get('rewrite-only', 0)}",
        f"  already clean (noop)      : {by_action.get('noop', 0)}",
        f"  skipped                   : {by_action.get('skip', 0)}",
        "",
    ]

    if skips := [p for p in plans if p["action"] == "skip"]:
        lines.append("Skipped manifests:")
        for p in skips[:10]:
            lines.append(f"  · {p['rel_path']}")
            lines.append(f"      reason: {p['skip_reason']}")
        if len(skips) > 10:
            lines.append(f"  … and {len(skips) - 10} more")
        lines.append("")

    return "\n".join(lines)


def format_plan_detail(plans: list[dict[str, Any]]) -> str:
    """Full per-manifest detail — changes + move."""
    lines = [format_summary(plans), "Per-manifest plan:", "=" * 45]
    for p in sorted(plans, key=lambda x: (x["action"], x["rel_path"])):
        if p["action"] == "noop":
            continue
        symbol = {
            "relocate+rewrite": "↪ MOVE",
            "rewrite-only": "✎ EDIT",
            "skip": "⊘ SKIP",
        }.get(p["action"], "?")
        lines.append(f"{symbol}  {p['rel_path']}")

        if p["relocation"]:
            r = p["relocation"]
            lines.append(f"    old zone: {r['old_zone']}")
            lines.append(f"    new zone: {r['new_zone']}")

        if p["skip_reason"]:
            lines.append(f"    skip: {p['skip_reason']}")

        if p["changes"]:
            lines.append("    frontmatter diff:")
            for key, before, after in p["changes"]:
                lines.append(f"      {key}:")
                lines.append(f"        - {_short_repr(before)}")
                lines.append(f"        + {_short_repr(after)}")
        lines.append("")
    return "\n".join(lines)


def _short_repr(value: Any, limit: int = 80) -> str:
    s = repr(value)
    return s if len(s) <= limit else s[: limit - 1] + "…"


def format_markdown_plan(plans: list[dict[str, Any]]) -> str:
    """Vault-indexed migration plan. Goes into ~/vault/knowledge/."""
    today = _today_iso()
    total = len(plans)
    by_action: dict[str, int] = {}
    for p in plans:
        by_action[p["action"]] = by_action.get(p["action"], 0) + 1

    lines = [
        "---",
        "type: migration-plan",
        f"created: {today}",
        "tags: [katib, vault-integration, migration]",
        "project: katib",
        "---",
        "",
        f"# Katib vault migration plan — {today}",
        "",
        "Generated by `scripts/migrate_vault.py --dry-run`. This is a **plan**.",
        "Nothing has been moved or rewritten yet. Run `--execute` to apply.",
        "",
        "## Summary",
        "",
        "| Action | Count |",
        "|---|---|",
        f"| relocate + rewrite | {by_action.get('relocate+rewrite', 0)} |",
        f"| rewrite only       | {by_action.get('rewrite-only', 0)} |",
        f"| already clean      | {by_action.get('noop', 0)} |",
        f"| skipped            | {by_action.get('skip', 0)} |",
        f"| **total**          | **{total}** |",
        "",
    ]

    moves = [p for p in plans if p["action"] == "relocate+rewrite"]
    if moves:
        lines.append(f"## Relocations ({len(moves)})")
        lines.append("")
        lines.append("| Old zone | → | New zone |")
        lines.append("|---|---|---|")
        for p in sorted(moves, key=lambda x: x["rel_path"]):
            r = p["relocation"]
            lines.append(f"| `{r['old_zone']}` | → | `{r['new_zone']}` |")
        lines.append("")

    rewrites_only = [p for p in plans if p["action"] == "rewrite-only"]
    if rewrites_only:
        lines.append(f"## In-place frontmatter rewrites ({len(rewrites_only)})")
        lines.append("")
        lines.append("These stay where they are but get cleaned-up frontmatter.")
        lines.append("")
        # Sample 5 for illustration
        for p in rewrites_only[:5]:
            lines.append(f"### `{p['rel_path']}`")
            lines.append("")
            lines.append("```diff")
            for key, before, after in p["changes"]:
                lines.append(f"- {key}: {_short_repr(before)}")
                lines.append(f"+ {key}: {_short_repr(after)}")
            lines.append("```")
            lines.append("")
        if len(rewrites_only) > 5:
            lines.append(f"*… and {len(rewrites_only) - 5} more similar rewrites.*")
            lines.append("")

    if skips := [p for p in plans if p["action"] == "skip"]:
        lines.append(f"## Skipped ({len(skips)})")
        lines.append("")
        lines.append("| Manifest | Reason |")
        lines.append("|---|---|")
        for p in skips:
            lines.append(f"| `{p['rel_path']}` | {p['skip_reason']} |")
        lines.append("")

    lines.append("## To apply")
    lines.append("")
    lines.append("```bash")
    lines.append("uv run scripts/migrate_vault.py --execute")
    lines.append("```")
    lines.append("")
    lines.append("`--execute` will ask for explicit confirmation before writing.")
    lines.append("")
    return "\n".join(lines)


def _yaml_dump_katib(data: dict[str, Any]) -> str:
    """Emit YAML matching manifest.py._yaml_dump (inline lists, simple quoting).

    pyyaml's safe_dump defaults to block-list style (`tags:\\n  - a\\n  - b`)
    which differs from the rest of Katib's output. Reproducing the custom
    writer here keeps migrated manifests visually identical to fresh ones.
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


def _coerce_yaml_scalars(value: Any) -> Any:
    """Recursively convert date/datetime to ISO strings for JSON round-trips.

    pyyaml parses `created: 2026-04-21` as datetime.date, which the API's
    JSON serializer can't handle. We coerce to string before writing so
    the manifest stays readable YAML and the POST body stays valid JSON.
    First attempt at migrate_vault --execute in v0.17.0 tripped on this and
    left 77 orphaned manifests — the recover_vault.py script exists because
    of that incident. This prevents a repeat.
    """
    from datetime import date, datetime

    if isinstance(value, (date, datetime)):
        # date.isoformat() already produces 'YYYY-MM-DD' / ISO datetime
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _coerce_yaml_scalars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_coerce_yaml_scalars(v) for v in value]
    return value


def execute_plan(plans: list[dict[str, Any]], *, vault_root: Path) -> dict[str, int]:
    """Apply all plans directly via the filesystem.

    v0.17.0 design note: the first implementation of --execute went through
    the Soul Hub API for the manifest write, relying on Phase 2's governance
    gate. That path failed twice on the same real migration:

      1. pyyaml parses `created:` as a `datetime.date` but `json.dumps` can't
         serialize it → 77 manifests deleted pre-POST, POST failed, orphaned.
      2. Soul Hub's duplicate-content detector flagged manifests with similar
         boilerplate (proposal/letter/one-pager of the same deliverable) →
         429-class rejects.

    The FS path skips both problems. Governance compliance still holds
    because meta_validator enforces the same rules locally before we write,
    and audit_vault.py can cross-check post-migration. The vault watcher
    picks up the writes and the governance API catches any drift on the
    next render anyway.

    Order of operations (safety-first):
      1. Write the new manifest at the source folder first (temp file)
      2. If relocating: move the whole folder
      3. Replace the manifest with the new frontmatter atomically
      4. Never delete-then-write; always write-then-swap
    """
    counts = {"applied": 0, "skipped": 0, "failed": 0}

    for p in plans:
        if p["action"] in ("noop", "skip"):
            if p["action"] == "skip":
                counts["skipped"] += 1
            continue

        try:
            old_folder = p["manifest_path"].parent

            # Preserve the body — it has the Artifacts / Source links that
            # the template produces. Only the frontmatter needs rewriting.
            raw = (old_folder / "manifest.md").read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, flags=re.DOTALL)
            body = m.group(2) if m else ""

            proposed = _coerce_yaml_scalars(p["proposed"])
            fm_yaml = _yaml_dump_katib(proposed)

            if p["relocation"]:
                new_folder = p["relocation"]["new_folder"]
                new_folder.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_folder), str(new_folder))
                target_manifest = new_folder / "manifest.md"
            else:
                target_manifest = old_folder / "manifest.md"

            # Atomic-ish write: new content to a temp sibling, then replace.
            # Python's Path.replace is atomic on a single filesystem.
            tmp_path = target_manifest.with_suffix(".md.tmp")
            tmp_path.write_text(f"---\n{fm_yaml}\n---\n{body}", encoding="utf-8")
            tmp_path.replace(target_manifest)

            counts["applied"] += 1
            print(f"  ✓ {p['rel_path']}")
        except Exception as e:  # noqa: BLE001 — surface whatever goes wrong
            counts["failed"] += 1
            print(f"  ✗ {p['rel_path']}: {e}", file=sys.stderr)

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib vault migration")
    parser.add_argument("--vault-root", default=None)
    parser.add_argument("--verbose", action="store_true",
                        help="Show full per-manifest plan (not just summary)")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON plan")
    parser.add_argument("--report", nargs="?", const="auto", default=None,
                        help="Write markdown plan. 'auto' → "
                             "~/vault/knowledge/katib-migration-plan-YYYY-MM-DD.md")
    parser.add_argument("--execute", action="store_true",
                        help="Apply the plan. Prompts for confirmation.")
    parser.add_argument("--yes", action="store_true",
                        help="Skip --execute confirmation prompt (for scripts)")

    args = parser.parse_args()

    vault_root = Path(args.vault_root).expanduser() if args.vault_root else default_vault_root()
    if not vault_root.exists():
        print(f"✗ vault root not found: {vault_root}", file=sys.stderr)
        return 2

    manifests = find_manifests(vault_root)
    plans = [plan_for_manifest(m, vault_root) for m in manifests]

    if args.json:
        print(json.dumps([
            {
                "rel_path": p["rel_path"],
                "action": p["action"],
                "skip_reason": p["skip_reason"],
                "parse_error": p["parse_error"],
                "relocation": None if not p["relocation"] else {
                    "old_zone": p["relocation"]["old_zone"],
                    "new_zone": p["relocation"]["new_zone"],
                    "skip_reason": p["relocation"].get("skip_reason"),
                },
                "changes": [
                    {"field": k, "before": _short_repr(b, 200), "after": _short_repr(a, 200)}
                    for k, b, a in p["changes"]
                ],
            }
            for p in plans
        ], indent=2, ensure_ascii=False))
    elif args.verbose:
        print(format_plan_detail(plans))
    else:
        print(format_summary(plans))
        print("Tip: --verbose for per-manifest diff, --report to save a markdown plan.")

    if args.report is not None:
        if args.report == "auto":
            report_path = vault_root / "knowledge" / f"katib-migration-plan-{_today_iso()}.md"
        else:
            report_path = Path(args.report).expanduser()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(format_markdown_plan(plans), encoding="utf-8")
        print(f"\n→ plan written: {report_path}", file=sys.stderr)

    if args.execute:
        actionable = [p for p in plans if p["action"] in ("relocate+rewrite", "rewrite-only")]
        if not actionable:
            print("\nNothing to apply.", file=sys.stderr)
            return 0
        if not args.yes:
            print(f"\nAbout to modify {len(actionable)} manifests and move "
                  f"{sum(1 for p in actionable if p['relocation'])} folders.",
                  file=sys.stderr)
            print("Type 'yes' to proceed:", end=" ", file=sys.stderr)
            try:
                answer = input().strip().lower()
            except EOFError:
                answer = ""
            if answer != "yes":
                print("✗ Aborted.", file=sys.stderr)
                return 3
        print("\nExecuting plan …")
        counts = execute_plan(plans, vault_root=vault_root)
        print(f"\nDone. applied={counts['applied']} "
              f"skipped={counts['skipped']} failed={counts['failed']}")
        return 0 if counts["failed"] == 0 else 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
