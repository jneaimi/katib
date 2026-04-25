"""katib component — component authoring CLI.

Subcommands:
    new <name>        Scaffold a new component (writes files + audit entry)
    validate <name>   Full validation (schema, langs, tokens, brands, inputs, a11y, docs)
    test <name>       Render in isolation as a one-section recipe; assert clean PDF
    register <name>   Re-validate + regenerate capabilities.yaml + audit register entry
    share <name>      Bundle the component into dist/<name>-<version>.tar.gz
    lint --all        Validate every component

Global flag:
    --json            Emit JSON to stdout instead of human-readable text.

Examples:
    uv run scripts/component.py new my-widget --tier section
    uv run scripts/component.py validate eyebrow
    uv run scripts/component.py test chart-donut --lang en
    uv run scripts/component.py register chart-donut
    uv run scripts/component.py share chart-donut
    uv run scripts/component.py lint --all

Exit codes:
    0   success
    1   operational error (validation failed, component missing, audit refused)
    2   bad CLI usage
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import component_ops as ops  # noqa: E402


# ---------------------------------------------------------------------------
# text formatters
# ---------------------------------------------------------------------------


def _human_new(result: ops.ScaffoldResult) -> str:
    lines = [
        f"✓ Scaffolded {result.component} ({result.tier}, namespace={result.namespace})",
        f"  path: {result.path}",
        "  files:",
    ]
    for f in result.files_created:
        lines.append(f"    - {f}")
    if result.graduation_warning:
        lines.append(f"\n⚠ {result.graduation_warning}")
    lines.append(
        "\nNext steps:\n"
        "  1. Edit component.yaml, HTML variants, README.md\n"
        f"  2. uv run scripts/component.py validate {result.component}\n"
        f"  3. uv run scripts/component.py test {result.component}\n"
        f"  4. uv run scripts/component.py register {result.component}"
    )
    return "\n".join(lines)


def _human_validate(result: ops.ValidationResult) -> str:
    header = f"components/{result.path[len('components/'):]} — validate" if result.path.startswith("components/") else result.path
    lines = [header]
    if not result.issues:
        lines.append("  ✓ all checks passed")
    else:
        for issue in result.issues:
            marker = "✗" if issue.severity == "error" else "⚠"
            lines.append(f"  {marker} [{issue.category}] {issue.message}")
    lines.append(
        f"\n{len(result.errors)} error(s), {len(result.warnings)} warning(s)."
    )
    return "\n".join(lines)


def _human_test(results: list[ops.IsolatedRenderResult]) -> str:
    lines = ["Isolated render — test harness"]
    for r in results:
        status = "✓" if r.weasyprint_warnings == 0 else "⚠"
        variant = f" + {r.variant}" if r.variant else ""
        lines.append(
            f"  {status} {r.lang}{variant} → {r.pdf_path} "
            f"({r.pdf_bytes} bytes, {r.weasyprint_warnings} wp warnings)"
        )
    return "\n".join(lines)


def _human_register(result: ops.RegisterResult) -> str:
    lines = [
        f"✓ {result.component} registered",
        "  capabilities.yaml regenerated",
        f"  audit trail: action=register at={result.audit_entry['at']}",
    ]
    if result.validation.warnings:
        lines.append(f"  (with {len(result.validation.warnings)} warning(s) — see validate)")
    return "\n".join(lines)


def _human_share(result: ops.ShareResult) -> str:
    lines = [
        f"✓ {result.component} bundled",
        f"  path: {result.bundle_path}",
        f"  size: {result.bundle_bytes} bytes",
        "  includes:",
    ]
    for f in result.files_included:
        lines.append(f"    - {f}")
    return "\n".join(lines)


def _human_lint(results: list[ops.ValidationResult]) -> str:
    total = len(results)
    failed = sum(1 for r in results if not r.ok)
    warns = sum(len(r.warnings) for r in results)
    lines = []
    for r in results:
        status = "✓" if r.ok else "✗"
        wstr = f" ({len(r.warnings)} warn)" if r.warnings else ""
        lines.append(f"  {status} {r.component}{wstr}")
    lines.append(
        f"\n{total - failed}/{total} ok, {failed} failed, {warns} total warnings."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_new(args) -> int:
    try:
        result = ops.scaffold(
            args.name,
            tier=args.tier,
            namespace=args.namespace,
            languages=(args.languages.split(",") if args.languages else None),
            requires_tokens=(args.requires_tokens.split(",") if args.requires_tokens else None),
            description=args.description,
            force=args.force,
            justification=args.justification,
            from_graduation=args.from_graduation,
        )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        payload = asdict(result)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_human_new(result))
    return 0


def _cmd_validate(args) -> int:
    try:
        result = ops.validate_full(args.name)
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(_human_validate(result))
    return 0 if result.ok else 1


def _cmd_test(args) -> int:
    try:
        results = ops.render_isolated(
            args.name, lang=args.lang, variant=args.variant
        )
    except (ValueError, RuntimeError, FileNotFoundError) as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(
            json.dumps(
                [asdict(r) for r in results], ensure_ascii=False, indent=2
            )
        )
    else:
        print(_human_test(results))

    if any(r.weasyprint_warnings > 0 for r in results):
        return 1
    return 0


def _cmd_register(args) -> int:
    try:
        result = ops.register(args.name)
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(
            json.dumps(
                {
                    "component": result.component,
                    "capabilities_regenerated": result.capabilities_regenerated,
                    "audit_entry": result.audit_entry,
                    "validation": result.validation.as_dict(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(_human_register(result))
    return 0


def _cmd_share(args) -> int:
    print(
        "DEPRECATED: `katib component share` will be removed in a future release.\n"
        "Use `uv run scripts/pack.py export --component <name>` instead — it "
        "produces a `.katib-pack` artifact compatible with the marketplace "
        "(Phase 6) and supports recipes, brands, and bundles too. See PACK-FORMAT.md.",
        file=sys.stderr,
    )
    try:
        result = ops.bundle_share(args.name)
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(_human_share(result))
    return 0


def _cmd_lint(args) -> int:
    if not args.all:
        print("lint requires --all (no per-component variant yet)", file=sys.stderr)
        return 2
    results = ops.lint_all()
    if args.json:
        print(
            json.dumps(
                [r.as_dict() for r in results], ensure_ascii=False, indent=2
            )
        )
    else:
        print(_human_lint(results))
    return 0 if all(r.ok for r in results) else 1


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
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # new
    p_new = sub.add_parser("new", help="Scaffold a new component")
    p_new.add_argument("name")
    p_new.add_argument("--tier", required=True, choices=list(ops.TIER_DIRS))
    p_new.add_argument("--namespace", default="katib")
    p_new.add_argument("--languages", default=None, help="Comma-separated: en,ar")
    p_new.add_argument("--requires-tokens", default=None, help="Comma-separated")
    p_new.add_argument("--description", default=None)
    p_new.add_argument("--force", action="store_true", help="Override graduation gate.")
    p_new.add_argument("--justification", default=None, help="Required with --force.")
    p_new.add_argument("--from-graduation", default=None, help="Graduation proposal id.")
    p_new.set_defaults(func=_cmd_new)

    # validate
    p_validate = sub.add_parser("validate", help="Run validation")
    p_validate.add_argument("name")
    p_validate.set_defaults(func=_cmd_validate)

    # test
    p_test = sub.add_parser("test", help="Render in isolation")
    p_test.add_argument("name")
    p_test.add_argument("--lang", default=None, help="en | ar | bilingual")
    p_test.add_argument("--variant", default=None)
    p_test.set_defaults(func=_cmd_test)

    # register
    p_register = sub.add_parser("register", help="Register the component")
    p_register.add_argument("name")
    p_register.set_defaults(func=_cmd_register)

    # share
    p_share = sub.add_parser("share", help="Bundle the component")
    p_share.add_argument("name")
    p_share.set_defaults(func=_cmd_share)

    # lint
    p_lint = sub.add_parser("lint", help="Validate all components")
    p_lint.add_argument("--all", action="store_true", required=False)
    p_lint.set_defaults(func=_cmd_lint)

    args = ap.parse_args(argv)

    try:
        return args.func(args)
    except Exception as e:   # never leak raw tracebacks
        return _emit_error(e, json_out=getattr(args, "json", False))


if __name__ == "__main__":
    sys.exit(main())
