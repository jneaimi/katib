#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Katib reflect — summarise passive-capture logs and surface self-improvement leads.

Reads three append-only logs written by build.py (via memory.py):
  runs.jsonl             every successful render
  feedback.jsonl         user corrections
  domain-requests.jsonl  doc types that didn't fit any existing domain

Usage:
    uv run scripts/reflect.py                       # summary of last 30 days
    uv run scripts/reflect.py --since 7d            # last N days (Xd|Xw|all)
    uv run scripts/reflect.py --domain tutorial     # filter to one domain
    uv run scripts/reflect.py --stats               # counts only, skip proposals
    uv run scripts/reflect.py --propose             # write Markdown proposal to memory dir
    uv run scripts/reflect.py --json                # machine-readable output

What counts as a "proposal":
  - A before→after feedback pair that recurs ≥3 times (same domain/lang) → rename in writing.{lang}.md or templates.
  - A domain-request whose routed_to is the same and recurs ≥3 times → candidate new domain.
  - A doc type that renders 0 times in the window → deadweight (flag, don't delete).

reflect.py is READ-ONLY. Applying proposals stays manual in v0.10 — by design.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from config import load_config  # noqa: E402
from memory import filter_since, memory_path, read_jsonl  # noqa: E402

PROPOSAL_MIN_REPEATS = 3


def parse_since(spec: str | None) -> int | None:
    if not spec or spec == "all":
        return None
    m = re.fullmatch(r"(\d+)([dw])", spec.strip())
    if not m:
        raise ValueError(f"--since must match Nd or Nw (got {spec!r})")
    n, unit = int(m.group(1)), m.group(2)
    return n * (7 if unit == "w" else 1)


def _filter_domain(rows, domain):
    if not domain:
        yield from rows
        return
    for r in rows:
        if r.get("domain") == domain:
            yield r


def summarise(cfg: dict, *, since_days: int | None, domain_filter: str | None) -> dict:
    runs = list(_filter_domain(filter_since(read_jsonl(cfg, "runs.jsonl"), since_days), domain_filter))
    feedback = list(_filter_domain(filter_since(read_jsonl(cfg, "feedback.jsonl"), since_days), domain_filter))
    requests = list(filter_since(read_jsonl(cfg, "domain-requests.jsonl"), since_days))

    by_domain = Counter(r.get("domain") for r in runs if r.get("domain"))
    by_lang = Counter(r.get("lang") for r in runs if r.get("lang"))
    by_doc = Counter(f"{r.get('domain')}/{r.get('doc')}" for r in runs if r.get("domain") and r.get("doc"))
    by_layout = Counter(r.get("layout") for r in runs if r.get("layout"))
    by_brand = Counter(r.get("brand") for r in runs if r.get("brand"))

    # Pages histogram — coarse buckets
    page_buckets: Counter = Counter()
    for r in runs:
        p = r.get("pages")
        if isinstance(p, int):
            if p <= 2:
                page_buckets["1-2"] += 1
            elif p <= 5:
                page_buckets["3-5"] += 1
            elif p <= 10:
                page_buckets["6-10"] += 1
            elif p <= 20:
                page_buckets["11-20"] += 1
            else:
                page_buckets["21+"] += 1

    # Feedback clustering — (domain, lang, before, after) → count
    pair_counts: Counter = Counter()
    pair_reasons: dict[tuple, list[str]] = defaultdict(list)
    for f in feedback:
        key = (f.get("domain"), f.get("lang"), f.get("before"), f.get("after"))
        if all(key[:2]) and key[2] is not None and key[3] is not None:
            pair_counts[key] += 1
            if f.get("reason"):
                pair_reasons[key].append(f["reason"])

    # Domain requests — routed_to → count
    route_counts: Counter = Counter()
    route_samples: dict[str, list[str]] = defaultdict(list)
    for req in requests:
        routed = req.get("routed_to") or "(unrouted)"
        route_counts[routed] += 1
        if req.get("request"):
            route_samples[routed].append(req["request"])

    return {
        "window_days": since_days,
        "domain_filter": domain_filter,
        "runs_total": len(runs),
        "feedback_total": len(feedback),
        "requests_total": len(requests),
        "by_domain": by_domain.most_common(),
        "by_lang": by_lang.most_common(),
        "by_doc": by_doc.most_common(10),
        "by_layout": by_layout.most_common(),
        "by_brand": by_brand.most_common(5),
        "pages": sorted(page_buckets.items(), key=lambda kv: kv[0]),
        "pair_counts": pair_counts,
        "pair_reasons": pair_reasons,
        "route_counts": route_counts,
        "route_samples": route_samples,
    }


def build_proposals(summary: dict) -> list[dict]:
    proposals: list[dict] = []

    # Repeated corrections — candidate string swaps
    for (domain, lang, before, after), count in summary["pair_counts"].items():
        if count < PROPOSAL_MIN_REPEATS:
            continue
        target_file = f"references/writing.{lang}.md"
        reasons = summary["pair_reasons"].get((domain, lang, before, after), [])
        proposals.append({
            "kind": "string-swap",
            "domain": domain,
            "lang": lang,
            "count": count,
            "before": before,
            "after": after,
            "reason_samples": reasons[:3],
            "target": target_file,
            "action": (
                f"Users have corrected {before!r} → {after!r} {count} times in {domain}/{lang}. "
                f"Audit templates in domains/{domain}/templates/ and the phrasing guide "
                f"in {target_file}; replace where the correction is universally correct."
            ),
        })

    # Domain requests — candidate new domain
    for routed, count in summary["route_counts"].items():
        if count < PROPOSAL_MIN_REPEATS:
            continue
        samples = summary["route_samples"].get(routed, [])[:5]
        proposals.append({
            "kind": "new-domain-candidate",
            "routed_to": routed,
            "count": count,
            "sample_requests": samples,
            "action": (
                f"{count} user requests routed to {routed!r} as closest-match. "
                f"Review samples and decide whether to add a dedicated domain "
                f"or a new doc_type under {routed}."
            ),
        })

    # Unused doc types — stale templates
    used = {doc for doc, _ in summary["by_doc"]}
    all_types = _discover_doc_types()
    for key in sorted(all_types):
        if key not in used and not summary["domain_filter"]:
            proposals.append({
                "kind": "unused-doc-type",
                "doc_type": key,
                "action": (
                    f"{key} has not been rendered in this window. Flag for possible deprecation "
                    f"— but confirm with the user before removing."
                ),
            })

    return proposals


def _discover_doc_types() -> set[str]:
    """Walk domains/*/styles.json and collect every 'domain/doc_type' key."""
    out: set[str] = set()
    for styles_path in (SKILL_ROOT / "domains").glob("*/styles.json"):
        domain = styles_path.parent.name
        try:
            data = json.loads(styles_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for doc_type in (data.get("doc_types") or {}).keys():
            out.add(f"{domain}/{doc_type}")
    return out


def format_text(summary: dict, proposals: list[dict]) -> str:
    lines = []
    window = f"last {summary['window_days']} days" if summary["window_days"] else "all time"
    if summary["domain_filter"]:
        window += f" · domain={summary['domain_filter']}"
    lines.append(f"# Katib reflect — {window}")
    lines.append("")
    lines.append(
        f"runs: {summary['runs_total']}  ·  "
        f"feedback: {summary['feedback_total']}  ·  "
        f"domain-requests: {summary['requests_total']}"
    )
    lines.append("")

    if summary["by_domain"]:
        lines.append("## Renders by domain")
        for name, n in summary["by_domain"]:
            lines.append(f"  {n:>4}  {name}")
        lines.append("")

    if summary["by_lang"]:
        lines.append("## Language split")
        for name, n in summary["by_lang"]:
            lines.append(f"  {n:>4}  {name}")
        lines.append("")

    if summary["by_doc"]:
        lines.append("## Top doc types")
        for name, n in summary["by_doc"]:
            lines.append(f"  {n:>4}  {name}")
        lines.append("")

    if summary["pages"]:
        lines.append("## Page-count buckets")
        for bucket, n in summary["pages"]:
            lines.append(f"  {n:>4}  {bucket} pp")
        lines.append("")

    if summary["by_brand"]:
        lines.append("## Brand profiles used")
        for name, n in summary["by_brand"]:
            lines.append(f"  {n:>4}  {name}")
        lines.append("")

    if proposals:
        lines.append("## Proposals")
        lines.append("")
        for i, p in enumerate(proposals, 1):
            lines.append(f"### {i}. {p['kind']}")
            for key, val in p.items():
                if key in {"kind", "action"}:
                    continue
                if isinstance(val, list):
                    if not val:
                        continue
                    lines.append(f"- **{key}:**")
                    for item in val:
                        lines.append(f"  - {item}")
                else:
                    lines.append(f"- **{key}:** {val}")
            lines.append("")
            lines.append(f"> {p['action']}")
            lines.append("")
    else:
        lines.append("## Proposals")
        lines.append("")
        lines.append(
            "_Nothing recurs ≥3 times in this window. Keep capturing corrections as "
            "they come up — reflect will surface patterns once there's signal._"
        )
        lines.append("")

    return "\n".join(lines)


def write_proposal_file(mem_dir: Path, text: str) -> Path:
    proposals_dir = mem_dir / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    path = proposals_dir / f"{stamp}-reflect.md"
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib reflect — passive-log analyser")
    parser.add_argument("--since", default="30d", help="Time window: Nd, Nw, or 'all' (default 30d)")
    parser.add_argument("--domain", default=None, help="Filter to one domain")
    parser.add_argument("--stats", action="store_true", help="Counts only, skip proposals")
    parser.add_argument("--propose", action="store_true", help="Also write proposal to memory/proposals/")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    try:
        since_days = parse_since(args.since)
    except ValueError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2

    cfg = load_config()
    summary = summarise(cfg, since_days=since_days, domain_filter=args.domain)
    proposals = [] if args.stats else build_proposals(summary)

    if args.json:
        # Tuple keys → strings so the payload is JSON-serialisable
        jsonable_pairs = [
            {"domain": k[0], "lang": k[1], "before": k[2], "after": k[3], "count": v}
            for k, v in summary["pair_counts"].items()
        ]
        payload = {
            **{k: v for k, v in summary.items() if k not in {"pair_counts", "pair_reasons"}},
            "pair_counts": jsonable_pairs,
            "proposals": proposals,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    text = format_text(summary, proposals)
    print(text)

    if args.propose:
        path = write_proposal_file(memory_path(cfg), text)
        print(f"\n→ proposal written: {path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
