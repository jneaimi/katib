"""Validate one or more component.yaml files against the schema.

Phase 1 shape — covers just the schema-conformance check. Phase 2 extends
this to the full validator described in the ADR (token/input hygiene,
HTML parseability, README completeness, test presence).

Usage:
    uv run scripts/validate_component.py                       # all components
    uv run scripts/validate_component.py eyebrow callout       # specific names
    uv run scripts/validate_component.py --tier primitive      # filter by tier

Exit:
    0 — all validated
    1 — one or more failures
    2 — bad input
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"
SCHEMA_FILE = REPO_ROOT / "schemas" / "component.yaml.schema.json"
TIER_DIRS = {"primitive": "primitives", "section": "sections", "cover": "covers"}


def _load_schema() -> dict:
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


def _iter_component_files(
    tier: str | None = None, names: list[str] | None = None
) -> list[Path]:
    out: list[Path] = []
    tier_dirs = [TIER_DIRS[tier]] if tier else list(TIER_DIRS.values())
    for tier_dirname in tier_dirs:
        tdir = COMPONENTS_DIR / tier_dirname
        if not tdir.exists():
            continue
        for cdir in sorted(tdir.iterdir()):
            if names and cdir.name not in names:
                continue
            meta = cdir / "component.yaml"
            if meta.exists():
                out.append(meta)
    return out


def validate_file(path: Path, validator: Draft202012Validator) -> list[str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [f"{list(e.path)}: {e.message}" for e in errors]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "names", nargs="*", help="Component names to validate. Default: all."
    )
    ap.add_argument(
        "--tier", choices=list(TIER_DIRS.keys()), help="Limit to a specific tier."
    )
    args = ap.parse_args(argv)

    paths = _iter_component_files(tier=args.tier, names=args.names or None)
    if not paths:
        print("no components found matching filter", file=sys.stderr)
        return 2

    schema = _load_schema()
    validator = Draft202012Validator(schema)

    total = len(paths)
    failed = 0
    for p in paths:
        errors = validate_file(p, validator)
        name = p.parent.name
        if errors:
            failed += 1
            print(f"  ✗ {name}")
            for err in errors:
                print(f"      {err}")
        else:
            print(f"  ✓ {name}")

    print(f"\n{total - failed}/{total} components valid, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
