"""Phase 2 — verify user-tier writes (audit + memory) actually land outside REPO_ROOT.

Phase 2 scope (narrow): only audit and graduation-gate logs move to the user
tier. Recipe YAMLs and component scaffold files STILL land under bundled
REPO_ROOT — scaffold-write migration is Phase 3, which must be shipped
alongside the two-tier read wiring (lint_all_recipes, compose.load_recipe)
to avoid breaking read paths.

What these tests prove:
- scaffold_recipe/scaffold's audit entry lands in `user_memory_dir()`
- `request_log.memory_dir()` agrees with `tokens.user_memory_dir()` (no divergence)
- env-var overrides route audit correctly
- `_display_path` handles user-tier paths without ValueError

Uses the `isolated_user_dirs` conftest fixture so no writes touch the real
`~/.katib/` tree on the developer's machine.
"""
from __future__ import annotations

from pathlib import Path

from core import component_ops, recipe_ops, request_log
from core import tokens


# ---------------------------------------------------------------- T-U1: recipe audit lands in user memory


def test_recipe_audit_entry_writes_to_user_memory(isolated_user_dirs):
    """scaffold_recipe appends an audit row. After Phase 2 that row lives
    under `user_memory_dir()`, not under REPO_ROOT/memory."""
    name = "phase2-recipe-audit-smoke"
    # Because RECIPES_DIR is redirected by the fixture, we can scaffold
    # freely without touching the bundled recipes dir.
    recipe_ops.scaffold_recipe(
        name=name,
        namespace="user",
        languages=["en"],
        description="Audit smoke — user namespace bypasses graduation gate.",
        domain_hint=None,
        target_pages=[1, 1],
        page_limit=1,
        when=None,
        keywords=[],
    )
    audit_file = recipe_ops.AUDIT_FILE
    assert audit_file.exists()
    assert str(audit_file).startswith(str(isolated_user_dirs / "memory"))
    assert name in audit_file.read_text(encoding="utf-8")


# ---------------------------------------------------------------- T-U2: component audit lands in user memory


def test_component_audit_entry_writes_to_user_memory(isolated_user_dirs):
    """scaffold (component) appends an audit row. After Phase 2 that row
    lives under `user_memory_dir()`. The component files themselves still
    land under bundled COMPONENTS_DIR — that's Phase 3's job."""
    name = "phase2-component-audit-smoke"
    component_ops._cleanup_component_dir(name)
    try:
        component_ops.scaffold(
            name=name,
            tier="primitive",
            namespace="user",
            languages=["en"],
            description="Audit smoke — component scaffold stays bundled, audit moves.",
            force=False,
            justification=None,
        )
        audit_file = component_ops.AUDIT_FILE
        assert audit_file.exists()
        assert str(audit_file).startswith(str(isolated_user_dirs / "memory"))
        assert name in audit_file.read_text(encoding="utf-8")
    finally:
        component_ops._cleanup_component_dir(name)


# ---------------------------------------------------------------- T-U3: env override for MEMORY_DIR


def test_env_override_routes_memory_dir(tmp_path, monkeypatch):
    """KATIB_MEMORY_DIR overrides the audit file location. Exercises the
    env → helper → module-attr path that the isolated_user_dirs fixture
    automates."""
    custom_memory = tmp_path / "my-memory"
    custom_memory.mkdir()
    monkeypatch.setenv("KATIB_MEMORY_DIR", str(custom_memory))
    monkeypatch.setattr(recipe_ops, "MEMORY_DIR", custom_memory)
    monkeypatch.setattr(recipe_ops, "AUDIT_FILE", custom_memory / "recipe-audit.jsonl")
    monkeypatch.setattr(recipe_ops, "REQUESTS_FILE", custom_memory / "recipe-requests.jsonl")

    # Isolate recipe scaffold target too so we don't touch bundled recipes/
    custom_recipes = tmp_path / "custom-recipes"
    custom_recipes.mkdir()
    monkeypatch.setenv("KATIB_RECIPES_DIR", str(custom_recipes))
    monkeypatch.setattr(recipe_ops, "RECIPES_DIR", custom_recipes)

    name = "phase2-env-override-smoke"
    recipe_ops.scaffold_recipe(
        name=name,
        namespace="user",
        languages=["en"],
        description="env override smoke.",
        domain_hint=None,
        target_pages=[1, 1],
        page_limit=1,
        when=None,
        keywords=[],
    )
    assert (custom_memory / "recipe-audit.jsonl").exists()


