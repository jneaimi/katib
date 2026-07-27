"""Generate capabilities.yaml from components/ + recipes/.

Auto-regenerates the flat, machine-readable index that agents read before any
routing decision. Never hand-edit capabilities.yaml — this script owns it.

Usage:
    uv run scripts/generate_capabilities.py
    uv run scripts/generate_capabilities.py --out capabilities.yaml
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"
RECIPES_DIR = REPO_ROOT / "recipes"
DEFAULT_OUT = REPO_ROOT / "capabilities.yaml"
SCHEMA_VERSION = 1

TIER_DIRS = ("primitives", "sections", "covers")

sys.path.insert(0, str(REPO_ROOT))
from core.tokens import user_components_dir, user_recipes_dir  # noqa: E402


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def collect_components(bundled_only: bool = False) -> dict[str, dict]:
    """Collect components from bundled AND user tiers. User-tier components
    shadow bundled ones of the same name (last-wins since user is processed
    second) — matches the render-time precedent in compose.

    `bundled_only=True` skips the user tier entirely — used to generate the
    COMMITTED capabilities.yaml, which must never carry private (namespace:
    user) content into the public repo.
    """
    out: dict[str, dict] = {}
    tiers = [COMPONENTS_DIR] if bundled_only else [COMPONENTS_DIR, user_components_dir()]
    component_dirs = [d for d in tiers if d.exists()]
    for base in component_dirs:
        for tier_dirname in TIER_DIRS:
            tier_dir = base / tier_dirname
            if not tier_dir.exists():
                continue
            for cdir in sorted(tier_dir.iterdir()):
                meta = cdir / "component.yaml"
                if not meta.exists():
                    continue
                c = _load_yaml(meta)
                name = c["name"]
                out[name] = {
                    "namespace": c.get("namespace", "katib"),
                    "tier": c.get("tier"),
                    "version": c.get("version"),
                    "languages": c.get("languages", []),
                    "variants": c.get("variants", []),
                    "description": c.get("description", ""),
                    "used_in_recipes": 0,
                }
    return out


def collect_recipes(components: dict[str, dict], bundled_only: bool = False) -> dict[str, dict]:
    """Collect recipes from bundled AND user tiers. User-tier recipes with
    the same name as a bundled recipe shadow the bundled one (last-wins
    since user tier is processed second).

    `bundled_only=True` skips the user tier — see collect_components().
    """
    out: dict[str, dict] = {}
    tiers = [RECIPES_DIR] if bundled_only else [RECIPES_DIR, user_recipes_dir()]
    recipe_dirs = [d for d in tiers if d.exists()]
    seen: set[str] = set()
    for rdir in recipe_dirs:
        for rfile in sorted(rdir.glob("*.yaml")):
            r = _load_yaml(rfile)
            name = r["name"]
            sections_shape = [s["component"] for s in r.get("sections", [])]
            out[name] = {
                "namespace": r.get("namespace", "katib"),
                "version": r.get("version"),
                "description": r.get("description", ""),
                "languages": r.get("languages", []),
                "target_pages": r.get("target_pages"),
                "page_limit": r.get("page_limit"),
                "when": r.get("when"),
                "keywords": r.get("keywords", []),
                "sections_shape": sections_shape,
            }
            # Only count component-usage once per recipe name to avoid
            # double-counting when a user recipe shadows a bundled one.
            if name in seen:
                continue
            seen.add(name)
            for cname in set(sections_shape):
                if cname in components:
                    components[cname]["used_in_recipes"] += 1
    return out


def governance() -> dict:
    return {
        "adding_component": {
            "forbidden": [
                "Hand-edit the components/ directory without an audit entry",
                "Hand-edit capabilities.yaml (regenerated from source)",
            ],
            "required_sequence": [
                "katib component new <name>    # scaffolder (Phase 2+)",
                "Fill in HTML variants + styles + README",
                "katib component validate <name>",
                "katib component test <name>",
                "katib component register <name>",
            ],
        },
        "adding_recipe": {
            "forbidden": [
                "Hand-edit recipes/ without an audit entry",
                "Hand-edit capabilities.yaml",
            ],
            "required_sequence": [
                "katib recipe new <name>       # scaffolder (Phase 2+)",
                "Fill in sections + metadata",
                "katib recipe validate <name>",
                "katib recipe register <name>",
            ],
        },
    }


def build_capabilities(bundled_only: bool = False) -> dict:
    components = collect_components(bundled_only=bundled_only)
    recipes = collect_recipes(components, bundled_only=bundled_only)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema_version": SCHEMA_VERSION,
        "governance": governance(),
        "recipes": recipes,
        "components": components,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="Output path.")
    ap.add_argument(
        "--bundled-only",
        action="store_true",
        help="Exclude the user tier (~/.katib). REQUIRED for the committed "
        "capabilities.yaml so private (namespace: user) content never enters "
        "the public repo.",
    )
    args = ap.parse_args(argv)

    caps = build_capabilities(bundled_only=args.bundled_only)
    text = yaml.safe_dump(caps, sort_keys=False, allow_unicode=True, width=100)
    banner = (
        "# capabilities.yaml — AUTO-GENERATED from components/ + recipes/.\n"
        "# Do not hand-edit. Regenerate the COMMITTED manifest with:\n"
        "#     uv run scripts/generate_capabilities.py --bundled-only\n"
        "# --bundled-only excludes the user tier (~/.katib) so private content\n"
        "# never enters the public repo. A pre-commit guard rejects any\n"
        "# 'namespace: user' entry here.\n\n"
    )
    out_path = Path(args.out)
    out_path.write_text(banner + text, encoding="utf-8")
    print(
        f"wrote {out_path}  "
        f"({len(caps['components'])} components, {len(caps['recipes'])} recipes)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
