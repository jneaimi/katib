"""Phase 2 Day 13 — scripts/log_request.py subprocess tests."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CMD = ["uv", "run", "scripts/log_request.py"]


@pytest.fixture
def memdir(tmp_path):
    env = {**os.environ, "KATIB_MEMORY_DIR": str(tmp_path)}
    return tmp_path, env


def _run(env, *args, expect_rc=None):
    result = subprocess.run(
        [*CMD, *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if expect_rc is not None:
        assert result.returncode == expect_rc, (
            f"unexpected rc={result.returncode}\n"
            f"  cmd: {' '.join(args)}\n"
            f"  stdout: {result.stdout!r}\n"
            f"  stderr: {result.stderr!r}"
        )
    return result


def _run_json(env, *args, expect_rc=None):
    result = _run(env, "--json", *args, expect_rc=expect_rc)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"stdout not JSON:\n"
            f"  cmd: {' '.join(args)}\n"
            f"  stdout: {result.stdout!r}\n"
            f"  stderr: {result.stderr!r}\n"
            f"  error: {e}"
        )


# ================================================================ help / errors


def test_help_exits_zero(memdir):
    _, env = memdir
    result = _run(env, "--help", expect_rc=0)
    assert "component" in result.stdout
    assert "recipe" in result.stdout


def test_missing_subcommand_fails(memdir):
    _, env = memdir
    result = _run(env)
    assert result.returncode == 2


# ================================================================ component


def test_component_logs_entry(memdir):
    path, env = memdir
    _run(
        env,
        "component",
        "--requested", "chart-pie",
        "--closest", "chart-donut",
        "--intent", "breakdown with center label",
        "--reason", "donut center is opinionated",
        expect_rc=0,
    )
    log_path = path / "component-requests.jsonl"
    assert log_path.exists()
    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["requested"] == "chart-pie"
    assert entry["kind"] == "component"


def test_component_requires_name(memdir):
    _, env = memdir
    result = _run(
        env, "component",
        "--intent", "x", "--reason", "y",
        expect_rc=1,
    )
    assert "at least one" in result.stderr


def test_component_json_output(memdir):
    path, env = memdir
    payload = _run_json(
        env,
        "component",
        "--requested", "mytest",
        "--intent", "x",
        "--reason", "y",
        expect_rc=0,
    )
    assert payload["requested"] == "mytest"
    assert payload["schema_version"] == 1


# ================================================================ recipe


def test_recipe_logs_entry(memdir):
    path, env = memdir
    _run(
        env,
        "recipe",
        "--requested", "white-paper",
        "--intent", "long-form policy piece",
        "--reason", "no existing recipe",
        expect_rc=0,
    )
    assert (path / "recipe-requests.jsonl").exists()


# ================================================================ list / count / search


def test_list_returns_empty_when_no_log(memdir):
    _, env = memdir
    result = _run(env, "list", "component", expect_rc=0)
    assert "no component" in result.stdout.lower()


def test_list_shows_entries(memdir):
    path, env = memdir
    for i in range(3):
        _run(
            env, "component",
            "--requested", f"widget-{i}",
            "--intent", "x", "--reason", "y",
            expect_rc=0,
        )
    result = _run(env, "list", "component", expect_rc=0)
    assert "widget-0" in result.stdout
    assert "widget-2" in result.stdout


def test_count_returns_number(memdir):
    _, env = memdir
    for _ in range(3):
        _run(
            env, "component",
            "--requested", "mywidget",
            "--intent", "x", "--reason", "y",
            expect_rc=0,
        )
    result = _run(env, "count", "component", "mywidget", expect_rc=0)
    assert "3" in result.stdout


def test_count_json(memdir):
    _, env = memdir
    payload = _run_json(env, "count", "component", "nonexistent", expect_rc=0)
    assert payload["count"] == 0


def test_search_finds_match(memdir):
    _, env = memdir
    _run(
        env, "component",
        "--requested", "alpha",
        "--intent", "bilingual footer",
        "--reason", "y",
        expect_rc=0,
    )
    _run(
        env, "component",
        "--requested", "beta",
        "--intent", "chart thing",
        "--reason", "y",
        expect_rc=0,
    )
    result = _run(env, "search", "component", "bilingual", expect_rc=0)
    assert "alpha" in result.stdout
    assert "beta" not in result.stdout


# ================================================================ JSON contract regression


def test_json_contract_always_valid(memdir):
    """Every exit path in --json mode must emit parseable JSON."""
    _, env = memdir
    invocations = [
        ["list", "component"],
        ["count", "component", "anything"],
        ["search", "component", "anything"],
    ]
    for args in invocations:
        result = _run(env, "--json", *args)
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"invocation {args} produced non-JSON stdout:\n"
                f"  stdout: {result.stdout!r}\n"
                f"  error: {e}"
            )
