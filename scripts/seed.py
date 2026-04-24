"""katib seed — starter content seeder.

The two-tier layout makes bundled recipes (in the skill folder) canonical and
user-tier recipes (in ~/.katib/) the editable, durable copies. On fresh
install, `install.sh` copies a curated set of bundled recipes into the user
tier so every install starts with working starters the user can modify
without touching the skill. This CLI is the opt-in counterpart for
returning users who want to pull a new starter the manifest added.

Subcommands:
    list                 Show manifest entries + which are already seeded
    refresh <name>       Copy bundled → user-tier if not present
    refresh --all        Refresh every manifest entry missing in user-tier
    refresh <name> --force --justification "why"
                         Overwrite an existing user-tier file

Global flag:
    --json               Emit JSON to stdout.

Exit codes:
    0   success (or no-op)
    1   operational error (missing bundled source, manifest mismatch, refused overwrite)
    2   bad CLI usage
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.tokens import user_memory_dir, user_recipes_dir  # noqa: E402

MANIFEST_PATH = REPO_ROOT / "seed-manifest.yaml"
BUNDLED_RECIPES_DIR = REPO_ROOT / "recipes"


class SeedError(RuntimeError):
    """Raised for any seed-flow failure the user should see."""


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise SeedError(f"seed manifest not found: {MANIFEST_PATH}")
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8")) or {}
    if data.get("version") != 1:
        raise SeedError(
            f"seed manifest version {data.get('version')!r} not supported "
            f"(this CLI understands version 1)"
        )
    recipes = data.get("recipes") or []
    components = data.get("components") or []
    if not isinstance(recipes, list) or not isinstance(components, list):
        raise SeedError("seed manifest 'recipes' and 'components' must be lists")
    # Every listed recipe must exist in the bundled tier.
    missing = [
        r for r in recipes
        if not (BUNDLED_RECIPES_DIR / f"{r}.yaml").exists()
    ]
    if missing:
        raise SeedError(
            "seed manifest references recipes that don't exist in the "
            "bundled tier: " + ", ".join(missing)
        )
    return {"version": 1, "recipes": recipes, "components": components}


def _log_event(event: dict) -> None:
    log_dir = user_memory_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "seed-events.jsonl"
    event["timestamp"] = datetime.now(timezone.utc).isoformat()
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _seed_recipe(
    name: str, *, force: bool = False, justification: str | None = None
) -> dict:
    src = BUNDLED_RECIPES_DIR / f"{name}.yaml"
    if not src.exists():
        raise SeedError(f"bundled recipe not found: {src}")
    dst_dir = user_recipes_dir()
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{name}.yaml"

    if dst.exists() and not force:
        return {"action": "skip", "recipe": name, "path": str(dst), "reason": "exists"}

    if dst.exists() and force and not justification:
        raise SeedError(
            f"refusing to overwrite {dst} without --justification '<why>'"
        )

    shutil.copy2(src, dst)
    event = {
        "event": "seed_recipe",
        "recipe": name,
        "source": str(src),
        "destination": str(dst),
        "forced": force,
    }
    if justification:
        event["justification"] = justification
    _log_event(event)
    return {"action": "seeded", "recipe": name, "path": str(dst)}


# ---------------------------------------------------------------------------
# subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_list(args) -> int:
    manifest = _load_manifest()
    dst_dir = user_recipes_dir()
    rows = []
    for r in manifest["recipes"]:
        target = dst_dir / f"{r}.yaml"
        rows.append({"name": r, "kind": "recipe", "seeded": target.exists(), "path": str(target)})
    if args.json:
        print(json.dumps({"user_tier": str(dst_dir), "items": rows}, ensure_ascii=False, indent=2))
    else:
        print(f"User tier: {dst_dir}")
        print(f"Manifest:  {MANIFEST_PATH.relative_to(REPO_ROOT)}")
        print()
        if not rows:
            print("(manifest lists no recipes)")
            return 0
        width = max(len(r["name"]) for r in rows)
        for r in rows:
            mark = "✓" if r["seeded"] else "·"
            print(f"  {mark}  {r['name']:<{width}}   {'seeded' if r['seeded'] else 'absent'}")
    return 0


def _cmd_refresh(args) -> int:
    manifest = _load_manifest()
    known = set(manifest["recipes"])

    if args.all:
        names = sorted(known)
    else:
        if not args.name:
            print("refresh requires <name> or --all", file=sys.stderr)
            return 2
        if args.name not in known:
            raise SeedError(
                f"recipe {args.name!r} is not in the seed manifest. "
                f"Known: {', '.join(sorted(known)) or '(none)'}"
            )
        names = [args.name]

    results = []
    had_error = False
    for name in names:
        try:
            results.append(
                _seed_recipe(
                    name, force=bool(args.force), justification=args.justification
                )
            )
        except SeedError as e:
            had_error = True
            results.append({"action": "error", "recipe": name, "message": str(e)})

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if r["action"] == "seeded":
                print(f"✓ seeded {r['recipe']} → {r['path']}")
            elif r["action"] == "skip":
                print(f"·  skipped {r['recipe']} ({r['reason']})")
            else:
                print(f"✗  {r['recipe']}: {r['message']}", file=sys.stderr)
    return 1 if had_error else 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="Show manifest + seeded state")
    p_list.set_defaults(func=_cmd_list)

    p_refresh = sub.add_parser("refresh", help="Copy bundled → user tier")
    p_refresh.add_argument("name", nargs="?", default=None)
    p_refresh.add_argument(
        "--all", action="store_true", help="Refresh every manifest entry"
    )
    p_refresh.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing user-tier files (requires --justification).",
    )
    p_refresh.add_argument(
        "--justification",
        default=None,
        help="Required when --force overwrites an existing file.",
    )
    p_refresh.set_defaults(func=_cmd_refresh)

    args = ap.parse_args(argv)

    try:
        return args.func(args)
    except SeedError as e:
        if args.json:
            print(json.dumps({"action": "error", "message": str(e)}, ensure_ascii=False))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
