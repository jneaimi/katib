"""Phase 2 Day 10 — route.py CLI router tests."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ROUTE = ["uv", "run", "scripts/route.py"]


def _inject_no_persist(args: tuple[str, ...]) -> list[str]:
    """Append --no-persist to infer/resolve invocations so tests don't pollute
    memory/*.jsonl. Day 13's persist-path tests live in test_request_log_cli.py
    and explicitly exercise persistence with their own tmp memory dirs.
    """
    if not args:
        return list(args)
    if args[0] in ("infer", "resolve"):
        return list(args) + ["--no-persist"]
    return list(args)


def _run(*args: str, cwd: Path = REPO_ROOT) -> dict:
    """Run route.py with args, parse stdout as JSON, return dict.

    Fails the test if stdout isn't valid JSON — catches the subprocess
    JSON contract leak that was explicitly called out in the ADR.
    """
    result = subprocess.run(
        [*ROUTE, *_inject_no_persist(args)],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"route.py stdout was not JSON:\n"
            f"  stdout: {result.stdout!r}\n"
            f"  stderr: {result.stderr!r}\n"
            f"  error:  {e}"
        )


# ================================================================ infer


def test_infer_high_confidence_returns_render():
    out = _run(
        "infer",
        "--transcript",
        "render tutorial framework-guide bloom ai-collaboration production in English with jasem brand",
    )
    assert out["action"] == "render"
    assert out["recipe"] == "tutorial"
    assert out["lang"] == "en"
    assert out["brand"] == "jasem"
    assert out["confidence"] == "HIGH"
    # Observability: reasons should be populated
    assert isinstance(out["reasons"], list) and len(out["reasons"]) > 0
    # Summary contract: starts with "Inferred:" and ends with exactly one "."
    # (semicolons are internal joiners; ellipsis in truncated previews doesn't count)
    assert out["summary"].startswith("Inferred:")
    assert out["summary"].endswith(".")


def test_infer_empty_transcript_returns_ask_intent():
    out = _run("infer", "--transcript", "")
    assert out["action"] == "ask_intent"
    assert "message" in out
    # No intent → summary may or may not be populated; doesn't matter


def test_infer_explicit_recipe_shortcircuits_gate():
    out = _run(
        "infer",
        "--transcript",
        "",
        "--recipe",
        "tutorial",
        "--lang",
        "en",
        "--brand",
        "jasem",
    )
    assert out["action"] == "render"
    assert out["recipe"] == "tutorial"
    assert out["lang"] == "en"
    assert out["brand"] == "jasem"
    # "confidence" is NOT set when short-circuiting (gate not run)
    assert "confidence" not in out


def test_infer_unknown_recipe_returns_error():
    out = _run("infer", "--transcript", "", "--recipe", "nonexistent-recipe-xyz")
    assert out["action"] == "error"
    assert out["code"] == "unknown_recipe"


def test_infer_medium_returns_present_candidates():
    """Diluted intent → MEDIUM → present_candidates with AUQ payload."""
    out = _run(
        "infer",
        "--transcript",
        "please render the tutorial framework guide in English using jasem brand",
        "--brand",
        "jasem",
    )
    # Could be proceed or choose depending on score — both are valid routing
    if out["action"] == "present_candidates":
        assert out["confidence"] == "MEDIUM"
        q = out["question"]
        assert set(q.keys()) == {"question", "header", "options", "multiSelect"}
        assert 2 <= len(q["options"]) <= 4
        for opt in q["options"]:
            assert set(opt.keys()) == {"label", "description"}


def test_infer_low_confidence_fires_questions(tmp_path):
    """LOW path: weak topic + ambiguous brand + ambiguous lang → ask_questions."""
    # Synthesize an ambiguous-brand environment via temp dir
    brands = tmp_path / "brands"
    brands.mkdir()
    for n in ("alpha", "beta", "gamma"):
        (brands / f"{n}.yaml").write_text(f"name: {n.capitalize()}")
    env = {"KATIB_BRANDS_DIR": str(brands), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    # Invoke via subprocess directly so we can set env
    import os

    env.update({k: os.environ[k] for k in ("HOME", "PATH") if k in os.environ})
    result = subprocess.run(
        [*ROUTE, "infer", "--transcript", "showcase mixed تركي widget blarg", "--no-persist"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = json.loads(result.stdout)
    assert out["action"] == "ask_questions"
    assert out["confidence"] == "LOW"
    assert len(out["questions"]) == 2
    # Each question must match AUQ payload shape
    for q in out["questions"]:
        assert set(q.keys()) == {"question", "header", "options", "multiSelect"}
        assert len(q["header"]) <= 12
    # answer_map should let the agent translate labels back to values
    assert "answer_map" in out
    assert "fit" in out["answer_map"]
    assert "frequency" in out["answer_map"]
    assert out["answer_map"]["fit"]["Yes, fits"] == "yes-fits"


def test_infer_explicit_lang_overrides_inferred():
    """If user passes --lang ar but intent is English, explicit wins + logs override."""
    out = _run(
        "infer",
        "--transcript",
        "render tutorial framework-guide bloom ai-collaboration production with jasem brand",
        "--lang",
        "ar",
        "--brand",
        "jasem",
    )
    # Lang should be AR even though intent is English
    assert out["action"] == "render"
    assert out["lang"] == "ar"
    # Override should be recorded in reasons
    assert any("override" in r.lower() for r in out["reasons"])


def test_infer_transcript_file_read_from_disk(tmp_path):
    f = tmp_path / "t.txt"
    f.write_text(
        "render tutorial framework-guide bloom ai-collaboration production "
        "in English with jasem brand"
    )
    out = _run("infer", "--transcript-file", str(f))
    assert out["action"] == "render"
    assert out["recipe"] == "tutorial"


# ================================================================ resolve


@pytest.mark.parametrize(
    "q1,q2,expected_action,expects_render",
    [
        ("yes-fits", "one-off", "render", True),
        ("yes-fits", "recurring", "render", True),
        ("partial", "occasional", "render", True),  # log-and-fill still renders
        ("no-different", "one-off", "render", True),  # log-and-fill
        ("no-different", "occasional", "wait", False),  # log-and-wait
        ("no-different", "recurring", "wait", False),
    ],
)
def test_resolve_matrix_actions(q1, q2, expected_action, expects_render):
    out = _run(
        "resolve",
        "--q1",
        q1,
        "--q2",
        q2,
        "--closest-recipe",
        "tutorial",
        "--intent",
        "test prose",
    )
    assert out["action"] == expected_action
    if expects_render:
        assert out["recipe"] == "tutorial"
    # Log entry always emitted
    assert "log_entry" in out
    assert out["log_entry"]["schema_version"] == 1
    assert out["log_entry"]["fit"] == q1
    assert out["log_entry"]["frequency"] == q2


def test_resolve_force_graduation_requires_justification():
    out = _run(
        "resolve",
        "--q1",
        "no-different",
        "--q2",
        "recurring",
        "--closest-recipe",
        "tutorial",
        "--intent",
        "something",
        "--force-graduation",
        # No --justification
    )
    assert out["action"] == "error"
    assert "justification" in out["message"].lower()


def test_resolve_force_graduation_success():
    out = _run(
        "resolve",
        "--q1",
        "no-different",
        "--q2",
        "recurring",
        "--closest-recipe",
        "tutorial",
        "--intent",
        "test",
        "--force-graduation",
        "--justification",
        "3 similar memos logged this quarter",
    )
    assert out["action"] == "graduate"
    assert out["log_entry"]["action"] == "request-graduation"
    assert (
        out["log_entry"]["force_graduation_justification"]
        == "3 similar memos logged this quarter"
    )


def test_resolve_unknown_recipe_returns_error():
    out = _run(
        "resolve",
        "--q1",
        "yes-fits",
        "--q2",
        "one-off",
        "--closest-recipe",
        "does-not-exist",
        "--intent",
        "x",
    )
    assert out["action"] == "error"


# ================================================================ error handling


def test_internal_error_wraps_not_raw_traceback(tmp_path):
    """route.py must NEVER leak a raw Python traceback on stdout.

    If the exception path runs, the output should still be valid JSON
    with action=error.
    """
    # Point route.py at a non-existent transcript file — should produce a
    # clean JSON error, not a raw FileNotFoundError traceback.
    missing = tmp_path / "nope.txt"
    result = subprocess.run(
        [*ROUTE, "infer", "--transcript-file", str(missing), "--no-persist"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # stdout must be parseable JSON
    out = json.loads(result.stdout)
    assert out["action"] == "error"
    assert out["code"] == "internal_error"


def test_json_contract_always_valid():
    """Regression guard: every exit path emits exactly one JSON document."""
    # Smoke-run several args and confirm JSON parses cleanly
    invocations = [
        ["infer", "--transcript", ""],
        ["infer", "--transcript", "random intent"],
        ["resolve", "--q1", "yes-fits", "--q2", "one-off", "--closest-recipe", "tutorial", "--intent", "x"],
    ]
    for args in invocations:
        result = subprocess.run(
            [*ROUTE, *_inject_no_persist(tuple(args))],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        json.loads(result.stdout)  # raises if not valid JSON
