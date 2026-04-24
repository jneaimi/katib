"""Phase 4 — end-to-end regression guard for user-tier components.

Simulates a fresh-install user who scaffolds a custom component, references it
from a user-tier recipe, and renders end-to-end. Protects against:

- `component_ops.scaffold()` writing to bundled `COMPONENTS_DIR` regardless
  of `--namespace user` (the symmetric bug to Phase 2's recipe write path).
- `compose._resolve_component_dir()` missing the user tier → user components
  fail to resolve at render time.
- `compose._load_primitive_styles()` scanning only the bundled primitives dir
  → user primitive CSS silently dropped from the rendered HTML.
- `build.py._on_disk_components()` missing user tier → audit gate orphans
  every user component (the Phase-2-shaped regression).
- `component_ops` `.relative_to(REPO_ROOT)` crashes on user-tier paths.

Two tests:

1. `test_fresh_install_user_component_renders_e2e` — spawns the public CLIs
   as fresh Python subprocesses (matching real user behaviour), proving
   scaffold → write-to-user-tier → audit-gated render → PDF all line up.

2. `test_user_primitive_and_section_styles_reach_compose_output` — calls
   `compose()` in-process and asserts BOTH a user-primitive sentinel
   (`#112233`, exercises `_load_primitive_styles()`) AND a user-section
   sentinel (`#445566`, exercises the per-section CSS loader) land in the
   returned HTML. Only way to prove CSS inclusion without PDF pixel-matching.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def user_env(tmp_path):
    """Simulate a fresh-install user: all `KATIB_*` dirs under `tmp_path`.

    Returns `(env_dict, tmp_path)` — suitable for `subprocess.run(env=...)`.
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
    env.pop("KATIB_DEV_MODE", None)
    return env, tmp_path


def _run(cmd, env, cwd=REPO_ROOT):
    return subprocess.run(
        cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=180
    )


# ------------------------------------------------------------------ T-E1: full subprocess E2E


