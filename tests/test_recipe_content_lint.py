"""Phase 2 post-close-out — content_lint wired into recipe validate/register.

Covers the three gating modes introduced by Open Item #2:
    default          warnings surface, don't block register
    --strict         warnings promoted to errors, block register
    --no-content-lint  skip the check entirely (legacy override)

Also: KATIB_STRICT_LINT env var is a CI-friendly synonym for --strict.
"""
from __future__ import annotations

import json
import os
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
    name = "pytest-content-lint-recipe"
    ops._cleanup_recipe(name)
    yield name
    ops._cleanup_recipe(name)


def _inject_slop(path: Path) -> None:
    """Append a description with a banned opener + vague declarative to the YAML."""
    import yaml as yaml_mod
    data = yaml_mod.safe_load(path.read_text(encoding="utf-8"))
    # Overwrite description with deliberate slop (the rules are phrase-based
    # so they'll match regardless of YAML key context after extract_text strips).
    data["description"] = "In today's world, the results are amazing. Let me be clear: this works."
    path.write_text(
        yaml_mod.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


# ================================================================ library-level


def test_validate_clean_recipe_no_content_issues():
    """Existing tutorial.yaml should pass clean under default + strict."""
    v = ops.validate_recipe_full("tutorial")
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


def test_validate_clean_recipe_strict_still_clean():
    v = ops.validate_recipe_full("tutorial", strict=True)
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


def test_validate_dirty_recipe_surfaces_warnings(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    v = ops.validate_recipe_full(throwaway_name)
    content_issues = [i for i in v.issues if i.category == "content"]
    assert len(content_issues) >= 2   # banned-opener + vague-declarative at minimum
    # Default: ALL content findings surface as warnings, regardless of
    # content_lint's internal severity. Never blocks register.
    assert all(i.severity == "warning" for i in content_issues)
    # Internal severity preserved in the message for human review
    messages = [i.message for i in content_issues]
    assert any("error" in m or "warn" in m for m in messages)


def test_validate_dirty_recipe_strict_promotes_to_error(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    v = ops.validate_recipe_full(throwaway_name, strict=True)
    content_errs = [i for i in v.issues if i.category == "content" and i.severity == "error"]
    assert len(content_errs) >= 2
    # strict + content errors → ok() is False
    assert not v.ok


def test_validate_dirty_recipe_no_content_lint_skips(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    v = ops.validate_recipe_full(throwaway_name, content_lint=False)
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


def test_register_refuses_on_strict_with_content_errors(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    with pytest.raises(ValueError, match="validation error"):
        ops.register_recipe(throwaway_name, strict=True)


def test_register_passes_on_default_with_content_warnings(throwaway_name):
    """Default mode: content warnings are advisory; register still succeeds."""
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    # Should NOT raise — warnings don't block register
    result = ops.register_recipe(throwaway_name)
    assert result.capabilities_regenerated


def test_share_refuses_on_strict_with_content_errors(throwaway_name, tmp_path):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    with pytest.raises(ValueError, match="validation error"):
        ops.bundle_share_recipe(throwaway_name, out_dir=tmp_path, strict=True)


# ================================================================ env var


def test_env_var_strict_lint_promotes(throwaway_name, monkeypatch):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    monkeypatch.setenv("KATIB_STRICT_LINT", "1")
    v = ops.validate_recipe_full(throwaway_name)
    content_errs = [i for i in v.issues if i.category == "content" and i.severity == "error"]
    assert len(content_errs) >= 2


# ================================================================ lint_all


def test_lint_all_existing_recipes_clean_default():
    results = ops.lint_all_recipes()
    for r in results:
        assert r.ok, f"{r.recipe} broke lint_all default: {[i.message for i in r.errors]}"


def test_lint_all_existing_recipes_clean_strict():
    """All 7 shipped recipes must pass even under --strict. If any rule addition
    ever breaks this, the rule addition needs a commit re-auditing existing
    content before it lands."""
    results = ops.lint_all_recipes(strict=True)
    for r in results:
        assert r.ok, f"{r.recipe} broke lint_all strict: {[i.message for i in r.errors]}"


# ================================================================ CLI subprocess


def test_cli_validate_default_tutorial_passes():
    result = subprocess.run(
        [*CMD, "validate", "tutorial"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0


def test_cli_validate_strict_dirty_fails(throwaway_name):
    # Create dirty recipe via CLI then strict-validate
    subprocess.run(
        [*CMD, "new", throwaway_name, "--languages", "en", "--keywords", "smoke"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=30,
    )
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    result = subprocess.run(
        [*CMD, "validate", throwaway_name, "--strict"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 1
    assert "content" in result.stdout.lower() or "banned-opener" in result.stdout.lower()


def test_cli_validate_no_content_lint_dirty_passes(throwaway_name):
    subprocess.run(
        [*CMD, "new", throwaway_name, "--languages", "en", "--keywords", "smoke"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=30,
    )
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    result = subprocess.run(
        [*CMD, "validate", throwaway_name, "--no-content-lint"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0


def test_cli_register_strict_dirty_refuses(throwaway_name):
    subprocess.run(
        [*CMD, "new", throwaway_name, "--languages", "en", "--keywords", "smoke"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=30,
    )
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    result = subprocess.run(
        [*CMD, "register", throwaway_name, "--strict"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 1


def test_cli_lint_all_strict_still_passes():
    """Production regression guard: lint --all --strict must stay green on
    the shipped tree. If this ever fails, content was committed in a rule-
    adding commit without re-auditing existing recipes."""
    result = subprocess.run(
        [*CMD, "lint", "--all", "--strict"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0


def test_cli_validate_json_shape_includes_content_category(throwaway_name):
    subprocess.run(
        [*CMD, "new", throwaway_name, "--languages", "en", "--keywords", "smoke"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=30,
    )
    _inject_slop(ops.RECIPES_DIR / f"{throwaway_name}.yaml")

    result = subprocess.run(
        [*CMD, "--json", "validate", throwaway_name],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    payload = json.loads(result.stdout)
    categories = {i["category"] for i in payload["issues"]}
    assert "content" in categories
