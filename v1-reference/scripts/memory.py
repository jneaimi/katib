#!/usr/bin/env python3
"""Katib memory — append-only jsonl logs + read helpers.

Three log files live under cfg["memory"]["location"]:
  runs.jsonl             every successful render
  feedback.jsonl         user corrections ("change X to Y")
  domain-requests.jsonl  doc types that didn't fit any domain

Both reflect.py and build.py go through this module so the schema stays honest.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


def _mem_dir(cfg: dict) -> Path:
    loc = cfg.get("memory", {}).get("location")
    if not loc:
        raise ValueError("memory.location missing from cfg")
    path = Path(loc).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def log_run(cfg: dict, meta: dict, render_meta: dict, output: Path | str) -> None:
    """Append one row to runs.jsonl after a successful render."""
    row = {
        "ts": _now(),
        "domain": meta.get("domain"),
        "doc": meta.get("doc_type"),
        "lang": (meta.get("languages") or [None])[0],
        "layout": meta.get("layout"),
        "cover_style": meta.get("cover_style"),
        "pages": next(iter((render_meta.get("page_counts") or {}).values()), None),
        "tier": meta.get("tier"),
        "brand": meta.get("brand_name"),
        "output": str(output),
    }
    _append(_mem_dir(cfg) / "runs.jsonl", row)


def log_feedback(
    cfg: dict,
    *,
    domain: str,
    lang: str,
    before: str,
    after: str,
    reason: str = "",
    doc_type: str | None = None,
) -> None:
    row = {
        "ts": _now(),
        "domain": domain,
        "doc": doc_type,
        "lang": lang,
        "before": before,
        "after": after,
        "reason": reason,
    }
    _append(_mem_dir(cfg) / "feedback.jsonl", row)


def log_domain_request(cfg: dict, *, request: str, routed_to: str | None = None, reason: str = "") -> None:
    row = {
        "ts": _now(),
        "request": request,
        "routed_to": routed_to,
        "reason": reason,
    }
    _append(_mem_dir(cfg) / "domain-requests.jsonl", row)


def read_jsonl(cfg: dict, name: str) -> Iterator[dict[str, Any]]:
    path = _mem_dir(cfg) / name
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def filter_since(rows: Iterator[dict], since_days: int | None) -> Iterator[dict]:
    if not since_days:
        yield from rows
        return
    cutoff = datetime.now(timezone.utc).timestamp() - since_days * 86400
    for row in rows:
        ts = row.get("ts", "")
        try:
            if datetime.fromisoformat(ts).timestamp() >= cutoff:
                yield row
        except ValueError:
            continue


def memory_path(cfg: dict) -> Path:
    """Expose the resolved memory dir (for display/debug)."""
    return _mem_dir(cfg)
