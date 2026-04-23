"""Phase 2 Day 13 — graduation-gate activation proof.

Verifies that once Day-13's request-log writer populates
`memory/component-requests.jsonl` (or `recipe-requests.jsonl`) with ≥ 3
matching entries, the Day-11/12 scaffolder's graduation warning goes silent.

This is the "integration check" that proves the Day-11/12 readers and the
Day-13 writer agree on the same schema.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def memdir(tmp_path, monkeypatch):
    """Redirect KATIB_MEMORY_DIR so we don't pollute real memory/."""
    monkeypatch.setenv("KATIB_MEMORY_DIR", str(tmp_path))
    # Both component_ops and request_log read from the overridden path.
    # Reload the modules so their module-level REQUESTS_FILE / AUDIT_FILE
    # paths (captured at import time as constants) get refreshed... actually
    # for component_ops and recipe_ops these are repo-root-anchored constants,
    # not env-driven. So instead we patch the REQUESTS_FILE attribute.
    from core import component_ops, recipe_ops
    monkeypatch.setattr(
        component_ops, "REQUESTS_FILE", tmp_path / "component-requests.jsonl"
    )
    monkeypatch.setattr(
        recipe_ops, "REQUESTS_FILE", tmp_path / "recipe-requests.jsonl"
    )
    # Redirect AUDIT_FILE + dispatch to tmp too, so scaffold doesn't pollute
    # the real audit log.
    monkeypatch.setattr(
        component_ops, "AUDIT_FILE", tmp_path / "component-audit.jsonl"
    )
    monkeypatch.setattr(
        recipe_ops, "AUDIT_FILE", tmp_path / "recipe-audit.jsonl"
    )
    return tmp_path


def _cleanup_component_if_exists(name: str) -> None:
    from core import component_ops
    component_ops._cleanup_component_dir(name)


def _cleanup_recipe_if_exists(name: str) -> None:
    from core import recipe_ops
    recipe_ops._cleanup_recipe(name)


# ================================================================ component activation


def test_component_scaffold_warns_when_log_empty(memdir):
    """Baseline — matches Day-11 behavior from before Day 13."""
    from core import component_ops

    name = "activation-proof-a"
    try:
        result = component_ops.scaffold(name, tier="primitive", languages=["en"])
        assert result.graduation_warning is not None
        assert "not yet active" in result.graduation_warning.lower()
    finally:
        _cleanup_component_if_exists(name)


def test_component_scaffold_warns_when_fewer_than_three(memdir):
    """2 logged entries → still gated."""
    from core import component_ops, request_log

    name = "activation-proof-b"
    # Seed 2 requests
    for _ in range(2):
        request_log.log_component_request(
            requested=name,
            closest_existing=None,
            intent="test",
            reason="test",
        )
    try:
        result = component_ops.scaffold(name, tier="primitive", languages=["en"])
        assert result.graduation_warning is not None
        # Message should now reflect the actual count (not the "log missing" variant)
        assert "2" in result.graduation_warning or "request" in result.graduation_warning.lower()
    finally:
        _cleanup_component_if_exists(name)


def test_component_scaffold_silent_at_threshold(memdir):
    """3+ logged entries → graduation gate satisfied; no warning."""
    from core import component_ops, request_log

    name = "activation-proof-c"
    for _ in range(3):
        request_log.log_component_request(
            requested=name,
            closest_existing=None,
            intent="test",
            reason="test",
        )
    try:
        result = component_ops.scaffold(name, tier="primitive", languages=["en"])
        assert result.graduation_warning is None
    finally:
        _cleanup_component_if_exists(name)


def test_component_scaffold_counts_closest_existing_matches(memdir):
    """Requests logged with closest_existing=X also count toward X's threshold."""
    from core import component_ops, request_log

    name = "activation-proof-d"
    # 3 requests where the user asked for something else but closest was our name
    for _ in range(3):
        request_log.log_component_request(
            requested="different-name",
            closest_existing=name,
            intent="test",
            reason="test",
        )
    try:
        result = component_ops.scaffold(name, tier="primitive", languages=["en"])
        assert result.graduation_warning is None
    finally:
        _cleanup_component_if_exists(name)


# ================================================================ recipe activation


def test_recipe_scaffold_silent_at_threshold(memdir):
    """Same contract for recipes."""
    from core import recipe_ops, request_log

    name = "activation-proof-recipe"
    for _ in range(3):
        request_log.log_recipe_request(
            requested=name,
            closest_existing=None,
            intent="test",
            reason="test",
        )
    try:
        result = recipe_ops.scaffold_recipe(
            name, languages=["en"], keywords=["smoke"]
        )
        assert result.graduation_warning is None
    finally:
        _cleanup_recipe_if_exists(name)


def test_recipe_scaffold_warns_when_log_empty(memdir):
    from core import recipe_ops

    name = "activation-proof-recipe-empty"
    try:
        result = recipe_ops.scaffold_recipe(
            name, languages=["en"], keywords=["smoke"]
        )
        assert result.graduation_warning is not None
    finally:
        _cleanup_recipe_if_exists(name)