# ---------------------------------------------------------------- T-U4: audit write doesn't pollute bundled memory


def test_scaffold_audit_leaves_bundled_memory_untouched(isolated_user_dirs):
    """CI guard: with isolation active, REPO_ROOT/memory/recipe-audit.jsonl
    receives no new entries for the test recipe."""
    bundled_audit = recipe_ops.REPO_ROOT / "memory" / "recipe-audit.jsonl"
    before = bundled_audit.read_text(encoding="utf-8") if bundled_audit.exists() else ""

    name = "phase2-bundled-audit-noleak"
    recipe_ops.scaffold_recipe(
        name=name,
        namespace="user",
        languages=["en"],
        description="Leak-guard.",
        domain_hint=None,
        target_pages=[1, 1],
        page_limit=1,
        when=None,
        keywords=[],
    )
    after = bundled_audit.read_text(encoding="utf-8") if bundled_audit.exists() else ""
    assert before == after, f"test polluted bundled audit: {name} leaked into REPO_ROOT/memory"


# ---------------------------------------------------------------- T-U5: request_log agrees with tokens


def test_request_log_memory_dir_agrees_with_tokens(monkeypatch):
    """Phase 2 unified: request_log.memory_dir() delegates to tokens.user_memory_dir().
    With env unset, both must return ~/.katib/memory. With env set, both must
    return the override."""
    monkeypatch.delenv("KATIB_MEMORY_DIR", raising=False)
    assert request_log.memory_dir() == tokens.user_memory_dir()
    assert request_log.memory_dir() == Path.home() / ".katib" / "memory"

    monkeypatch.setenv("KATIB_MEMORY_DIR", "/tmp/katib-test-memory-xyz")
    assert request_log.memory_dir() == tokens.user_memory_dir()
    assert request_log.memory_dir() == Path("/tmp/katib-test-memory-xyz")


# ---------------------------------------------------------------- T-U6: _display_path handles user-tier paths


def test_relative_to_display_handles_user_tier_paths():
    """`_display_path` helper returns str(p) for paths outside REPO_ROOT,
    which prevents the `.relative_to(REPO_ROOT)` ValueError regression
    that would fire once Phase 3 moves scaffold writes to user tier."""
    bundled = recipe_ops.REPO_ROOT / "recipes" / "x.yaml"
    user_tier = Path.home() / ".katib" / "recipes" / "x.yaml"
    assert recipe_ops._display_path(bundled) == "recipes/x.yaml"
    # User-tier path is outside REPO_ROOT — must not raise
    rendered = recipe_ops._display_path(user_tier)
    assert rendered == str(user_tier)


# ---------------------------------------------------------------- T-U7: module constants at import time point to user memory


def test_ops_memory_constants_default_to_user_tier(monkeypatch):
    """Sanity check on the Phase-2 constant shuffle. With no env var,
    the module constant must resolve to `user_memory_dir()`. This is the
    one assertion that a regression to `REPO_ROOT / "memory"` would
    instantly catch."""
    monkeypatch.delenv("KATIB_MEMORY_DIR", raising=False)
    # Re-import to re-evaluate module-level constants
    import importlib
    from core import recipe_ops as ro
    from core import component_ops as co
    ro = importlib.reload(ro)
    co = importlib.reload(co)
    assert ro.MEMORY_DIR == tokens.user_memory_dir()
    assert co.MEMORY_DIR == tokens.user_memory_dir()
    assert ro.AUDIT_FILE.parent == tokens.user_memory_dir()
    assert co.AUDIT_FILE.parent == tokens.user_memory_dir()
