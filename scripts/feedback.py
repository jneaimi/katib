#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Katib — feedback.py: capture user corrections to feedback.jsonl.

Thin CLI wrapper around memory.log_feedback. Exists because the feedback loop
only pays off when corrections actually get logged — and nobody imports a
Python helper mid-conversation. A one-line bash command collapses the friction
to zero, so reflect.py's `string-swap` detection starts receiving real signal.

Usage:
    # Log a correction
    python3 scripts/feedback.py add \\
        --before "click" --after "select" \\
        --domain tutorial --lang en \\
        --reason "consistency with existing UI copy"

    # List recent rows
    python3 scripts/feedback.py list
    python3 scripts/feedback.py list --since 30d --domain tutorial
    python3 scripts/feedback.py list --limit 5

    # Search for rows mentioning a term in either `before` or `after`
    python3 scripts/feedback.py search "click"
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from config import load_config  # noqa: E402
from memory import (  # noqa: E402
    filter_since,
    log_feedback,
    memory_path,
    read_jsonl,
)


_SINCE_RE = re.compile(r"^(\d+)([dw])$")


def parse_since(s: str | None) -> int | None:
    """'7d' → 7; '2w' → 14; None → None (no filter)."""
    if not s:
        return None
    m = _SINCE_RE.match(s)
    if not m:
        raise argparse.ArgumentTypeError(f"--since must look like '7d' or '2w', got {s!r}")
    n, unit = int(m.group(1)), m.group(2)
    return n if unit == "d" else n * 7


# ===================== COMMANDS =====================

def cmd_add(args: argparse.Namespace) -> int:
    cfg = load_config()
    log_feedback(
        cfg,
        domain=args.domain,
        lang=args.lang,
        before=args.before,
        after=args.after,
        reason=args.reason or "",
        doc_type=args.doc,
    )
    mem = memory_path(cfg)
    print(f"✓ feedback logged — {args.domain}/{args.lang}: {args.before!r} → {args.after!r}")
    print(f"  → {mem / 'feedback.jsonl'}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    cfg = load_config()
    since_days = parse_since(args.since)
    rows = list(filter_since(read_jsonl(cfg, "feedback.jsonl"), since_days))

    if args.domain:
        rows = [r for r in rows if r.get("domain") == args.domain]
    if args.lang:
        rows = [r for r in rows if r.get("lang") == args.lang]

    if not rows:
        print("(no feedback rows match the filter)")
        return 0

    # Keep the last N (most recent) — read_jsonl returns in insertion order
    rows = rows[-args.limit:]
    _print_rows(rows)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    cfg = load_config()
    needle = args.term.lower()
    rows = [
        r for r in read_jsonl(cfg, "feedback.jsonl")
        if needle in (r.get("before") or "").lower()
        or needle in (r.get("after") or "").lower()
    ]
    if not rows:
        print(f"(no feedback rows match {args.term!r})")
        return 0
    print(f"▶ {len(rows)} row(s) matching {args.term!r}:\n")
    _print_rows(rows)
    return 0


# ===================== OUTPUT =====================

def _print_rows(rows: list[dict]) -> None:
    for r in rows:
        ts = (r.get("ts") or "")[:19].replace("T", " ")
        d = r.get("domain", "-")
        lang = r.get("lang", "-")
        doc = r.get("doc") or ""
        doc_str = f"/{doc}" if doc else ""
        before = r.get("before", "")
        after = r.get("after", "")
        reason = r.get("reason") or ""
        print(f"  {ts}  {d}{doc_str}/{lang}  {before!r} → {after!r}")
        if reason:
            print(f"  {'':19}  (reason: {reason})")


# ===================== MAIN =====================

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="feedback.py",
        description="Log + browse Katib feedback corrections.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Log a before→after correction")
    p_add.add_argument("--before", required=True, help="The wording/value that was wrong")
    p_add.add_argument("--after",  required=True, help="The replacement the user wants")
    p_add.add_argument("--domain", required=True, help="Domain (e.g., tutorial, business-proposal)")
    p_add.add_argument("--lang",   required=True, choices=["en", "ar"], help="Language")
    p_add.add_argument("--reason", default="", help="Short why (optional but helpful for reflect)")
    p_add.add_argument("--doc", dest="doc", default=None,
                       help="Doc type (optional, e.g. how-to, proposal)")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="Show recent feedback rows")
    p_list.add_argument("--since", default=None, help="Window: Nd or Nw (e.g., 7d, 2w)")
    p_list.add_argument("--domain", default=None, help="Filter by domain")
    p_list.add_argument("--lang", default=None, choices=["en", "ar"], help="Filter by lang")
    p_list.add_argument("--limit", type=int, default=20, help="Max rows to print (default 20)")
    p_list.set_defaults(func=cmd_list)

    # search
    p_search = sub.add_parser("search", help="Find rows where a term appears in before/after")
    p_search.add_argument("term", help="Substring to search for (case-insensitive)")
    p_search.set_defaults(func=cmd_search)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
