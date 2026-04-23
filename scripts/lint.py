"""katib lint — mechanical content-lint (anti-slop) for HTML / Markdown.

Usage:
    uv run scripts/lint.py <file>                # auto-detect lang
    uv run scripts/lint.py <file> --lang ar      # force Arabic ruleset
    uv run scripts/lint.py <file> --lang en      # force English ruleset
    uv run scripts/lint.py <file> --json         # machine-readable
    uv run scripts/lint.py --stdin --lang ar     # read from stdin

Exit codes:
    0   clean
    1   violations found (errors)
    2   bad input
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import content_lint as cl  # noqa: E402


def _format_text(violations: list[cl.Violation], label: str) -> str:
    if not violations:
        return f"✓ {label}: clean (0 violations)"
    errs = [v for v in violations if v.severity == "error"]
    warns = [v for v in violations if v.severity == "warn"]
    lines = [f"✗ {label}: {len(errs)} error(s), {len(warns)} warning(s)"]
    for v in violations:
        sev = "ERROR" if v.severity == "error" else "warn "
        lines.append(f"  [{sev}] L{v.line:4d} · {v.rule}: {v.pattern}")
        if v.snippet:
            lines.append(f"         → {v.snippet}")
    return "\n".join(lines)


def _format_json(violations: list[cl.Violation], label: str) -> str:
    return json.dumps(
        {
            "file": label,
            "clean": not violations,
            "error_count": sum(1 for v in violations if v.severity == "error"),
            "warning_count": sum(1 for v in violations if v.severity == "warn"),
            "violations": [v.as_dict() for v in violations],
        },
        ensure_ascii=False,
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="Path to file (HTML or MD). Omit with --stdin.")
    ap.add_argument("--stdin", action="store_true", help="Read from stdin instead of a file.")
    ap.add_argument("--lang", choices=["ar", "en"], help="Force lang; default: auto-detect.")
    ap.add_argument("--json", action="store_true", help="Machine-readable output.")
    args = ap.parse_args(argv)

    if args.stdin:
        raw = sys.stdin.read()
        label = "<stdin>"
        path = None
    else:
        if not args.file:
            print("ERROR: provide a file path or --stdin", file=sys.stderr)
            return 2
        path = Path(args.file).expanduser()
        if not path.exists():
            if args.json:
                print(json.dumps({"action": "error", "message": f"file not found: {path}"}))
            else:
                print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
        raw = path.read_text(encoding="utf-8")
        label = str(path)

    text = cl.extract_text(raw)
    lang = args.lang or cl.guess_language(path, text)

    try:
        violations = cl.lint(text, lang)
    except ValueError as e:
        if args.json:
            print(json.dumps({"action": "error", "message": str(e)}))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(_format_json(violations, label))
    else:
        print(_format_text(violations, label))

    errors = sum(1 for v in violations if v.severity == "error")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
