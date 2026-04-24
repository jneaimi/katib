"""Request log — JSONL writers for graduation gate + gate/sensor observability.

Activates the Day-11 (component) and Day-12 (recipe) graduation gates by
persisting the request entries those gates read. Also persists every gate
decision (from `gate.resolve`) and context inference (from
`context_sensor.infer_signals`) that `scripts/route.py` produces.

Four JSONL files under `memory/` (or `$KATIB_MEMORY_DIR` if set):

    component-requests.jsonl    graduation-gate input for components
    recipe-requests.jsonl       graduation-gate input for recipes
    gate-decisions.jsonl        every route.py resolve decision
    context-inferences.jsonl    every route.py infer signal extraction

Writes are POSIX atomic-append (line-level, under 4KB). No locking needed at
Phase 2 scale. Concurrent agents safe as long as each append is a single
`write()` call with a trailing newline.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUEST_SCHEMA_VERSION = 1
GATE_LOG_SCHEMA_VERSION = 1
CONTEXT_LOG_SCHEMA_VERSION = 1

Kind = Literal["component", "recipe"]


def memory_dir() -> Path:
    """Resolve the memory directory — delegates to `tokens.user_memory_dir()`.

    Unified in Phase 2 so `request_log` (graduation-gate reader) and the ops
    modules (audit writers) share a single source of truth. Any
    $KATIB_MEMORY_DIR override is handled inside `tokens.user_memory_dir()`.
    """
    from core.tokens import user_memory_dir
    return user_memory_dir()


def _file_for_kind(kind: Kind) -> Path:
    if kind == "component":
        return memory_dir() / "component-requests.jsonl"
    if kind == "recipe":
        return memory_dir() / "recipe-requests.jsonl"
    raise ValueError(f"unknown kind {kind!r}; expected 'component' or 'recipe'")


def _gate_decisions_file() -> Path:
    return memory_dir() / "gate-decisions.jsonl"


def _context_inferences_file() -> Path:
    return memory_dir() / "context-inferences.jsonl"


def _append_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    # Single write() → POSIX atomic for lines under 4KB
    with path.open("a", encoding="utf-8") as f:
        f.write(line)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Graduation-gate writers
# ---------------------------------------------------------------------------


@dataclass
class RequestEntry:
    """The canonical record shape Day-11/12 graduation gates read."""

    kind: Kind
    requested: str | None
    closest_existing: str | None
    intent: str
    reason: str
    source: str = "cli"
    logged_by: str = "katib"
    ts: str | None = None

    def to_dict(self) -> dict:
        return {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "ts": self.ts or _now(),
            "kind": self.kind,
            "requested": self.requested,
            "closest_existing": self.closest_existing,
            "intent": self.intent,
            "reason": self.reason,
            "source": self.source,
            "logged_by": self.logged_by,
        }


def log_component_request(
    *,
    requested: str | None,
    closest_existing: str | None,
    intent: str,
    reason: str,
    source: str = "cli",
    logged_by: str = "katib",
    ts: str | None = None,
) -> dict:
    """Append an entry to component-requests.jsonl. Returns the written dict."""
    if not requested and not closest_existing:
        raise ValueError(
            "must supply at least one of requested / closest_existing"
        )
    entry = RequestEntry(
        kind="component",
        requested=requested,
        closest_existing=closest_existing,
        intent=intent,
        reason=reason,
        source=source,
        logged_by=logged_by,
        ts=ts,
    ).to_dict()
    _append_jsonl(_file_for_kind("component"), entry)
    return entry


def log_recipe_request(
    *,
    requested: str | None,
    closest_existing: str | None,
    intent: str,
    reason: str,
    source: str = "cli",
    logged_by: str = "katib",
    ts: str | None = None,
) -> dict:
    """Append an entry to recipe-requests.jsonl. Returns the written dict."""
    if not requested and not closest_existing:
        raise ValueError(
            "must supply at least one of requested / closest_existing"
        )
    entry = RequestEntry(
        kind="recipe",
        requested=requested,
        closest_existing=closest_existing,
        intent=intent,
        reason=reason,
        source=source,
        logged_by=logged_by,
        ts=ts,
    ).to_dict()
    _append_jsonl(_file_for_kind("recipe"), entry)
    return entry


# ---------------------------------------------------------------------------
# Observability writers (gate + sensor)
# ---------------------------------------------------------------------------


def log_gate_decision(log_entry: dict) -> None:
    """Persist a gate-resolve log_entry (as produced by `gate.resolve`).

    Never raises on a bad shape — always writes whatever dict it gets so we
    can debug after the fact. Missing schema_version gets a default.
    """
    entry = dict(log_entry)
    entry.setdefault("schema_version", GATE_LOG_SCHEMA_VERSION)
    entry.setdefault("ts", _now())
    _append_jsonl(_gate_decisions_file(), entry)


def log_context_inference(log_entry: dict) -> None:
    """Persist a context_sensor log_entry (as produced by `infer_signals`)."""
    entry = dict(log_entry)
    entry.setdefault("schema_version", CONTEXT_LOG_SCHEMA_VERSION)
    entry.setdefault("ts", _now())
    _append_jsonl(_context_inferences_file(), entry)


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------


_SINCE_RE = re.compile(r"^(\d+)([dwh])$")


def parse_since(spec: str | None) -> timedelta | None:
    """'7d' → 7 days, '2w' → 14 days, '12h' → 12 hours, None → None."""
    if not spec:
        return None
    m = _SINCE_RE.match(spec)
    if not m:
        raise ValueError(f"--since must look like '7d', '2w', or '12h'; got {spec!r}")
    n, unit = int(m.group(1)), m.group(2)
    if unit == "h":
        return timedelta(hours=n)
    days = n if unit == "d" else n * 7
    return timedelta(days=days)


def _read_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def read_requests(
    kind: Kind,
    *,
    since: timedelta | None = None,
) -> list[dict]:
    """Return request entries for `kind`, optionally filtered by recency."""
    entries = _read_entries(_file_for_kind(kind))
    if since is None:
        return entries
    cutoff = datetime.now(timezone.utc) - since
    out: list[dict] = []
    for e in entries:
        ts_raw = e.get("ts")
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw)
        except ValueError:
            continue
        if ts >= cutoff:
            out.append(e)
    return out


def count_requests(kind: Kind, name: str) -> int:
    """Count entries matching `name` via requested OR closest_existing."""
    n = 0
    for e in _read_entries(_file_for_kind(kind)):
        if e.get("requested") == name or e.get("closest_existing") == name:
            n += 1
    return n


def search_requests(kind: Kind, needle: str) -> list[dict]:
    """Return entries where `needle` appears in requested/closest_existing/intent/reason."""
    needle_lower = needle.lower()
    out: list[dict] = []
    for e in _read_entries(_file_for_kind(kind)):
        hay = " ".join(
            str(e.get(k) or "")
            for k in ("requested", "closest_existing", "intent", "reason")
        ).lower()
        if needle_lower in hay:
            out.append(e)
    return out


def read_gate_decisions(*, since: timedelta | None = None) -> list[dict]:
    entries = _read_entries(_gate_decisions_file())
    if since is None:
        return entries
    cutoff = datetime.now(timezone.utc) - since
    out: list[dict] = []
    for e in entries:
        ts_raw = e.get("ts")
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw)
        except ValueError:
            continue
        if ts >= cutoff:
            out.append(e)
    return out


def read_context_inferences(*, since: timedelta | None = None) -> list[dict]:
    entries = _read_entries(_context_inferences_file())
    if since is None:
        return entries
    cutoff = datetime.now(timezone.utc) - since
    out: list[dict] = []
    for e in entries:
        ts_raw = e.get("ts")
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw)
        except ValueError:
            continue
        if ts >= cutoff:
            out.append(e)
    return out
