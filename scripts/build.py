"""katib build — render a recipe to PDF.

Phase 1 CLI (Python-only). The `katib` npx/shell wrapper gets rewired to
this in Phase 5. For now, invoke via uv:

    uv run scripts/build.py <recipe> --lang en
    uv run scripts/build.py <recipe> --lang ar --brand jasem --slug 2026-04-23-demo
    uv run scripts/build.py <recipe> --lang en --out /tmp/test.pdf
    uv run scripts/build.py <recipe> --lang en --skip-audit-check
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.brand_presets import (  # noqa: E402
    SavePresetError,
    find_cover_image,
    save_cover_preset,
)
from core.compose import compose  # noqa: E402
from core.output import resolve_document_folder  # noqa: E402
from core.render import render_to_pdf  # noqa: E402

COMPONENTS_DIR = REPO_ROOT / "components"
RECIPES_DIR = REPO_ROOT / "recipes"
AUDIT_FILE = REPO_ROOT / "memory" / "component-audit.jsonl"
RECIPE_AUDIT_FILE = REPO_ROOT / "memory" / "recipe-audit.jsonl"
TIER_DIRS = ("primitives", "sections", "covers")


class AuditError(RuntimeError):
    pass


def _on_disk_components() -> set[str]:
    out: set[str] = set()
    for tier_dirname in TIER_DIRS:
        tdir = COMPONENTS_DIR / tier_dirname
        if not tdir.exists():
            continue
        for cdir in tdir.iterdir():
            if (cdir / "component.yaml").exists():
                out.add(cdir.name)
    return out


def _audit_entries() -> set[str]:
    out: set[str] = set()
    if not AUDIT_FILE.exists():
        return out
    for line in AUDIT_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        name = entry.get("component")
        if name:
            out.add(name)
    return out


def _on_disk_recipes() -> set[str]:
    if not RECIPES_DIR.exists():
        return set()
    return {p.stem for p in RECIPES_DIR.glob("*.yaml")}


def _recipe_audit_entries() -> set[str]:
    if not RECIPE_AUDIT_FILE.exists():
        return set()
    out: set[str] = set()
    for line in RECIPE_AUDIT_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        name = entry.get("recipe")
        if name:
            out.add(name)
    return out


def check_audit() -> None:
    # Components
    on_disk = _on_disk_components()
    audited = _audit_entries()
    orphans = on_disk - audited
    if orphans:
        names = ", ".join(sorted(orphans))
        raise AuditError(
            "Component(s) present on disk without an audit entry:\n"
            f"    {names}\n"
            "Every component under components/ must have a matching entry "
            f"in {AUDIT_FILE.relative_to(REPO_ROOT)}.\n"
            "Either remove the component or seed an audit entry.\n"
            "(Use `uv run scripts/component.py new <name>` to handle this automatically.)"
        )
    # Recipes
    on_disk_recipes = _on_disk_recipes()
    audited_recipes = _recipe_audit_entries()
    recipe_orphans = on_disk_recipes - audited_recipes
    if recipe_orphans:
        names = ", ".join(sorted(recipe_orphans))
        raise AuditError(
            "Recipe(s) present on disk without an audit entry:\n"
            f"    {names}\n"
            "Every recipe under recipes/ must have a matching entry "
            f"in {RECIPE_AUDIT_FILE.relative_to(REPO_ROOT)}.\n"
            "Either remove the recipe or seed an audit entry.\n"
            "(Use `uv run scripts/recipe.py new <name>` to handle this automatically.)"
        )


def _default_slug(recipe: str) -> str:
    return f"{date.today().isoformat()}-{recipe}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("recipe", help="Recipe name (file in recipes/) or full path.")
    ap.add_argument("--lang", default="en", help="en | ar | bilingual")
    ap.add_argument("--brand", default=None, help="Brand profile name or path.")
    ap.add_argument("--slug", default=None, help="Output folder slug.")
    ap.add_argument(
        "--out", default=None, help="Override full output PDF path (bypasses slug)."
    )
    ap.add_argument(
        "--skip-audit-check",
        action="store_true",
        help="Skip the startup audit-presence check (tests only).",
    )
    ap.add_argument(
        "--save-cover-preset",
        metavar="NAME",
        default=None,
        help=(
            "After rendering, save the resolved cover image as a reusable preset "
            "on the --brand profile. Preset name must match [a-z0-9][a-z0-9_-]*."
        ),
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="With --save-cover-preset, overwrite an existing preset of the same name.",
    )
    args = ap.parse_args(argv)

    if args.save_cover_preset and not args.brand:
        print(
            "ERROR: --save-cover-preset requires --brand to know where to save.",
            file=sys.stderr,
        )
        return 1

    if not args.skip_audit_check:
        try:
            check_audit()
        except AuditError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    try:
        html, meta = compose(args.recipe, args.lang, brand=args.brand)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    recipe_name = meta["recipe"]["name"]
    if args.out:
        out_path = Path(args.out).expanduser().resolve()
    else:
        slug = args.slug or _default_slug(recipe_name)
        folder = resolve_document_folder(recipe_name, slug)
        out_path = folder / f"{recipe_name}.{args.lang}.pdf"

    pdf = render_to_pdf(html, out_path, base_url=REPO_ROOT)
    print(f"wrote {pdf}  ({pdf.stat().st_size} bytes)")

    if args.save_cover_preset:
        cover = find_cover_image(meta.get("resolved_images", []))
        if not cover:
            print(
                "ERROR: --save-cover-preset: no cover-tier image slot was "
                "resolved in this render (is the recipe using a cover component "
                "with an image input?).",
                file=sys.stderr,
            )
            return 1
        try:
            dest = save_cover_preset(
                brand=args.brand,
                preset_name=args.save_cover_preset,
                cover_image=cover,
                force=args.force,
            )
        except SavePresetError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print(
            f"saved cover preset {args.save_cover_preset!r} → {dest}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
