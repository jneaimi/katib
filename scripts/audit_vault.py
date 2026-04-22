#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Katib vault audit — walks every existing Katib manifest and reports
governance drift against the current schema + zone rules.

Phase 4 of the vault-integration migration (ADR §20). Purely read-only —
never modifies anything. Use `migrate_vault.py --dry-run` to see what
`migrate_vault.py --execute` would change, then `--execute` to actually
run the migration.

Usage:
    python3 scripts/audit_vault.py                       # summary to stdout
    python3 scripts/audit_vault.py --verbose             # every violation listed
    python3 scripts/audit_vault.py --json                # machine-readable
    python3 scripts/audit_vault.py --report              # write markdown report to
                                                         # ~/vault/knowledge/katib-audit-YYYY-MM-DD.md
    python3 scripts/audit_vault.py --vault-root /path    # override vault root

Exit code: 0 if any manifests were audited (success = ran to completion).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from meta_validator import validate, read_manifest, SchemaViolation  # noqa: E402


def default_vault_root() -> Path:
    """Vault root lookup: $KATIB_VAULT_ROOT env → ~/vault convention."""
    if env := os.environ.get("KATIB_VAULT_ROOT"):
        return Path(env).expanduser()
    return Path.home() / "vault"


def find_manifests(vault_root: Path) -> list[Path]:
    """Katib writes manifests in two places today:
      - content/katib/<domain>/<slug>/manifest.md  (legacy routing)
      - projects/<slug>/outputs/<domain>/<slug>/manifest.md  (Phase 2+ routing)
    """
    found: list[Path] = []
    katib_root = vault_root / "content" / "katib"
    if katib_root.exists():
        found.extend(katib_root.rglob("manifest.md"))
    projects_root = vault_root / "projects"
    if projects_root.exists():
        for proj in projects_root.iterdir():
            outputs = proj / "outputs"
            if outputs.exists():
                found.extend(outputs.rglob("manifest.md"))
    return sorted(found)


def audit_manifest(path: Path, vault_root: Path) -> dict:
    """Return a result record for one manifest.

    Keys:
      path        — absolute Path
      rel_path    — path relative to vault_root (string, forward slashes)
      zone        — manifest folder relative to vault_root
      project     — frontmatter `project` field (or None on parse failure)
      domain      — frontmatter `domain` (info for the migrate planner)
      doc_type    — frontmatter `doc_type`
      katib_version — frontmatter `katib_version` (often stale on legacy)
      source_agent  — frontmatter `source_agent`
      violations  — list[SchemaViolation]
      errors      — count of severity='error' violations
      warns       — count of severity='warn' violations
      parse_error — str if frontmatter couldn't be read, else None
    """
    try:
        rel = path.relative_to(vault_root)
    except ValueError:
        rel = path

    zone = path.parent.relative_to(vault_root).as_posix()

    base = {
        "path": path,
        "rel_path": str(rel),
        "zone": zone,
        "project": None,
        "domain": None,
        "doc_type": None,
        "katib_version": None,
        "source_agent": None,
        "violations": [],
        "errors": 0,
        "warns": 0,
        "parse_error": None,
    }

    try:
        meta, content_len = read_manifest(path)
    except Exception as e:  # broad on purpose — any parse failure is a finding
        base["parse_error"] = str(e)
        base["errors"] = 1
        return base

    base["project"] = meta.get("project")
    base["domain"] = meta.get("domain")
    base["doc_type"] = meta.get("doc_type")
    base["katib_version"] = meta.get("katib_version")
    base["source_agent"] = meta.get("source_agent")

    violations = validate(meta, zone=zone, content_length=content_len)
    base["violations"] = violations
    base["errors"] = sum(1 for v in violations if v.severity == "error")
    base["warns"] = sum(1 for v in violations if v.severity == "warn")
    return base


def _violation_message(v: SchemaViolation) -> str:
    """Friendly short string for one violation, severity-tagged."""
    sev = "ERROR" if v.severity == "error" else "warn"
    if v.field:
        return f"[{sev}] {v.field}: {v.message}"
    return f"[{sev}] {v.message}"