def test_fresh_install_user_component_renders_e2e(user_env):
    env, tmp = user_env
    comp_name = "p4-user-widget"
    recipe_name = "p4-user-widget-recipe"

    # 1. Scaffold a user section.
    r = _run(
        [sys.executable, "scripts/component.py", "new", comp_name,
         "--tier", "section", "--namespace", "user",
         "--languages", "en",
         "--description", "E2E smoke — fresh-install user section."],
        env=env,
    )
    assert r.returncode == 0, (
        f"component scaffold failed:\nstdout={r.stdout}\nstderr={r.stderr}"
    )

    # 2. Must land in user tier, NOT in bundled.
    user_comp_dir = tmp / "components" / "sections" / comp_name
    assert user_comp_dir.exists(), (
        f"scaffold did not write to user tier. Expected {user_comp_dir}.\n"
        f"stdout: {r.stdout}"
    )
    assert (user_comp_dir / "component.yaml").exists()
    bundled_comp_dir = REPO_ROOT / "components" / "sections" / comp_name
    assert not bundled_comp_dir.exists(), (
        f"scaffold polluted bundled tier at {bundled_comp_dir}"
    )

    # 3. Write a minimal en.html that echoes an input.
    (user_comp_dir / "en.html").write_text(
        '<section class="katib-p4-user-widget">'
        '<h2>{{ input.title }}</h2>'
        '</section>\n',
        encoding="utf-8",
    )

    # 4. Patch component.yaml to declare the `title` input.
    yaml_path = user_comp_dir / "component.yaml"
    cdata = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    cdata["accepts"] = {
        "inputs": [
            {"title": {"type": "string", "required": True,
                       "description": "Section heading."}}
        ]
    }
    yaml_path.write_text(
        yaml.safe_dump(cdata, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    # 5. Scaffold a user recipe (any name — we overwrite the body next).
    r = _run(
        [sys.executable, "scripts/recipe.py", "new", recipe_name,
         "--namespace", "user",
         "--description", "E2E smoke recipe referencing a user section."],
        env=env,
    )
    assert r.returncode == 0, (
        f"recipe scaffold failed:\nstdout={r.stdout}\nstderr={r.stderr}"
    )

    # 6. Overwrite recipe YAML to use our user section.
    user_recipe = tmp / "recipes" / f"{recipe_name}.yaml"
    user_recipe.write_text(
        f"name: {recipe_name}\n"
        f"version: 0.1.0\n"
        f"namespace: user\n"
        f"languages: [en]\n"
        f"description: E2E smoke.\n"
        f"sections:\n"
        f"  - component: {comp_name}\n"
        f"    inputs:\n"
        f"      title: Phase-4 fresh-install user component render.\n",
        encoding="utf-8",
    )

    # 7. Render via the audit-gated build path (NO --skip-audit-check).
    #    This is the shape real users hit. Fails before Task 6 because the
    #    audit gate cannot see the user component.
    out_pdf = tmp / "out.pdf"
    r = _run(
        [sys.executable, "scripts/build.py", recipe_name,
         "--lang", "en", "--out", str(out_pdf)],
        env=env,
    )
    assert r.returncode == 0, (
        "build failed — this is the Phase-4 regression symptom.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert out_pdf.exists() and out_pdf.stat().st_size > 0

    pdf = PdfReader(str(out_pdf))
    text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    assert "Phase-4 fresh-install" in text, (
        f"rendered PDF does not contain the section input text.\n"
        f"text: {text!r}"
    )


# ------------------------------------------------------------------ T-E2: scaffold refuses bundled shadow


def test_fresh_install_scaffold_refuses_to_shadow_bundled_component(user_env):
    """Match recipe precedent: scaffolding a user component with the same
    name as a bundled one must be refused without `--force --justification`.
    `module` is a bundled section shipped with the skill.
    """
    env, _ = user_env
    r = _run(
        [sys.executable, "scripts/component.py", "new", "module",
         "--tier", "section", "--namespace", "user"],
        env=env,
    )
    assert r.returncode != 0, (
        f"scaffold should refuse to shadow bundled 'module'.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    combined = (r.stdout + r.stderr).lower()
    assert "already exists" in combined or "bundled" in combined


# ------------------------------------------------------------------ T-E3: in-process CSS sentinel


def test_user_primitive_and_section_styles_reach_compose_output(isolated_user_dirs):
    """Proves BOTH user primitive CSS AND user section CSS reach the rendered
    HTML when `compose()` runs with user-tier components. Primitive sentinels
    come from `_load_primitive_styles()`; section sentinels come from the
    per-section loader that reads `comp["__dir__"] / styles.css`. Without
    Task 5's two-tier wiring, neither sentinel appears.
    """
    from core import compose as compose_mod
    from core.tokens import user_components_dir, user_recipes_dir

    user_comp_root = user_components_dir()
    user_rec_root = user_recipes_dir()

    # --- user primitive with sentinel CSS ---
    prim_dir = user_comp_root / "primitives" / "p4-user-prim"
    prim_dir.mkdir(parents=True)
    (prim_dir / "component.yaml").write_text(yaml.safe_dump({
        "name": "p4-user-prim",
        "tier": "primitive",
        "version": "0.1.0",
        "namespace": "user",
        "description": "User primitive for CSS sentinel test.",
        "languages": ["en"],
        "requires": {"tokens": []},
        "accepts": {
            "inputs": [{"text": {"type": "string", "required": False}}]
        },
    }, sort_keys=False), encoding="utf-8")
    (prim_dir / "en.html").write_text(
        '<span class="p4-prim-sentinel">{{ input.text }}</span>\n',
        encoding="utf-8",
    )
    (prim_dir / "styles.css").write_text(
        ".p4-prim-sentinel { color: #112233; }\n", encoding="utf-8",
    )
    (prim_dir / "README.md").write_text("# p4-user-prim\n", encoding="utf-8")

    # --- user section with sentinel CSS ---
    sec_dir = user_comp_root / "sections" / "p4-user-section"
    sec_dir.mkdir(parents=True)
    (sec_dir / "component.yaml").write_text(yaml.safe_dump({
        "name": "p4-user-section",
        "tier": "section",
        "version": "0.1.0",
        "namespace": "user",
        "description": "User section for CSS sentinel test.",
        "languages": ["en"],
        "requires": {"tokens": []},
        "accepts": {
            "inputs": [{"title": {"type": "string", "required": True}}]
        },
    }, sort_keys=False), encoding="utf-8")
    (sec_dir / "en.html").write_text(
        '<section class="p4-section-sentinel">'
        '<h2>{{ input.title }}</h2>'
        '</section>\n',
        encoding="utf-8",
    )
    (sec_dir / "styles.css").write_text(
        ".p4-section-sentinel { background: #445566; }\n",
        encoding="utf-8",
    )
    (sec_dir / "README.md").write_text("# p4-user-section\n", encoding="utf-8")

    # --- user recipe that references the user section ---
    recipe_path = user_rec_root / "p4-sentinel-recipe.yaml"
    recipe_path.write_text(yaml.safe_dump({
        "name": "p4-sentinel-recipe",
        "version": "0.1.0",
        "namespace": "user",
        "description": "CSS sentinel recipe.",
        "languages": ["en"],
        "sections": [
            {"component": "p4-user-section",
             "inputs": {"title": "Sentinel."}},
        ],
    }, sort_keys=False), encoding="utf-8")

    # --- in-process render ---
    html, _meta = compose_mod.compose("p4-sentinel-recipe", lang="en")

    # Primitive CSS reaches the HTML (loaded upfront by _load_primitive_styles)
    assert "#112233" in html, (
        "user primitive CSS (#112233) was NOT loaded. "
        "`_load_primitive_styles()` must scan user_components_dir() too."
    )
    # Section CSS reaches the HTML (loaded per-section via comp.__dir__)
    assert "#445566" in html, (
        "user section CSS (#445566) was NOT loaded. "
        "`_resolve_component_dir()` must return the user-tier path so the "
        "per-section CSS loader finds styles.css."
    )
