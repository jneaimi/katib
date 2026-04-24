"""Phase 2 Day 12 — scripts/recipe.py CLI subprocess tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import recipe_ops as ops  # noqa: E402

CMD = ["uv", "run", "scripts/recipe.py"]


@pytest.fixture
def throwaway_name():
    name = "pytest-recipe-cli"
    ops._cleanup_recipe(name)
    yield name
    ops._cleanup_recipe(name)


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


def _run_json(*args: str, expect_rc: int | None = None):
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


def test_help():
    result = _run("--help", expect_rc=0)
    assert "new" in result.stdout
    assert "validate" in result.stdout


def test_missing_subcommand_fails():
    result = _run()
    assert result.returncode == 2


def test_unknown_recipe_human():
    result = _run("validate", "does-not-exist-xyz", expect_rc=1)
    assert "ERROR" in result.stderr


def test_unknown_recipe_json():
    payload = _run_json("validate", "does-not-exist-xyz", expect_rc=1)
    assert payload["action"] == "error"


# ================================================================ new


def test_new_scaffolds_recipe(throwaway_name):
    result = _run(
        "new", throwaway_name, "--languages", "en", "--keywords", "smoke,test",
        expect_rc=0,
    )
    assert "Scaffolded" in result.stdout
    rpath = ops.RECIPES_DIR / f"{throwaway_name}.yaml"
    assert rpath.exists()


def test_new_json_output(throwaway_name):
    payload = _run_json(
        "new", throwaway_name, "--languages", "en", "--keywords", "smoke",
        expect_rc=0,
    )
    assert payload["recipe"] == throwaway_name
    assert payload["namespace"] == "katib"


def test_new_rejects_existing_recipe():
    result = _run("new", "tutorial", expect_rc=1)
    assert "already exists" in result.stderr


def test_new_target_pages_parsing(throwaway_name):
    result = _run(
        "new", throwaway_name,
        "--languages", "en", "--keywords", "smoke",
        "--target-pages", "3,8", "--page-limit", "10",
        expect_rc=0,
    )
    import yaml
    data = yaml.safe_load((ops.RECIPES_DIR / f"{throwaway_name}.yaml").read_text())
    assert data["target_pages"] == [3, 8]
    assert data["page_limit"] == 10


# ================================================================ validate


def test_validate_existing_recipe():
    result = _run("validate", "tutorial", expect_rc=0)
    assert "tutorial" in result.stdout


def test_validate_json_shape():
    payload = _run_json("validate", "tutorial", expect_rc=0)
    assert set(payload.keys()) == {"recipe", "path", "ok", "issues"}


def test_validate_detects_bad_recipe(throwaway_name):
    _run("new", throwaway_name, "--languages", "en", "--keywords", "smoke", expect_rc=0)
    # Inject a bad component reference
    import yaml
    rpath = ops.RECIPES_DIR / f"{throwaway_name}.yaml"
    data = yaml.safe_load(rpath.read_text())
    data["sections"].append({"component": "nonexistent-xyz"})
    rpath.write_text(yaml.safe_dump(data, sort_keys=False))
    result = _run("validate", throwaway_name, expect_rc=1)
    assert "nonexistent-xyz" in result.stdout


# ================================================================ test (render)


def test_test_renders_recipe(throwaway_name):
    _run("new", throwaway_name, "--languages", "en", "--keywords", "smoke", expect_rc=0)
    result = _run("test", throwaway_name, expect_rc=0)
    assert ".pdf" in result.stdout


def test_test_json_shape(throwaway_name):
    _run("new", throwaway_name, "--languages", "en", "--keywords", "smoke", expect_rc=0)
    payload = _run_json("test", throwaway_name, expect_rc=0)
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["pdf_bytes"] > 500


def test_test_all_langs_flag(throwaway_name):
    _run("new", throwaway_name, "--languages", "en,ar", "--keywords", "smoke", expect_rc=0)
    payload = _run_json("test", throwaway_name, "--all-langs", expect_rc=0)
    langs = {r["lang"] for r in payload}
    assert langs == {"en", "ar"}


# ================================================================ register


def test_register_chain(throwaway_name):
    _run("new", throwaway_name, "--languages", "en", "--keywords", "smoke", expect_rc=0)
    result = _run("register", throwaway_name, expect_rc=0)
    assert "registered" in result.stdout
    caps = (REPO_ROOT / "capabilities.yaml").read_text("utf-8")
    assert throwaway_name in caps


# ================================================================ share


def test_share_produces_bundle(throwaway_name):
    _run("new", throwaway_name, "--languages", "en", "--keywords", "smoke", expect_rc=0)
    result = _run("share", throwaway_name, expect_rc=0)
    assert "bundled" in result.stdout
    assert ".tar.gz" in result.stdout


# ================================================================ lint


def test_lint_all():
    result = _run("lint", "--all", expect_rc=0)
    assert "tutorial" in result.stdout


def test_lint_json_shape():
    payload = _run_json("lint", "--all", expect_rc=0)
    assert isinstance(payload, list)
    assert len(payload) >= 7


def test_lint_requires_all_flag():
    result = _run("lint", expect_rc=2)
    assert "--all" in result.stderr


# ================================================================ JSON contract regression


def test_json_contract_always_valid(throwaway_name):
    """Every exit path of scripts/recipe.py must emit parseable JSON in --json mode."""
    invocations = [
        ["validate", "tutorial"],
        ["validate", "does-not-exist-abc"],
        ["lint", "--all"],
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
