"""Phase 2 Day 11 — scripts/component.py CLI subprocess tests.

Mirrors test_route.py's JSON-contract regression-guard pattern. Every verb
is exercised both in human mode (exit code + stderr message) and --json mode
(stdout parses, structured error shape).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import component_ops as ops   # noqa: E402

CMD = ["uv", "run", "scripts/component.py"]


@pytest.fixture
def throwaway_name():
    name = "pytest-cli-ephemeral"
    ops._cleanup_component_dir(name)
    yield name
    ops._cleanup_component_dir(name)


def _run(*args: str, expect_rc: int | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [*CMD, *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60
    )
    if expect_rc is not None:
        assert result.returncode == expect_rc, (
            f"unexpected rc={result.returncode}\n"
            f"  cmd: {' '.join(args)}\n"
            f"  stdout: {result.stdout!r}\n"
            f"  stderr: {result.stderr!r}"
        )
    return result


def _run_json(*args: str, expect_rc: int | None = None) -> dict | list:
    """Run with --json and parse stdout as JSON. Fails the test if not parseable."""
    result = _run("--json", *args, expect_rc=expect_rc)
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


def test_help_exits_zero():
    result = _run("--help", expect_rc=0)
    assert "new" in result.stdout
    assert "validate" in result.stdout


def test_missing_subcommand_fails():
    result = _run()
    assert result.returncode == 2


def test_unknown_component_human_mode():
    result = _run("validate", "does-not-exist-xyz", expect_rc=1)
    assert "ERROR" in result.stderr
    assert "does-not-exist-xyz" in result.stderr


def test_unknown_component_json_mode():
    payload = _run_json("validate", "does-not-exist-xyz", expect_rc=1)
    assert payload["action"] == "error"
    assert "does-not-exist-xyz" in payload["message"]


# ================================================================ new


def test_new_scaffolds_and_emits_human_output(throwaway_name):
    result = _run(
        "new", throwaway_name, "--tier", "primitive", "--languages", "en",
        expect_rc=0,
    )
    assert "Scaffolded" in result.stdout
    assert throwaway_name in result.stdout
    cdir = REPO_ROOT / "components" / "primitives" / throwaway_name
    assert cdir.exists()


def test_new_json_output(throwaway_name):
    payload = _run_json(
        "new", throwaway_name, "--tier", "primitive", "--languages", "en",
        expect_rc=0,
    )
    assert payload["component"] == throwaway_name
    assert payload["tier"] == "primitive"
    assert "files_created" in payload
    assert len(payload["files_created"]) >= 3


def test_new_rejects_existing_name():
    result = _run("new", "eyebrow", "--tier", "primitive", expect_rc=1)
    assert "already exists" in result.stderr


def test_new_requires_tier():
    result = _run("new", "some-component")
    assert result.returncode == 2
    assert "--tier" in result.stderr


# ================================================================ validate


def test_validate_existing_component_passes():
    result = _run("validate", "eyebrow", expect_rc=0)
    assert "eyebrow" in result.stdout


def test_validate_json_shape():
    payload = _run_json("validate", "eyebrow", expect_rc=0)
    assert set(payload.keys()) == {"component", "tier", "path", "ok", "issues"}
    assert payload["component"] == "eyebrow"
    assert isinstance(payload["issues"], list)


# ================================================================ test


def test_test_renders_isolated_pdf(throwaway_name):
    # Scaffold first via CLI, then render
    _run("new", throwaway_name, "--tier", "primitive", "--languages", "en", expect_rc=0)
    result = _run("test", throwaway_name, expect_rc=0)
    assert "en" in result.stdout
    assert ".pdf" in result.stdout


def test_test_json_returns_array(throwaway_name):
    _run("new", throwaway_name, "--tier", "primitive", "--languages", "en", expect_rc=0)
    payload = _run_json("test", throwaway_name, expect_rc=0)
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["lang"] == "en"
    assert payload[0]["pdf_bytes"] > 100
    assert payload[0]["weasyprint_warnings"] == 0


# ================================================================ register


def test_register_chain(throwaway_name):
    _run("new", throwaway_name, "--tier", "primitive", "--languages", "en", expect_rc=0)
    result = _run("register", throwaway_name, expect_rc=0)
    assert "registered" in result.stdout

    # capabilities should now contain the component
    caps = (REPO_ROOT / "capabilities.yaml").read_text("utf-8")
    assert throwaway_name in caps


def test_register_refuses_broken_component(throwaway_name):
    _run("new", throwaway_name, "--tier", "primitive", "--languages", "en,ar", expect_rc=0)
    (REPO_ROOT / "components" / "primitives" / throwaway_name / "ar.html").unlink()
    result = _run("register", throwaway_name, expect_rc=1)
    assert "validation error" in result.stderr or "validation error" in result.stdout


# ================================================================ share


def test_share_produces_bundle(throwaway_name, tmp_path):
    _run("new", throwaway_name, "--tier", "primitive", "--languages", "en", expect_rc=0)
    result = _run("share", throwaway_name, expect_rc=0)
    assert "bundled" in result.stdout
    assert ".tar.gz" in result.stdout


# ================================================================ lint


def test_lint_all_smoke():
    result = _run("lint", "--all", expect_rc=0)
    # Every existing component passes (warnings only)
    assert "ok" in result.stdout or "✓" in result.stdout


def test_lint_json_shape():
    payload = _run_json("lint", "--all", expect_rc=0)
    assert isinstance(payload, list)
    assert len(payload) >= 20
    for r in payload:
        assert "component" in r
        assert "ok" in r


def test_lint_requires_all_flag():
    result = _run("lint", expect_rc=2)
    assert "--all" in result.stderr


# ================================================================ JSON contract regression


def test_json_contract_always_valid(throwaway_name):
    """Every exit path of the CLI must produce parseable JSON in --json mode.

    Mirrors the route.py regression guard.
    """
    invocations = [
        ["validate", "eyebrow"],               # success
        ["validate", "does-not-exist-abc"],    # operational error
        ["lint", "--all"],                      # success list
    ]
    for args in invocations:
        result = _run("--json", *args)
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"invocation {args} produced non-JSON stdout:\n"
                f"  stdout: {result.stdout!r}\n"
                f"  error: {e}"
            )
