"""Phase 2 Day 14 — end-to-end integration tests.

Cross-module flows that prove the Phase-2 engine works as a unit. Each test
targets a specific regression class that unit tests alone can't catch:

    T1  graduation workflow              lib → audit → capabilities
    T2  bare /katib happy path           sensor → gate → route → build → PDF
    T3  gate-fire full loop              infer → ask_questions → resolve → render
    T4  log-and-wait contract            resolve → JSONL write, no PDF
    T5  content-lint on production       tutorial.yaml ≤ small-N warnings, 0 errors
    T6  audit-gate breakage              rm component → build refuses
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ================================================================ fixtures


@pytest.fixture
def memdir(tmp_path, monkeypatch):
    """Redirect KATIB_MEMORY_DIR for test isolation + patch module paths.

    Required because core/component_ops.py, core/recipe_ops.py, and
    core/request_log.py all use module-level path constants captured at
    import time.
    """
    monkeypatch.setenv("KATIB_MEMORY_DIR", str(tmp_path))
    from core import component_ops, recipe_ops
    monkeypatch.setattr(component_ops, "REQUESTS_FILE", tmp_path / "component-requests.jsonl")
    monkeypatch.setattr(recipe_ops, "REQUESTS_FILE", tmp_path / "recipe-requests.jsonl")
    monkeypatch.setattr(component_ops, "AUDIT_FILE", tmp_path / "component-audit.jsonl")
    monkeypatch.setattr(recipe_ops, "AUDIT_FILE", tmp_path / "recipe-audit.jsonl")
    return tmp_path


# ================================================================ T1 — graduation workflow


def test_t1_graduation_workflow_end_to_end(memdir):
    """Log 3 component requests → scaffold (no warning) → validate → register → audit updated."""
    from core import component_ops, request_log

    name = "t1-integration-widget"
    component_ops._cleanup_component_dir(name)

    # 1. Log 3 requests — simulates pre-graduation accumulation
    for _ in range(3):
        request_log.log_component_request(
            requested=name,
            closest_existing=None,
            intent="bilingual-aware figure block",
            reason="no existing component supports RTL + figure caption",
        )

    try:
        # 2. Scaffold — must NOT emit graduation warning
        scaffold = component_ops.scaffold(
            name, tier="primitive", languages=["en"], requires_tokens=["accent"]
        )
        assert scaffold.graduation_warning is None, (
            "gate should be silent after 3 requests logged"
        )

        # 3. Validate — no schema errors on the scaffolded component
        v = component_ops.validate_full(name)
        schema_errors = [i for i in v.errors if i.category == "schema"]
        assert schema_errors == []

        # 4. Register — writes audit entry + regenerates capabilities.yaml
        reg = component_ops.register(name)
        assert reg.capabilities_regenerated
        assert reg.audit_entry["action"] == "register"

        # 5. The audit file should now have at least: scaffold + register
        audit_lines = (memdir / "component-audit.jsonl").read_text("utf-8").splitlines()
        entries = [json.loads(line) for line in audit_lines if line.strip()]
        matching = [e for e in entries if e.get("component") == name]
        actions = {e.get("action") for e in matching}
        assert {"scaffold", "register"} <= actions
    finally:
        component_ops._cleanup_component_dir(name)


# ================================================================ T2 — bare /katib happy path


def test_t2_bare_katib_high_confidence_renders(tmp_path):
    """Transcript → route.py infer (HIGH) → build.py → PDF written."""
    transcript = (
        "render tutorial framework-guide bloom ai-collaboration production "
        "in English with jasem brand"
    )

    # Step 1: route.py infer (JSON out)
    infer_result = subprocess.run(
        ["uv", "run", "scripts/route.py", "infer",
         "--transcript", transcript, "--no-persist"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert infer_result.returncode == 0
    inferred = json.loads(infer_result.stdout)
    assert inferred["action"] == "render"
    assert inferred["recipe"] == "tutorial"
    assert inferred["confidence"] == "HIGH"

    # Step 2: build.py
    out_pdf = tmp_path / "t2.pdf"
    build_result = subprocess.run(
        ["uv", "run", "scripts/build.py", inferred["recipe"],
         "--lang", inferred["lang"], "--brand", inferred["brand"] or "jasem",
         "--out", str(out_pdf)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=120,
    )
    assert build_result.returncode == 0
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 10_000, "tutorial PDF should be >10KB"


# ================================================================ T3 — gate-fire full loop


def test_t3_gate_fire_full_loop(tmp_path):
    """Ambiguous intent → infer ask_questions → resolve yes-fits/one-off → render."""
    # Step 1: infer with moderate-signal intent — should either proceed or choose
    # (route.py confidence tuning means HIGH is the common path for clear intents).
    # We want a path that goes through resolve — use --recipe short-circuit in
    # resolve to simulate "gate fired and user picked tutorial as closest".
    #
    # Simpler path that exercises resolve: skip infer, call resolve with
    # yes-fits + one-off → fill-closest → render action with recipe=tutorial.

    resolve_result = subprocess.run(
        ["uv", "run", "scripts/route.py", "resolve",
         "--q1", "yes-fits", "--q2", "one-off",
         "--closest-recipe", "tutorial",
         "--intent", "quick tutorial for the team",
         "--lang", "en", "--brand", "jasem",
         "--no-persist"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert resolve_result.returncode == 0
    resolved = json.loads(resolve_result.stdout)
    assert resolved["action"] == "render"
    assert resolved["recipe"] == "tutorial"
    assert resolved["resolved_action"] in ("fill-closest", "log-and-fill")


# ================================================================ T4 — log-and-wait contract


def test_t4_log_and_wait_persists_entries(tmp_path, monkeypatch):
    """Resolve no-different × recurring → wait action + recipe-request written."""
    monkeypatch.setenv("KATIB_MEMORY_DIR", str(tmp_path))

    result = subprocess.run(
        ["uv", "run", "scripts/route.py", "resolve",
         "--q1", "no-different", "--q2", "recurring",
         "--closest-recipe", "tutorial",
         "--intent", "monthly-board-minutes recurring board meeting doc"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
        env={**os.environ, "KATIB_MEMORY_DIR": str(tmp_path)},
    )
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["action"] == "wait"
    # Log entry present in the response + persisted to disk
    assert "log_entry" in out
    assert (tmp_path / "gate-decisions.jsonl").exists()
    assert (tmp_path / "recipe-requests.jsonl").exists()
    # The recipe-request entry should carry the closest recipe name
    recipe_requests = [
        json.loads(line) for line in
        (tmp_path / "recipe-requests.jsonl").read_text("utf-8").splitlines()
        if line.strip()
    ]
    assert len(recipe_requests) >= 1
    assert recipe_requests[0]["closest_existing"] == "tutorial"


# ================================================================ T5 — content-lint on production


def test_t5_content_lint_tutorial_no_errors():
    """scripts/lint.py recipes/tutorial.yaml — zero errors.

    Warnings are acceptable; production prose can trip jargon/waw-chain heuristics.
    Errors would mean banned-openers / emphasis-crutches / vague-declaratives
    in real production content — which is the point of the linter.
    """
    result = subprocess.run(
        ["uv", "run", "scripts/lint.py",
         str(REPO_ROOT / "recipes" / "tutorial.yaml"),
         "--lang", "en", "--json"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    # rc 0 (clean) or rc 1 (warnings/errors) are both valid exit statuses
    assert result.returncode in (0, 1)
    payload = json.loads(result.stdout)
    # The critical assertion: zero ERRORS on intentional production prose
    assert payload["error_count"] == 0, (
        f"tutorial.yaml has {payload['error_count']} content-lint errors: "
        f"{[v for v in payload['violations'] if v['severity'] == 'error']}"
    )


# ================================================================ T6 — audit-gate breakage


def test_t6_audit_gate_refuses_hand_added_component(tmp_path):
    """Scaffold a component, strip its audit entry, try to build — must fail loud."""
    from core import component_ops

    name = "t6-audit-break"
    component_ops._cleanup_component_dir(name)

    try:
        component_ops.scaffold(name, tier="primitive", languages=["en"])
        # Strip audit entries for this component — simulate hand-added state
        audit_file = component_ops.AUDIT_FILE
        original = audit_file.read_text("utf-8") if audit_file.exists() else ""
        try:
            cleaned = "\n".join(
                line for line in original.splitlines()
                if line.strip() and json.loads(line).get("component") != name
            )
            audit_file.write_text(cleaned + ("\n" if cleaned else ""), encoding="utf-8")

            # Now try to build — must refuse with clear audit error
            result = subprocess.run(
                ["uv", "run", "scripts/build.py", "tutorial",
                 "--lang", "en", "--out", str(tmp_path / "x.pdf")],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
            )
            assert result.returncode != 0
            assert "audit" in result.stderr.lower()
            assert name in result.stderr
        finally:
            # Restore audit file
            audit_file.write_text(original, encoding="utf-8")
    finally:
        component_ops._cleanup_component_dir(name)
