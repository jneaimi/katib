"""katib recipe — recipe authoring CLI (parallel to scripts/component.py).

Subcommands:
    new <name>        Scaffold a new recipe (writes YAML + audit entry)
    validate <name>   Schema + component refs + lang compat + variants + keywords + pages
    test <name>       Render to PDF in a throwaway dir; --all-langs for every lang
    register <name>   Re-validate + regenerate capabilities.yaml + audit register entry
    share <name>      Bundle the recipe into dist/recipe-<name>-<version>.tar.gz
    lint --all        Validate every recipe

Global flag:
    --json            Emit JSON to stdout instead of human-readable text.

Examples:
    uv run scripts/recipe.py new my-proposal --languages en,ar
    uv run scripts/recipe.py validate tutorial
    uv run scripts/recipe.py test tutorial --all-langs
    uv run scripts/recipe.py register tutorial
    uv run scripts/recipe.py share tutorial
    uv run scripts/recipe.py lint --all

Exit codes:
    0   success
    1   operational error (validation failed, recipe missing, audit refused)
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

from core import recipe_ops as ops  # noqa: E402


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------


def _human_new(result: ops.RecipeScaffoldResult) -> str:
    lines = [
        f"✓ Scaffolded recipe {result.recipe} (namespace={result.namespace})",
        f"  path: {result.path}",
    ]
    if result.graduation_warning:
        lines.append(f"\n⚠ {result.graduation_warning}")
    lines.append(
        "\nNext steps:\n"
        "  1. Edit the recipe YAML — sections, inputs, keywords, target_pages\n"
        f"  2. uv run scripts/recipe.py validate {result.recipe}\n"
        f"  3. uv run scripts/recipe.py test {result.recipe}\n"
        f"  4. uv run scripts/recipe.py register {result.recipe}"
    )
    return "\n".join(lines)


def _human_validate(result: ops.RecipeValidationResult) -> str:
    lines = [f"{result.path} — validate"]
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


def _human_test(results: list[ops.RecipeRenderResult]) -> str:
    lines = ["Recipe render"]
    for r in results:
        status = "✓" if r.weasyprint_warnings == 0 else "⚠"
        lines.append(
            f"  {status} {r.lang} → {r.pdf_path} "
            f"({r.pdf_bytes} bytes, {r.weasyprint_warnings} wp warnings)"
        )
    return "\n".join(lines)


def _human_register(result: ops.RecipeRegisterResult) -> str:
    lines = [
        f"✓ recipe {result.recipe} registered",
        "  capabilities.yaml regenerated",
        f"  audit trail: action=register at={result.audit_entry['at']}",
    ]
    if result.validation.warnings:
        lines.append(f"  (with {len(result.validation.warnings)} warning(s) — see validate)")
    return "\n".join(lines)


def _human_share(result: ops.RecipeShareResult) -> str:
    lines = [
        f"✓ recipe {result.recipe} bundled",
        f"  path: {result.bundle_path}",
        f"  size: {result.bundle_bytes} bytes",
        "  includes:",
    ]
    for f in result.files_included:
        lines.append(f"    - {f}")
    return "\n".join(lines)


def _human_lint(results: list[ops.RecipeValidationResult]) -> str:
    total = len(results)
    failed = sum(1 for r in results if not r.ok)
    warns = sum(len(r.warnings) for r in results)
    lines = []
    for r in results:
        status = "✓" if r.ok else "✗"
        wstr = f" ({len(r.warnings)} warn)" if r.warnings else ""
        lines.append(f"  {status} {r.recipe}{wstr}")
    lines.append(
        f"\n{total - failed}/{total} ok, {failed} failed, {warns} total warnings."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# handlers
# ---------------------------------------------------------------------------


def _cmd_new(args) -> int:
    try:
        result = ops.scaffold_recipe(
            args.name,
            namespace=args.namespace,
            languages=(args.languages.split(",") if args.languages else None),
            description=args.description,
            domain_hint=args.domain_hint,
            target_pages=_parse_target_pages(args.target_pages),
            page_limit=args.page_limit,
            keywords=(args.keywords.split(",") if args.keywords else None),
            when=args.when,
            force=args.force,
            justification=args.justification,
            from_graduation=args.from_graduation,
            bilingual=args.bilingual,
        )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(_human_new(result))
    return 0


def _parse_target_pages(raw: str | None) -> list[int] | None:
    if raw is None:
        return None
    try:
        parts = [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError as e:
        raise ValueError(f"--target-pages expects 'lo,hi' integers: {e}") from e
    if len(parts) != 2:
        raise ValueError(f"--target-pages expects exactly two ints, got {parts}")
    return parts


def _cmd_validate(args) -> int:
    try:
        result = ops.validate_recipe_full(
            args.name,
            content_lint=not args.no_content_lint,
            strict=args.strict,
        )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(_human_validate(result))
    return 0 if result.ok else 1


def _cmd_test(args) -> int:
    try:
        langs = args.lang.split(",") if args.lang else None
        if args.all_langs:
            # Pass every declared lang — recipe_ops expands from the recipe's own declaration
            import yaml
            from core.recipe_ops import _recipe_path, _load_recipe_yaml
            data = _load_recipe_yaml(_recipe_path(args.name))
            langs = list(data.get("languages", []))
        results = ops.render_recipe(args.name, langs=langs, brand=args.brand)
    except (ValueError, RuntimeError, FileNotFoundError) as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))
    else:
        print(_human_test(results))

    if any(r.weasyprint_warnings > 0 for r in results):
        return 1
    return 0


def _cmd_register(args) -> int:
    try:
        result = ops.register_recipe(
            args.name,
            content_lint=not args.no_content_lint,
            strict=args.strict,
        )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(
            json.dumps(
                {
                    "recipe": result.recipe,
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
    try:
        result = ops.bundle_share_recipe(args.name)
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(_human_share(result))
    return 0


def _cmd_lint(args) -> int:
    if not args.all:
        print("lint requires --all (no per-recipe variant yet)", file=sys.stderr)
        return 2
    results = ops.lint_all_recipes(
        content_lint=not args.no_content_lint,
        strict=args.strict,
    )
    if args.json:
        print(json.dumps([r.as_dict() for r in results], ensure_ascii=False, indent=2))
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
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # new
    p_new = sub.add_parser("new", help="Scaffold a new recipe")
    p_new.add_argument("name")
    p_new.add_argument("--namespace", default="katib")
    p_new.add_argument("--languages", default=None, help="Comma-separated: en,ar")
    p_new.add_argument("--description", default=None)
    p_new.add_argument("--domain-hint", default=None)
    p_new.add_argument("--target-pages", default=None, help="e.g. '3,8' — lo,hi")
    p_new.add_argument("--page-limit", type=int, default=None)
    p_new.add_argument("--keywords", default=None, help="Comma-separated")
    p_new.add_argument("--when", default=None, help="One-line usage hint.")
    p_new.add_argument("--force", action="store_true")
    p_new.add_argument("--justification", default=None)
    p_new.add_argument("--from-graduation", default=None)
    p_new.add_argument(
        "--bilingual",
        action="store_true",
        help=(
            "Scaffold a bilingual EN+AR recipe. Sets languages to [en, ar] and "
            "structures each section's text inputs under inputs_by_lang.{en,ar} "
            "with placeholder strings (matches the legal-mou.yaml pattern)."
        ),
    )
    p_new.set_defaults(func=_cmd_new)

    # validate
    p_val = sub.add_parser("validate", help="Run validation")
    p_val.add_argument("name")
    p_val.add_argument(
        "--strict",
        action="store_true",
        help="Promote content-lint warnings to errors (CI-friendly).",
    )
    p_val.add_argument(
        "--no-content-lint",
        action="store_true",
        help="Skip the content_lint pass entirely (legacy content override).",
    )
    p_val.set_defaults(func=_cmd_validate)

    # test
    p_test = sub.add_parser("test", help="Render to PDF")
    p_test.add_argument("name")
    p_test.add_argument("--lang", default=None, help="Comma-separated langs; default = first declared")
    p_test.add_argument("--all-langs", action="store_true", help="Render every declared language")
    p_test.add_argument("--brand", default=None)
    p_test.set_defaults(func=_cmd_test)

    # register
    p_reg = sub.add_parser("register", help="Register the recipe")
    p_reg.add_argument("name")
    p_reg.add_argument(
        "--strict",
        action="store_true",
        help="Promote content-lint warnings to errors (blocks register).",
    )
    p_reg.add_argument(
        "--no-content-lint",
        action="store_true",
        help="Skip the content_lint pass entirely.",
    )
    p_reg.set_defaults(func=_cmd_register)

    # share
    p_share = sub.add_parser("share", help="Bundle the recipe")
    p_share.add_argument("name")
    p_share.set_defaults(func=_cmd_share)

    # lint
    p_lint = sub.add_parser("lint", help="Validate all recipes")
    p_lint.add_argument("--all", action="store_true", required=False)
    p_lint.add_argument(
        "--strict",
        action="store_true",
        help="Promote content-lint warnings to errors.",
    )
    p_lint.add_argument(
        "--no-content-lint",
        action="store_true",
        help="Skip the content_lint pass entirely.",
    )
    p_lint.set_defaults(func=_cmd_lint)

    args = ap.parse_args(argv)

    try:
        return args.func(args)
    except Exception as e:
        return _emit_error(e, json_out=getattr(args, "json", False))


if __name__ == "__main__":
    sys.exit(main())
