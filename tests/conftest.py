"""Shared pytest fixtures."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def clean_env(monkeypatch):
    for var in ("KATIB_OUTPUT_ROOT", "KATIB_BRANDS_DIR", "GEMINI_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


@pytest.fixture
def isolated_user_dirs(tmp_path, monkeypatch):
    """Redirect user-tier writes to `tmp_path` subdirs for the duration of a
    test. Opt-in (not autouse) — existing tests rely on their own cleanup
    patterns; new tests that exercise Phase-2 user-tier writes should request
    this fixture to avoid writing to the real `~/.katib/` tree.

    Sets both the env vars (for subprocess-spawned builds that read them
    fresh) and the module-level constants on `recipe_ops` / `component_ops`
    (captured at import time, so env-only redirect wouldn't take effect
    inside the same Python process).
    """
    recipes = tmp_path / "recipes"
    memory = tmp_path / "memory"
    components = tmp_path / "components"
    brands = tmp_path / "brands"
    for d in (recipes, memory, components, brands):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("KATIB_RECIPES_DIR", str(recipes))
    monkeypatch.setenv("KATIB_MEMORY_DIR", str(memory))
    monkeypatch.setenv("KATIB_COMPONENTS_DIR", str(components))
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(brands))

    from core import component_ops, recipe_ops
    # RECIPES_DIR / COMPONENTS_DIR stay bundled (the real repo paths);
    # USER_RECIPES_DIR / USER_COMPONENTS_DIR are the tiers that redirect.
    monkeypatch.setattr(recipe_ops, "USER_RECIPES_DIR", recipes)
    monkeypatch.setattr(recipe_ops, "MEMORY_DIR", memory)
    monkeypatch.setattr(recipe_ops, "AUDIT_FILE", memory / "recipe-audit.jsonl")
    monkeypatch.setattr(recipe_ops, "REQUESTS_FILE", memory / "recipe-requests.jsonl")
    monkeypatch.setattr(component_ops, "USER_COMPONENTS_DIR", components)
    monkeypatch.setattr(component_ops, "MEMORY_DIR", memory)
    monkeypatch.setattr(component_ops, "AUDIT_FILE", memory / "component-audit.jsonl")
    monkeypatch.setattr(component_ops, "REQUESTS_FILE", memory / "component-requests.jsonl")

    # build.py captures its own module-level constants at import time.
    # In-process tests that call build.main() need the redirects too;
    # subprocess tests pick up the env vars directly and don't need this.
    import scripts.build as build_mod
    monkeypatch.setattr(build_mod, "AUDIT_FILE", memory / "component-audit.jsonl")
    monkeypatch.setattr(build_mod, "RECIPE_AUDIT_FILE", memory / "recipe-audit.jsonl")

    return tmp_path
