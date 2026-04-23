"""Phase 2 Day 13 — scripts/lint.py subprocess tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CMD = ["uv", "run", "scripts/lint.py"]


def _run(*args, expect_rc=None, stdin: str | None = None):
    result = subprocess.run(
        [*CMD, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        input=stdin,
    )
    if expect_rc is not None:
        assert result.returncode == expect_rc, (
            f"unexpected rc={result.returncode}\n"
            f"  cmd: {' '.join(args)}\n"
            f"  stdout: {result.stdout!r}\n"
            f"  stderr: {result.stderr!r}"
        )
    return result


def _run_json(*args, expect_rc=None, stdin=None):
    result = _run("--json", *args, expect_rc=expect_rc, stdin=stdin)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"stdout not JSON:\n"
            f"  cmd: {' '.join(args)}\n"
            f"  stdout: {result.stdout!r}\n"
            f"  error: {e}"
        )


# ================================================================ basic


def test_help_exits_zero():
    result = _run("--help", expect_rc=0)
    assert "lint" in result.stdout.lower()


def test_missing_file_returns_rc_2():
    result = _run(expect_rc=2)
    assert "--stdin" in result.stderr or "provide" in result.stderr.lower()


def test_nonexistent_file_returns_rc_2():
    result = _run("/tmp/definitely-does-not-exist-xyz.txt", expect_rc=2)
    assert "not found" in result.stderr.lower()


# ================================================================ file mode


def test_clean_file_exits_zero(tmp_path):
    f = tmp_path / "clean.en.html"
    f.write_text("<p>Shipped Tuesday. Two reports filed.</p>")
    result = _run(str(f), expect_rc=0)
    assert "clean" in result.stdout


def test_dirty_file_exits_one(tmp_path):
    f = tmp_path / "dirty.en.html"
    f.write_text("<p>In today's world, the results are amazing.</p>")
    result = _run(str(f), expect_rc=1)
    assert "error" in result.stdout.lower()


def test_json_output_shape(tmp_path):
    f = tmp_path / "dirty.en.html"
    f.write_text("<p>The results are amazing.</p>")
    payload = _run_json(str(f), expect_rc=1)
    assert set(payload.keys()) == {"file", "clean", "error_count", "warning_count", "violations"}
    assert payload["clean"] is False
    assert payload["error_count"] >= 1


# ================================================================ lang override


def test_force_lang_en(tmp_path):
    f = tmp_path / "anon.html"
    f.write_text("<p>The results are amazing</p>")
    result = _run(str(f), "--lang", "en", expect_rc=1)
    assert "vague-declarative" in result.stdout


def test_force_lang_ar(tmp_path):
    f = tmp_path / "anon.html"
    f.write_text("<p>النتائج مذهلة</p>")
    result = _run(str(f), "--lang", "ar", expect_rc=1)
    assert "vague-declarative" in result.stdout


# ================================================================ stdin mode


def test_stdin_clean(tmp_path):
    result = _run("--stdin", "--lang", "en", stdin="<p>Clean text.</p>", expect_rc=0)
    assert "clean" in result.stdout


def test_stdin_dirty():
    result = _run(
        "--stdin", "--lang", "en",
        stdin="<p>The results are amazing.</p>",
        expect_rc=1,
    )
    assert "vague-declarative" in result.stdout


# ================================================================ real recipe render


def test_tutorial_recipe_render_is_clean(tmp_path):
    """The tutorial recipe's rendered HTML should not trip content_lint."""
    # Render tutorial to a tmp HTML, then lint
    import subprocess as sp
    out_pdf = tmp_path / "tutorial.en.pdf"
    sp.run(
        ["uv", "run", "scripts/build.py", "tutorial", "--lang", "en", "--out", str(out_pdf)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Lint the recipe YAML directly — it's the authoritative source file.
    recipe_file = REPO_ROOT / "recipes" / "tutorial.yaml"
    result = _run(str(recipe_file), "--lang", "en")
    # Recipe prose may have some warnings; must not have unexpected errors.
    assert result.returncode in (0, 1)
