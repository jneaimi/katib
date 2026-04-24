"""Phase 3 — end-to-end subprocess test: fresh-install user scaffolds + renders a recipe.

This test is the standing regression guard against Phase 2's bug (build.py's
audit file paths were hardcoded to REPO_ROOT/memory/, so any user who
scaffolded a recipe hit an audit-gate orphan error on their first render).

Simulates a fresh-install user:
    - `KATIB_*_DIR` env vars set to tmp_path subdirs (no real ~/.katib writes)
    - Run `scripts/recipe.py new <name> --namespace user` as a subprocess
    - Run `scripts/build.py <name> --lang en` as a subprocess (NO --skip-audit-check)
    - Assert the PDF is produced end-to-end

If this test is passing, a real user on a fresh install can scaffold
and render a custom recipe. If it's failing, something in the tier
plumbing is broken — and unit tests won't catch it because they import
the module (capturing constants at import time) or patch them.

Uses subprocess so env vars and module-level constants are captured at
a FRESH Python start, matching real user behavior.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def user_env(tmp_path, monkeypatch):
    """Simulate a fresh-install user: all KATIB_* dirs under tmp_path.

    Returns a dict suitable for `subprocess.run(..., env=...)`.
    """
    recipes = tmp_path / "recipes"
    memory = tmp_path / "memory"
    components = tmp_path / "components"
    brands = tmp_path / "brands"
    output = tmp_path / "output"
    for d in (recipes, memory, components, brands, output):
        d.mkdir(parents=True, exist_ok=True)

    env = {**os.environ}
    env["KATIB_RECIPES_DIR"] = str(recipes)
    env["KATIB_MEMORY_DIR"] = str(memory)
    env["KATIB_COMPONENTS_DIR"] = str(components)
    env["KATIB_BRANDS_DIR"] = str(brands)
    env["KATIB_OUTPUT_ROOT"] = str(output)
    # Pop vars that might leak from the dev shell
    env.pop("KATIB_DEV_MODE", None)
    return env, tmp_path


def _run(cmd: list[str], env: dict, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=120)


def test_fresh_install_user_can_scaffold_and_render(user_env):
    """Full E2E: scaffold a custom recipe, render it via default audit-gated path.

    This test fails before Phase 3 Task 1 (build.py audit-path regression fix)
    and passes after all Phase 3 tasks are complete.
    """
    env, tmp = user_env
    name = "p3-e2e-fresh-install-smoke"

    # 1. Scaffold a recipe via the public CLI (simulating `katib recipe new`).
    r = _run(
        [sys.executable, "scripts/recipe.py", "new", name,
         "--namespace", "user",
         "--description", "End-to-end smoke — scaffold + render from fresh install."],
        env=env,
    )
    assert r.returncode == 0, f"scaffold failed: stdout={r.stdout!r} stderr={r.stderr!r}"

    # 2. The recipe file must land in the user tier.
    user_recipe = tmp / "recipes" / f"{name}.yaml"
    assert user_recipe.exists(), (
        f"recipe was not written to user tier. Expected at {user_recipe}.\n"
        f"recipe.py stdout: {r.stdout}"
    )
    # And NOT in bundled.
    bundled_recipe = REPO_ROOT / "recipes" / f"{name}.yaml"
    assert not bundled_recipe.exists(), (
        f"scaffold polluted bundled recipes/ — file leaked to {bundled_recipe}"
    )

    # 3. Audit entry must land in user memory (Phase 2 guarantee).
    user_audit = tmp / "memory" / "recipe-audit.jsonl"
    assert user_audit.exists()
    audit_content = user_audit.read_text(encoding="utf-8")
    assert name in audit_content

    # 4. Replace the scaffolded stub with a minimal recipe that uses only
    #    bundled components (module) — keeps the test independent of the
    #    scaffold template's contents.
    user_recipe.write_text(
        "name: " + name + "\n"
        "version: 0.1.0\n"
        "namespace: user\n"
        "languages: [en]\n"
        "description: E2E smoke recipe.\n"
        "sections:\n"
        "  - component: module\n"
        "    inputs:\n"
        "      title: Fresh-install E2E\n"
        "      body: This document proves a user-scaffolded recipe renders end-to-end.\n",
        encoding="utf-8",
    )

    # 5. Render it via build.py WITHOUT --skip-audit-check. This is the
    #    full audit-gated path a real user would hit.
    out_pdf = tmp / "output.pdf"
    r = _run(
        [sys.executable, "scripts/build.py", name,
         "--lang", "en", "--out", str(out_pdf)],
        env=env,
    )
    assert r.returncode == 0, (
        f"build failed — this is the Phase 2 regression symptom.\n"
        f"stdout: {r.stdout}\n"
        f"stderr: {r.stderr}"
    )
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
    pdf = PdfReader(str(out_pdf))
    assert len(pdf.pages) >= 1
    text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    assert "Fresh-install E2E" in text


def test_fresh_install_error_when_recipe_not_found_names_both_tiers(user_env):
    """When a recipe is referenced that exists in neither tier, the error
    message must name both paths the engine tried. Users with no source
    repo have no other way to discover where the skill looked.
    """
    env, tmp = user_env
    r = _run(
        [sys.executable, "scripts/build.py", "definitely-does-not-exist-xyz",
         "--lang", "en", "--skip-audit-check",
         "--out", str(tmp / "nope.pdf")],
        env=env,
    )
    assert r.returncode == 1
    combined = (r.stdout + r.stderr).lower()
    # The error should name BOTH paths tried (user tier + bundled tier).
    assert "not found" in combined
    # User-tier path should appear
    assert str(tmp / "recipes").lower() in combined or ".katib/recipes" in combined
    # Bundled-tier path should appear
    assert "recipes/" in combined or str(REPO_ROOT / "recipes").lower() in combined


def test_fresh_install_scaffold_refuses_to_shadow_bundled_recipe(user_env):
    """A user trying to scaffold a recipe with the same name as a bundled
    one (e.g., `tutorial`) must be refused with a clear message, not
    silently shadow the bundled recipe.
    """
    env, tmp = user_env
    # `tutorial` is a bundled recipe in this repo
    r = _run(
        [sys.executable, "scripts/recipe.py", "new", "tutorial",
         "--namespace", "user"],
        env=env,
    )
    assert r.returncode != 0, (
        f"scaffold should have refused to shadow bundled 'tutorial'. "
        f"stdout: {r.stdout} stderr: {r.stderr}"
    )
    combined = (r.stdout + r.stderr).lower()
    assert "already exists" in combined or "bundled" in combined