def format_text_summary(results: list[dict]) -> str:
    """Condensed stdout summary — counts + a few sample offenders."""
    total = len(results)
    if total == 0:
        return "No Katib manifests found."

    clean = sum(1 for r in results if not r["violations"] and not r["parse_error"])
    err_count = sum(1 for r in results if r["errors"])
    warn_only = sum(1 for r in results if not r["errors"] and r["warns"])

    lines = [
        "Katib vault audit — summary",
        "=" * 40,
        f"Total manifests scanned : {total}",
        f"Clean                   : {clean}",
        f"With error(s)           : {err_count}",
        f"Warning only            : {warn_only}",
        "",
    ]

    # Top error types
    error_counter: Counter[str] = Counter()
    for r in results:
        for v in r["violations"]:
            if v.severity == "error":
                # "tag pollution: 'domain' appears in tags" → bucket by prefix
                key = v.message.split(":", 1)[0] if ":" in v.message else v.message
                error_counter[key] += 1
    if error_counter:
        lines.append("Most common errors:")
        for msg, count in error_counter.most_common(10):
            lines.append(f"  {count:4d} · {msg}")
        lines.append("")

    # Project distribution
    proj_counter: Counter[str] = Counter(r["project"] or "<missing>" for r in results)
    lines.append("Manifest count by project:")
    for proj, count in proj_counter.most_common():
        lines.append(f"  {count:4d} · {proj}")
    lines.append("")

    # Manifests that want relocating (project != 'katib' but in content/katib)
    relocation_candidates = [
        r for r in results
        if r["project"] and r["project"] != "katib" and r["zone"].startswith("content/katib/")
    ]
    if relocation_candidates:
        lines.append(f"Manifests Phase 2 would relocate (project ≠ 'katib' but in content/katib/): "
                     f"{len(relocation_candidates)}")
        for r in relocation_candidates[:8]:
            lines.append(f"  · {r['project']:<24} ← {r['rel_path']}")
        if len(relocation_candidates) > 8:
            lines.append(f"  … and {len(relocation_candidates) - 8} more (use --verbose to list all)")
        lines.append("")

    # Stale katib_version
    stale = [r for r in results if r["katib_version"] == "0.1.0"]
    if stale:
        lines.append(f"Manifests with katib_version: 0.1.0 (stale, should auto-bump): {len(stale)}")

    legacy_agent = [r for r in results if r["source_agent"] == "claude-opus-4-7"]
    if legacy_agent:
        lines.append(f"Manifests with source_agent: claude-opus-4-7 (Phase 1 replaced this): "
                     f"{len(legacy_agent)}")

    return "\n".join(lines)


def format_text_verbose(results: list[dict]) -> str:
    """Per-manifest line listing every violation."""
    lines = [format_text_summary(results), "", "Per-manifest detail:", "=" * 40]
    for r in sorted(results, key=lambda x: (-x["errors"], -x["warns"], x["rel_path"])):
        header = f"{r['rel_path']}"
        if r["parse_error"]:
            lines.append(f"✗ {header}")
            lines.append(f"    parse error: {r['parse_error']}")
            continue
        if not r["violations"]:
            continue  # summary already covers clean count
        symbol = "✗" if r["errors"] else "⚠"
        lines.append(f"{symbol} {header}  [project={r['project']}, katib_version={r['katib_version']}]")
        for v in r["violations"]:
            lines.append(f"    {_violation_message(v)}")
    return "\n".join(lines)


