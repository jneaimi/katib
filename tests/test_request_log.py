"""Phase 2 Day 13 — core/request_log.py unit tests."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import request_log as rl  # noqa: E402


@pytest.fixture
def memdir(tmp_path, monkeypatch):
    """Redirect KATIB_MEMORY_DIR to a tmp path for isolation."""
    monkeypatch.setenv("KATIB_MEMORY_DIR", str(tmp_path))
    return tmp_path


# ================================================================ memory_dir


def test_memory_dir_default():
    # With no env, resolves to the user-tier memory dir (Phase 2 unified it
    # with tokens.user_memory_dir() — was REPO_ROOT/memory pre-Phase-2).
    os.environ.pop("KATIB_MEMORY_DIR", None)
    assert rl.memory_dir() == Path.home() / ".katib" / "memory"


def test_memory_dir_env_override(memdir):
    assert rl.memory_dir() == memdir


# ================================================================ component requests


def test_log_component_request_writes_jsonl(memdir):
    entry = rl.log_component_request(
        requested="chart-pie",
        closest_existing="chart-donut",
        intent="Percentage breakdown with center label",
        reason="donut center is opinionated",
    )
    assert entry["kind"] == "component"
    assert entry["schema_version"] == rl.REQUEST_SCHEMA_VERSION
    path = memdir / "component-requests.jsonl"
    assert path.exists()
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["requested"] == "chart-pie"


def test_log_component_request_requires_name(memdir):
    with pytest.raises(ValueError, match="at least one"):
        rl.log_component_request(
            requested=None, closest_existing=None, intent="x", reason="y"
        )


def test_log_recipe_request_writes_jsonl(memdir):
    entry = rl.log_recipe_request(
        requested="white-paper",
        closest_existing=None,
        intent="thought leadership on GCC AI policy",
        reason="no existing recipe for long-form op-ed",
    )
    path = memdir / "recipe-requests.jsonl"
    assert path.exists()
    assert entry["kind"] == "recipe"


def test_multiple_appends_preserve_order(memdir):
    for i in range(5):
        rl.log_component_request(
            requested=f"comp-{i}",
            closest_existing=None,
            intent=f"intent {i}",
            reason="r",
        )
    entries = rl.read_requests("component")
    assert [e["requested"] for e in entries] == [f"comp-{i}" for i in range(5)]


# ================================================================ count/read/search


def test_count_requests_matches_requested_or_closest(memdir):
    rl.log_component_request(
        requested="chart-pie", closest_existing="chart-donut", intent="x", reason="y"
    )
    rl.log_component_request(
        requested=None, closest_existing="chart-pie", intent="x", reason="y"
    )
    rl.log_component_request(
        requested="other", closest_existing="something-else", intent="x", reason="y"
    )
    assert rl.count_requests("component", "chart-pie") == 2
    assert rl.count_requests("component", "other") == 1
    assert rl.count_requests("component", "nonexistent") == 0


def test_read_requests_since_filters_old(memdir):
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    # Write an old entry (20 days ago)
    old_ts = (now - timedelta(days=20)).isoformat(timespec="seconds")
    rl.log_component_request(
        requested="old", closest_existing=None, intent="x", reason="y", ts=old_ts
    )
    # Write a fresh entry
    rl.log_component_request(
        requested="new", closest_existing=None, intent="x", reason="y"
    )
    recent = rl.read_requests("component", since=timedelta(days=7))
    names = [e["requested"] for e in recent]
    assert "new" in names
    assert "old" not in names


def test_search_requests_matches_intent(memdir):
    rl.log_component_request(
        requested="A", closest_existing=None, intent="bilingual table layout", reason="y"
    )
    rl.log_component_request(
        requested="B", closest_existing=None, intent="chart renderer", reason="y"
    )
    matches = rl.search_requests("component", "bilingual")
    assert len(matches) == 1
    assert matches[0]["requested"] == "A"


def test_search_requests_case_insensitive(memdir):
    rl.log_component_request(
        requested="A", closest_existing=None, intent="Bilingual Table Layout", reason="y"
    )
    assert len(rl.search_requests("component", "TABLE")) == 1


# ================================================================ parse_since


def test_parse_since_days():
    from datetime import timedelta

    assert rl.parse_since("7d") == timedelta(days=7)


def test_parse_since_weeks():
    from datetime import timedelta

    assert rl.parse_since("2w") == timedelta(days=14)


def test_parse_since_hours():
    from datetime import timedelta

    assert rl.parse_since("12h") == timedelta(hours=12)


def test_parse_since_none():
    assert rl.parse_since(None) is None


def test_parse_since_invalid():
    with pytest.raises(ValueError):
        rl.parse_since("7x")


# ================================================================ gate + context inference writers


def test_log_gate_decision_writes(memdir):
    rl.log_gate_decision({
        "ts": "2026-04-23T14:00:00Z",
        "request": "test intent",
        "action": "fill-closest",
        "routed_to": "tutorial",
    })
    path = memdir / "gate-decisions.jsonl"
    assert path.exists()
    entry = json.loads(path.read_text().splitlines()[0])
    assert entry["routed_to"] == "tutorial"
    assert entry["schema_version"] == rl.GATE_LOG_SCHEMA_VERSION


def test_log_context_inference_writes(memdir):
    rl.log_context_inference({
        "ts": "2026-04-23T14:00:00Z",
        "transcript_sample": "x",
        "inferred": {"intent_preview": "y"},
    })
    path = memdir / "context-inferences.jsonl"
    assert path.exists()
    entry = json.loads(path.read_text().splitlines()[0])
    assert entry["schema_version"] == rl.CONTEXT_LOG_SCHEMA_VERSION


def test_read_gate_decisions_returns_list(memdir):
    for i in range(3):
        rl.log_gate_decision({"request": f"intent-{i}", "action": "fill-closest"})
    entries = rl.read_gate_decisions()
    assert len(entries) == 3


def test_read_context_inferences_returns_list(memdir):
    for i in range(3):
        rl.log_context_inference({"transcript_sample": f"x-{i}"})
    entries = rl.read_context_inferences()
    assert len(entries) == 3


# ================================================================ schema version lock


def test_request_schema_version_is_one():
    """Locked contract — bumping this requires coordinated reader/writer updates."""
    assert rl.REQUEST_SCHEMA_VERSION == 1


def test_gate_log_schema_version_is_one():
    assert rl.GATE_LOG_SCHEMA_VERSION == 1


def test_context_log_schema_version_is_one():
    assert rl.CONTEXT_LOG_SCHEMA_VERSION == 1


# ================================================================ concurrent append (smoke — not a stress test)


def test_concurrent_appends_preserve_lines(memdir):
    """Write lines from multiple threads; each must appear intact.

    Not a stress test — just catches obvious corruption (truncated lines,
    interleaved bytes). POSIX atomic-append guarantees hold for writes
    well under 4KB.
    """
    import concurrent.futures

    def write_one(i: int) -> None:
        rl.log_component_request(
            requested=f"concurrent-{i}",
            closest_existing=None,
            intent=f"intent {i}",
            reason="r",
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(write_one, range(20)))

    entries = rl.read_requests("component")
    assert len(entries) == 20
    names = {e["requested"] for e in entries}
    assert names == {f"concurrent-{i}" for i in range(20)}
