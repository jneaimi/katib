"""katib pack — share-format CLI (Phase 4).

Subcommands:
    export    Pack a component, recipe, brand, or bundle into a .katib-pack
    import    Install a .katib-pack into the user tier (Day 5)
    inspect   Show manifest + contents tree without writing to disk (Day 4)
    verify    Schema + hash + structural checks; CI-grade (Day 4)

Global flag:
    --json    Emit JSON to stdout instead of human-readable text.

Examples:
    uv run scripts/pack.py export --component eyebrow
    uv run scripts/pack.py export --recipe tutorial --author "Jane Doe <jane@example.com>"
    uv run scripts/pack.py export --brand example --out /tmp/

Exit codes:
    0   success
    1   operational error (artifact missing, schema violation, etc.)
    2   bad CLI usage / not yet implemented
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import pack as pack_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Human formatters
# ---------------------------------------------------------------------------


def _human_export(r: pack_mod.ExportResult) -> str:
    files = "\n    ".join(r.files_included) if r.files_included else "(none)"
    return (
        f"✓ {r.artifact_kind} {r.artifact_name!r} packed\n"
        f"  pack:    {r.pack_name}@{r.version}\n"
        f"  path:    {r.pack_path}\n"
        f"  size:    {r.pack_bytes} bytes\n"
        f"  hash:    {r.content_hash}\n"
        f"  files:\n    {files}"
    )


def _human_inspect(r: pack_mod.PackInspectResult) -> str:
    lines = [
        f"Pack: {r.name}@{r.version}",
        f"  path:          {r.pack_path}",
        f"  size:          {r.pack_bytes} bytes",
        f"  pack_format:   {r.pack_format}",
        f"  content_hash:  {r.content_hash_claim}",
    ]
    if r.author:
        author_line = r.author.get("name", "")
        if r.author.get("email"):
            author_line = f"{author_line} <{r.author['email']}>"
        lines.append(f"  author:        {author_line}")
    if r.license:
        lines.append(f"  license:       {r.license}")
    if r.description:
        lines.append(f"  description:   {r.description}")
    if r.tags:
        lines.append(f"  tags:          {', '.join(r.tags)}")

    lines.append("")
    lines.append("Contents:")
    components = r.contents.get("components") or []
    recipes = r.contents.get("recipes") or []
    brands = r.contents.get("brands") or []
    if components:
        lines.append(f"  components ({len(components)}):")
        for c in components:
            lines.append(f"    - {c['name']} ({c.get('tier', '?')})")
    if recipes:
        lines.append(f"  recipes ({len(recipes)}):")
        for r2 in recipes:
            lines.append(f"    - {r2['name']}")
    if brands:
        lines.append(f"  brands ({len(brands)}):")
        for b in brands:
            lines.append(f"    - {b['name']}")
    if not (components or recipes or brands):
        lines.append("  (empty)")

    if r.requires:
        lines.append("")
        lines.append("Requires:")
        for k, v in r.requires.items():
            lines.append(f"  {k}: {v}")

    lines.append("")
    lines.append(f"Files ({len(r.files)}):")
    for f in r.files:
        lines.append(f"  {f}")
    return "\n".join(lines)


def _human_verify(r: pack_mod.PackVerifyResult) -> str:
    status = "✓ VERIFIED" if r.ok else "✗ FAILED"
    lines = [f"{status}  {r.pack_name}", f"  path: {r.pack_path}", ""]

    def _row(label: str, ok: bool, note: str = "") -> str:
        check = "✓" if ok else "✗"
        return f"  {check} {label}{(' — ' + note) if note else ''}"

    lines.append(_row("pack_format supported", r.pack_format_supported))
    lines.append(
        _row(
            "manifest schema",
            not r.schema_errors,
            note=f"{len(r.schema_errors)} error(s)" if r.schema_errors else "",
        )
    )
    lines.append(
        _row(
            "content_hash matches body",
            r.hash_match,
            note="" if r.hash_match else "manifest hash differs from recomputed",
        )
    )
    lines.append(
        _row(
            "component validations",
            not any(r.component_issues.values()),
            note=(
                f"{sum(len(v) for v in r.component_issues.values())} error(s) "
                f"across {len(r.component_issues)} component(s)"
                if r.component_issues
                else ""
            ),
        )
    )
    lines.append(
        _row(
            "recipe validations",
            not any(r.recipe_issues.values()),
            note=(
                f"{sum(len(v) for v in r.recipe_issues.values())} error(s) "
                f"across {len(r.recipe_issues)} recipe(s)"
                if r.recipe_issues
                else ""
            ),
        )
    )

    if r.schema_errors:
        lines.append("")
        lines.append("Schema errors:")
        for e in r.schema_errors:
            lines.append(f"  - {e}")
    for name, issues in r.component_issues.items():
        lines.append("")
        lines.append(f"Component {name!r}:")
        for issue in issues:
            lines.append(f"  - [{issue['severity']}] {issue['category']}: {issue['message']}")
    for name, issues in r.recipe_issues.items():
        lines.append("")
        lines.append(f"Recipe {name!r}:")
        for issue in issues:
            lines.append(f"  - [{issue['severity']}] {issue['category']}: {issue['message']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _resolve_author(args) -> dict[str, str] | None:
    if getattr(args, "author", None):
        return pack_mod.parse_author_string(args.author)
    return None


def _cmd_export(args) -> int:
    out_dir = Path(args.out).expanduser().resolve() if args.out else None
    author = _resolve_author(args)

    # Exactly one of --component / --recipe / --brand / --bundle must be set.
    selectors = [
        ("component", args.component),
        ("recipe", args.recipe),
        ("brand", args.brand),
        ("bundle", args.bundle),
    ]
    selected = [(k, v) for k, v in selectors if v]
    if len(selected) != 1:
        msg = (
            "export requires exactly one of --component / --recipe / --brand / --bundle "
            f"(got {len(selected)})"
        )
        return _emit_error(ValueError(msg), json_out=args.json)

    kind, name = selected[0]
    if kind != "bundle" and getattr(args, "include_brand", None):
        return _emit_error(
            ValueError("--include-brand only applies to --bundle exports"),
            json_out=args.json,
        )

    try:
        if kind == "component":
            result = pack_mod.export_component(name, author=author, out_dir=out_dir)
        elif kind == "recipe":
            result = pack_mod.export_recipe(
                name,
                author=author,
                out_dir=out_dir,
                with_previews=bool(getattr(args, "with_previews", False)),
            )
        elif kind == "brand":
            result = pack_mod.export_brand(name, author=author, out_dir=out_dir)
        else:  # bundle
            result = pack_mod.export_bundle(
                name,
                include_brand=getattr(args, "include_brand", None),
                author=author,
                out_dir=out_dir,
            )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(_human_export(result))
    return 0


def _cmd_import(args) -> int:
    if not args.pack:
        return _emit_error(ValueError("import requires a pack path"), json_out=args.json)

    pack_path = Path(args.pack).expanduser().resolve()
    try:
        result = pack_mod.import_pack(
            pack_path,
            force=args.force,
            justification=args.justification,
            dry_run=args.dry_run,
        )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(_human_import(result))
    return 0


def _human_import(r: pack_mod.ImportResult) -> str:
    if r.dry_run:
        verb = "would import"
        files_label = "files that would be written"
        audit_label = "audit entries that would be added"
    else:
        verb = "imported"
        files_label = "files written"
        audit_label = "audit entries"

    lines = [
        f"{'⓿' if r.dry_run else '✓'} {r.pack_name}@{r.pack_version} {verb}",
        f"  {files_label}:    {len(r.files_written)}",
        f"  {audit_label}:    {r.audit_entries_added}",
    ]
    if not r.dry_run:
        lines.append(f"  capabilities regenerated: {r.capabilities_regenerated}")
    if r.force:
        lines.append(f"  force:            true")
        lines.append(f"  justification:    {r.justification!r}")
        if r.collisions_resolved:
            label = "would overwrite" if r.dry_run else "overwritten"
            lines.append(f"  {label}:      {len(r.collisions_resolved)}")

    if r.dry_run and r.files_written:
        lines.append("")
        lines.append("Plan:")
        for arc in r.files_written[:20]:
            lines.append(f"  + {arc}")
        if len(r.files_written) > 20:
            lines.append(f"  ...and {len(r.files_written) - 20} more")

    return "\n".join(lines)


def _cmd_inspect(args) -> int:
    pack_path = Path(args.pack).expanduser().resolve()
    try:
        result = pack_mod.inspect_pack(pack_path)
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(_human_inspect(result))
    return 0


def _cmd_verify(args) -> int:
    pack_path = Path(args.pack).expanduser().resolve()
    try:
        result = pack_mod.verify_pack(pack_path)
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        # Add `ok` derived field explicitly (it's a property, not a dataclass field).
        payload = asdict(result)
        payload["ok"] = result.ok
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_human_verify(result))
    return 0 if result.ok else 1


def _emit_error(exc: BaseException, *, json_out: bool) -> int:
    if json_out:
        print(
            json.dumps(
                {"action": "error", "message": str(exc), "type": type(exc).__name__},
                ensure_ascii=False,
            )
        )
    else:
        print(f"ERROR: {exc}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# Argparse setup
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # export
    p_export = sub.add_parser("export", help="Pack an artifact into .katib-pack")
    grp = p_export.add_mutually_exclusive_group(required=True)
    grp.add_argument("--component", help="Component name to pack")
    grp.add_argument("--recipe", help="Recipe name to pack")
    grp.add_argument("--brand", help="Brand name to pack")
    grp.add_argument(
        "--bundle",
        help="Recipe name; pack the recipe + its custom (user-tier) component deps",
    )
    p_export.add_argument(
        "--include-brand",
        default=None,
        help='Brand name to include in a --bundle pack (only valid with --bundle).',
    )
    p_export.add_argument(
        "--author",
        default=None,
        help='Author override: "Name <email>" or "Name". Defaults to git config.',
    )
    p_export.add_argument(
        "--out",
        default=None,
        help="Output directory for the .katib-pack file. Default: ./dist/",
    )
    p_export.add_argument(
        "--with-previews",
        action="store_true",
        help=(
            "Slice B — render captured HTML previews per declared lang and "
            "embed them in the pack under previews/. The marketplace "
            "publisher will upload these to R2 and the registry UI will "
            "show them in a sandboxed iframe."
        ),
    )
    p_export.set_defaults(func=_cmd_export)

    # import (stub until Day 5)
    p_import = sub.add_parser("import", help="Install a .katib-pack (Day 5)")
    p_import.add_argument("pack", nargs="?", help="Path to a .katib-pack file")
    p_import.add_argument("--force", action="store_true")
    p_import.add_argument("--justification", default=None)
    p_import.add_argument("--dry-run", action="store_true")
    p_import.set_defaults(func=_cmd_import)

    # inspect (stub until Day 4)
    p_inspect = sub.add_parser("inspect", help="Show manifest + contents (Day 4)")
    p_inspect.add_argument("pack", nargs="?", help="Path to a .katib-pack file")
    p_inspect.set_defaults(func=_cmd_inspect)

    # verify (stub until Day 4)
    p_verify = sub.add_parser("verify", help="Schema + hash + structural checks (Day 4)")
    p_verify.add_argument("pack", nargs="?", help="Path to a .katib-pack file")
    p_verify.set_defaults(func=_cmd_verify)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except Exception as e:  # never leak raw tracebacks
        return _emit_error(e, json_out=getattr(args, "json", False))


if __name__ == "__main__":
    sys.exit(main())