def format_markdown_report(results: list[dict]) -> str:
    """Obsidian-friendly report for the vault."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = len(results)
    clean = sum(1 for r in results if not r["violations"] and not r["parse_error"])
    err_count = sum(1 for r in results if r["errors"])
    warn_only = sum(1 for r in results if not r["errors"] and r["warns"])

    lines = [
        "---",
        "type: audit-report",
        f"created: {today}",
        "tags: [katib, vault-integration, audit]",
        "project: katib",
        "---",
        "",
        f"# Katib vault audit — {today}",
        "",
        "Read-only scan of every Katib-authored manifest against the current",
        f"schema + zone governance rules. Produced by `scripts/audit_vault.py`.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---|",
        f"| Total manifests | {total} |",
        f"| Clean           | {clean} |",
        f"| With error(s)   | {err_count} |",
        f"| Warning only    | {warn_only} |",
        "",
        "## Violations by type",
        "",
    ]

    type_counter: Counter[tuple[str, str]] = Counter()
    for r in results:
        for v in r["violations"]:
            key = v.message.split(":", 1)[0] if ":" in v.message else v.message
            type_counter[(v.severity, key)] += 1

    lines.append("| Severity | Rule | Count |")
    lines.append("|---|---|---|")
    for (sev, msg), count in type_counter.most_common():
        lines.append(f"| {sev} | {msg} | {count} |")
    lines.append("")

    lines.append("## Project distribution")
    lines.append("")
    lines.append("| Project | Manifests |")
    lines.append("|---|---|")
    proj_counter: Counter[str] = Counter(r["project"] or "<missing>" for r in results)
    for proj, count in proj_counter.most_common():
        lines.append(f"| `{proj}` | {count} |")
    lines.append("")

    # Full per-manifest breakdown — only those with violations
    dirty = [r for r in results if r["violations"] or r["parse_error"]]
    if dirty:
        lines.append(f"## Manifests with violations ({len(dirty)})")
        lines.append("")
        lines.append("| Path | Errors | Warns | Project | katib_version |")
        lines.append("|---|---|---|---|---|")
        for r in sorted(dirty, key=lambda x: (-x["errors"], -x["warns"], x["rel_path"])):
            proj = r["project"] or "?"
            ver = r["katib_version"] or "?"
            lines.append(f"| `{r['rel_path']}` | {r['errors']} | {r['warns']} | {proj} | {ver} |")
        lines.append("")

    lines.append("## Next steps")
    lines.append("")
    lines.append("1. Review the drift above.")
    lines.append("2. Run `scripts/migrate_vault.py --dry-run` to see proposed changes.")
    lines.append("3. Review the migration plan.")
    lines.append("4. Run `scripts/migrate_vault.py --execute` to apply.")
    lines.append("")
    return "\n".join(lines)


def to_json(results: list[dict]) -> str:
    """Machine-readable — used by migrate_vault.py and by any downstream tool."""
    serialisable = []
    for r in results:
        serialisable.append({
            "rel_path": r["rel_path"],
            "zone": r["zone"],
            "project": r["project"],
            "domain": r["domain"],
            "doc_type": r["doc_type"],
            "katib_version": r["katib_version"],
            "source_agent": r["source_agent"],
            "errors": r["errors"],
            "warns": r["warns"],
            "violations": [
                {"severity": v.severity, "field": v.field, "message": v.message}
                for v in r["violations"]
            ],
            "parse_error": r["parse_error"],
        })
    return json.dumps(serialisable, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib vault audit")
    parser.add_argument("--vault-root", default=None,
                        help="Vault root (default: $KATIB_VAULT_ROOT or ~/vault)")
    parser.add_argument("--verbose", action="store_true",
                        help="List every violation for every manifest (not just summary)")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON instead of text")
    parser.add_argument("--report", nargs="?", const="auto", default=None,
                        help="Write markdown report to the vault. Pass a path or use 'auto' "
                             "for ~/vault/knowledge/katib-audit-YYYY-MM-DD.md")

    args = parser.parse_args()

    vault_root = Path(args.vault_root).expanduser() if args.vault_root else default_vault_root()
    if not vault_root.exists():
        print(f"✗ vault root not found: {vault_root}", file=sys.stderr)
        return 2

    manifests = find_manifests(vault_root)
    results = [audit_manifest(m, vault_root) for m in manifests]

    if args.json:
        print(to_json(results))
    elif args.verbose:
        print(format_text_verbose(results))
    else:
        print(format_text_summary(results))

    if args.report is not None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if args.report == "auto":
            report_path = vault_root / "knowledge" / f"katib-audit-{today}.md"
        else:
            report_path = Path(args.report).expanduser()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(format_markdown_report(results), encoding="utf-8")
        print(f"\n→ report written: {report_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
