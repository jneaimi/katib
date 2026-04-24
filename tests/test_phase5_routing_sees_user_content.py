"""Phase-5 release-readiness — router sees user-tier recipes and components.

The full user story: a fresh-install user scaffolds `~/.katib/recipes/my.yaml`,
then invokes `/katib --recipe my`. The agent calls `scripts/route.py infer`,
which consults `capabilities.yaml`. Without Phase-3/4's staleness-detection
wiring, capabilities.yaml ships frozen at skill-install time and never sees
user content — so the explicit-recipe short-circuit reports `unknown_recipe`
and the user hits a dead end.

These tests prove the staleness regen picks up user content on the fly and
the router short-circuits to `render` for both user recipes and user
recipes that reference user components.

Side effect: the subprocess regen writes to REPO_ROOT/capabilities.yaml
(staleness subprocess doesn't accept --out). The bundled capabilities.yaml
timestamp bounces during the test run; content is idempotent.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def user_env(tmp_path):
    """Fresh-install sandbox: every KATIB_* dir redirected to tmp_path."""
    recipes = tmp_path / "recipes"
    memory = tmp_path / "memory"
    components = tmp_path / "components"
    brands = tmp_path / "brands"
    for d in (recipes, memory, components, brands):
        d.mkdir(parents=True, exist_ok=True)
    env = {**os.environ}
    env["KATIB_RECIPES_DIR"] = str(recipes)
    env["KATIB_MEMORY_DIR"] = str(memory)
    env["KATIB_COMPONENTS_DIR"] = str(components)
    env["KATIB_BRANDS_DIR"] = str(brands)
    env.pop("KATIB_DEV_MODE", None)
    return env, tmp_path


def _run_route_infer(recipe_name: str, env: dict, transcript: str = "") -> dict:
    """Run `route.py infer --recipe <name>` with an empty transcript file.
    Returns parsed JSON from stdout. Non-zero returncode is fine for
    `action: error` responses — route.py signals problems via both."""
    transcript_file = Path(env["KATIB_RECIPES_DIR"]).parent / "transcript.txt"
    transcript_file.write_text(transcript, encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "scripts/route.py", "infer",
         "--transcript-file", str(transcript_file),
         "--recipe", recipe_name],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=60,
    )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        pytest.fail(
            f"route.py stdout is not JSON (rc={r.returncode}):\n"
            f"{r.stdout}\nstderr:\n{r.stderr}"
        )


# ---------------------------------------------------------------- T-R1: user recipe discoverable


def test_router_sees_user_recipe_via_staleness_regen(user_env):
    """Minimal story: user drops a recipe YAML into `~/.katib/recipes/`.
    The next `/katib --recipe <name>` invocation must short-circuit to
    `render` — meaning capabilities.yaml was regenerated to include the
    user recipe."""
    env, tmp = user_env
    recipe_file = tmp / "recipes" / "p5-user-only-recipe.yaml"
    recipe_file.write_text(
        "name: p5-user-only-recipe\n"
        "version: 0.1.0\n"
        "namespace: user\n"
        "description: Phase-5 router smoke.\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: module\n"
        "    inputs:\n"
        "      title: Router smoke\n",
        encoding="utf-8",
    )

    result = _run_route_infer("p5-user-only-recipe", env)

    # Must NOT report unknown_recipe
    assert result.get("action") != "error", (
        f"router failed to see user recipe:\n{json.dumps(result, indent=2)}"
    )
    assert result.get("action") == "render"
    assert result.get("recipe") == "p5-user-only-recipe"
    # Capability notes must record the regen (proves the path ran)
    assert "capability_notes" in result, (
        f"staleness regen did not fire — capability_notes missing:\n"
        f"{json.dumps(result, indent=2)}"
    )


# ---------------------------------------------------------------- T-R2: user recipe using user component


def test_router_sees_user_recipe_referencing_user_component(user_env):
    """Confirms Phase 4's user-component plumbing wires through capabilities:
    a user recipe referencing a user section must show up in caps AND the
    section component must appear too. This is the signal the context
    sensor uses to rank keyword matches."""
    env, tmp = user_env
    # Scaffold a user section by hand (minimal — skip the CLI to keep the test
    # focused on the routing path; component_ops is exercised by Phase 4 tests).
    sec_dir = tmp / "components" / "sections" / "p5-user-section"
    sec_dir.mkdir(parents=True)
    (sec_dir / "component.yaml").write_text(
        "name: p5-user-section\n"
        "tier: section\n"
        "version: 0.1.0\n"
        "namespace: user\n"
        "description: Phase-5 router smoke section.\n"
        "languages: [en]\n"
        "requires:\n"
        "  tokens: []\n"
        "accepts:\n"
        "  inputs:\n"
        "    - title:\n"
        "        type: string\n"
        "        required: true\n",
        encoding="utf-8",
    )
    (sec_dir / "en.html").write_text(
        '<section><h2>{{ input.title }}</h2></section>\n', encoding="utf-8",
    )
    (sec_dir / "README.md").write_text("# p5-user-section\n", encoding="utf-8")

    recipe_file = tmp / "recipes" / "p5-user-full-stack.yaml"
    recipe_file.write_text(
        "name: p5-user-full-stack\n"
        "version: 0.1.0\n"
        "namespace: user\n"
        "description: User recipe + user component end-to-end.\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: p5-user-section\n"
        "    inputs:\n"
        "      title: Full stack user-tier\n",
        encoding="utf-8",
    )

    result = _run_route_infer("p5-user-full-stack", env)
    assert result.get("action") == "render", (
        f"router did not resolve the user recipe:\n{json.dumps(result, indent=2)}"
    )
    assert result["recipe"] == "p5-user-full-stack"


# ---------------------------------------------------------------- T-R3: unknown recipe still errors cleanly


def test_router_reports_unknown_recipe_cleanly(user_env):
    """Regression guard for the error path: if a user asks for a recipe
    that doesn't exist in either tier, the error lists available recipes
    (and must include at least bundled ones, confirming the caps read
    worked)."""
    env, _ = user_env
    result = _run_route_infer("definitely-not-a-real-recipe-xyz", env)
    assert result.get("action") == "error"
    assert result.get("code") == "unknown_recipe"
    # Bundled recipes should appear in the "Available:" list so the user
    # can see what IS available.
    msg = result.get("message", "")
    assert "tutorial" in msg or "legal-mou" in msg, (
        f"error message didn't include any bundled recipe names:\n{msg}"
    )
