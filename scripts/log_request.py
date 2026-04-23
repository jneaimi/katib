"""katib log-request — append graduation-gate request entries.

Subcommands:
    component --requested X [--closest Y] --intent "..." --reason "..."
    recipe    --requested X [--closest Y] --intent "..." --reason "..."
    list      {component|recipe} [--since 30d]
    count     {component|recipe} <name>
    search    {component|recipe} <term>

Global flag:
    --json            Emit JSON to stdout instead of human-readable text.

Exit codes:
    0   success
    1   operational error (bad input, permission denied)
    2   bad CLI usage
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import request_log as rl  # noqa: E402


# ---------------------------------------------------------------------------
# handlers
# ---------------------------------------------------------------------------


def _cmd_component(args) -> int:
    try:
        entry = rl.log_component_request(
            requested=args.requested,
            closest_existing=args.closest,
            intent=args.intent,
            reason=args.reason,
            source=args.source,
            logged_by=args.logged_by,
        )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    else:
        print(f"✓ component request logged: {entry['requested'] or entry['closest_existing']}")
        print(f"  → {_pretty_path(rl._file_for_kind('component'))}")
    return 0


def _pretty_path(p: Path) -> str:
    """Show paths relative to the repo when possible; absolute otherwise."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def _cmd_recipe(args) -> int:
    try:
        entry = rl.log_recipe_request(
            requested=args.requested,
            closest_existing=args.closest,
            intent=args.intent,
            reason=args.reason,
            source=args.source,
            logged_by=args.logged_by,
        )
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    if args.json:
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    else:
        print(f"✓ recipe request logged: {entry['requested'] or entry['closest_existing']}")
        print(f"  → {_pretty_path(rl._file_for_kind('recipe'))}")
    return 0


def _cmd_list(args) -> int:
    try:
        since = rl.parse_since(args.since)
    except ValueError as e:
        return _emit_error(e, json_out=args.json)

    entries = rl.read_requests(args.kind, since=since)
    if args.json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return 0

    if not entries:
        print(f"(no {args.kind} requests)")
        return 0

    for e in entries:
        ts = (e.get("ts") or "")[:19].replace("T", " ")
        name = e.get("requested") or e.get("closest_existing") or "?"
        intent = (e.get("intent") or "")[:80]
        print(f"  {ts}  {name}  — {intent}")
    print(f"\n{len(entries)} entries.")
    return 0


def _cmd_count(args) -> int:
    n = rl.count_requests(args.kind, args.name)
    if args.json:
        print(json.dumps({"kind": args.kind, "name": args.name, "count": n}))
    else:
        print(f"{args.kind} {args.name!r}: {n} request(s)")
    return 0


def _cmd_search(args) -> int:
    entries = rl.search_requests(args.kind, args.term)
    if args.json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return 0
    if not entries:
        print(f"(no {args.kind} requests match {args.term!r})")
        return 0
    for e in entries:
        ts = (e.get("ts") or "")[:19].replace("T", " ")
        name = e.get("requested") or e.get("closest_existing") or "?"
        intent = (e.get("intent") or "")[:80]
        print(f"  {ts}  {name}  — {intent}")
    print(f"\n{len(entries)} matches.")
    return 0


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

    # component
    p_comp = sub.add_parser("component", help="Log a component request")
    p_comp.add_argument("--requested", default=None, help="Name the user asked for.")
    p_comp.add_argument("--closest", default=None, help="Closest existing component name.")
    p_comp.add_argument("--intent", required=True, help="What the user was trying to produce.")
    p_comp.add_argument("--reason", required=True, help="Why the closest isn't a fit.")
    p_comp.add_argument("--source", default="cli")
    p_comp.add_argument("--logged-by", default="katib")
    p_comp.set_defaults(func=_cmd_component)

    # recipe
    p_rec = sub.add_parser("recipe", help="Log a recipe request")
    p_rec.add_argument("--requested", default=None)
    p_rec.add_argument("--closest", default=None)
    p_rec.add_argument("--intent", required=True)
    p_rec.add_argument("--reason", required=True)
    p_rec.add_argument("--source", default="cli")
    p_rec.add_argument("--logged-by", default="katib")
    p_rec.set_defaults(func=_cmd_recipe)

    # list
    p_list = sub.add_parser("list", help="Show recent request rows")
    p_list.add_argument("kind", choices=["component", "recipe"])
    p_list.add_argument("--since", default=None, help="Window: e.g. 7d, 2w, 12h")
    p_list.set_defaults(func=_cmd_list)

    # count
    p_count = sub.add_parser("count", help="Count requests matching a name")
    p_count.add_argument("kind", choices=["component", "recipe"])
    p_count.add_argument("name")
    p_count.set_defaults(func=_cmd_count)

    # search
    p_search = sub.add_parser("search", help="Search requests by substring")
    p_search.add_argument("kind", choices=["component", "recipe"])
    p_search.add_argument("term")
    p_search.set_defaults(func=_cmd_search)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except Exception as e:
        return _emit_error(e, json_out=getattr(args, "json", False))


if __name__ == "__main__":
    sys.exit(main())
