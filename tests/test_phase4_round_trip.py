"""Phase-4 Day 7 — end-to-end round-trip.

The contract Phase 4 was built to satisfy: a user-tier recipe + its
custom component dependencies can be exported to a `.katib-pack` on
machine A, transferred peer-to-peer (here: file copy across two
isolated user-tier dirs), and imported on machine B such that the
recipe renders cleanly via `build.py`.

This is the integration test that proves all six prior days work
together: schema + hash + CLI + bundle dep walk + verify + audit-on-
import + bundled-dep gate. If this passes, Phase 4 is deliverable.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import pack as pack_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers — minimal renderable artifacts
# ---------------------------------------------------------------------------


def _make_user_component(user_components: Path, name: str, tier: str = "primitive") -> Path:
    """Scaffold a minimal renderable user-tier component.

    Just enough HTML/CSS for build.py + WeasyPrint to produce a valid
    PDF page when this component is composed into a recipe section.
    """
    tier_dir = {"primitive": "primitives", "section": "sections"}[tier]
    cdir = user_components / tier_dir / name
    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / "component.yaml").write_text(
        yaml.safe_dump(
            {
                "name": name,
                "tier": tier,
                "version": "0.1.0",
                "namespace": "user",
                "languages": ["en"],
                "description": f"Round-trip test component {name}.",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    # Minimal Jinja that produces visible text for assertion
    (cdir / "en.html").write_text(
        f'<div class="katib-{name}"><p>{name.upper()} component rendered OK.</p></div>',
        encoding="utf-8",
    )
    (cdir / "styles.css").write_text(
        f".katib-{name} {{ padding: 8mm; font-size: 11pt; }}\n", encoding="utf-8"
    )
    (cdir / "README.md").write_text(f"# {name}\nRound-trip test fixture.\n", encoding="utf-8")
    return cdir


def _make_user_recipe(user_recipes: Path, name: str, sections: list[dict]) -> Path:
    rpath = user_recipes / f"{name}.yaml"
    rpath.write_text(
        yaml.safe_dump(
            {
                "name": name,
                "version": "1.0.0",
                "namespace": "user",
                "languages": ["en"],
                "description": "Round-trip integration recipe.",
                "sections": sections,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return rpath


def _build_recipe(recipe_name: str, sandbox: Path, out_path: Path) -> subprocess.CompletedProcess:
    """Invoke build.py with sandbox env vars pointing user-tier dirs
    at `sandbox`. Returns the completed process so the caller can
    assert returncode + stderr."""
    env = os.environ.copy()
    env["KATIB_RECIPES_DIR"] = str(sandbox / "recipes")
    env["KATIB_COMPONENTS_DIR"] = str(sandbox / "components")
    env["KATIB_MEMORY_DIR"] = str(sandbox / "memory")
    env["KATIB_BRANDS_DIR"] = str(sandbox / "brands")
    env["KATIB_OUTPUT_ROOT"] = str(sandbox / "output")
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build.py"),
            recipe_name,
            "--lang",
            "en",
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        cwd=REPO_ROOT,
    )


# ---------------------------------------------------------------------------
# The full round-trip
# ---------------------------------------------------------------------------


def test_full_round_trip_export_import_render(tmp_path):
    """End-to-end: sandbox A scaffolds custom component + recipe;
    bundle export; sandbox B (clean) imports and renders. The
    rendered PDF in B must exist + be non-trivial + contain the
    text the custom component emits."""
    sandbox_a = tmp_path / "sandbox-a"
    sandbox_b = tmp_path / "sandbox-b"
    for sb in (sandbox_a, sandbox_b):
        for sub in ("recipes", "components", "memory", "brands", "output"):
            (sb / sub).mkdir(parents=True, exist_ok=True)

    # --- Sandbox A: scaffold + export ---
    a_components = sandbox_a / "components"
    a_recipes = sandbox_a / "recipes"
    _make_user_component(a_components, "custom-banner", tier="section")
    _make_user_recipe(
        a_recipes,
        "round-trip-demo",
        [
            {"component": "custom-banner"},
            {"component": "module", "inputs": {"title": "Section A", "body": "body of A"}},
        ],
    )

    # We can't use the isolated_user_dirs fixture here (it only handles
    # one sandbox), so redirect manually to A for the export step.
    orig_user_recipes = pack_mod.USER_RECIPES_DIR
    orig_user_components = pack_mod.USER_COMPONENTS_DIR
    orig_user_brands = pack_mod.USER_BRANDS_DIR
    pack_mod.USER_RECIPES_DIR = a_recipes
    pack_mod.USER_COMPONENTS_DIR = a_components
    pack_mod.USER_BRANDS_DIR = sandbox_a / "brands"

    # Also redirect recipe_ops + component_ops since verify_pack runs
    # the recipe validator under our redirects.
    from core import component_ops, recipe_ops
    orig_co_user = component_ops.USER_COMPONENTS_DIR
    orig_ro_user_recipes = recipe_ops.USER_RECIPES_DIR
    orig_ro_user_components = recipe_ops.USER_COMPONENTS_DIR
    component_ops.USER_COMPONENTS_DIR = a_components
    recipe_ops.USER_RECIPES_DIR = a_recipes
    recipe_ops.USER_COMPONENTS_DIR = a_components

    try:
        result_a = pack_mod.export_bundle(
            "round-trip-demo",
            author={"name": "Round Trip", "email": "rt@test"},
            out_dir=sandbox_a / "out",
        )
        assert Path(result_a.pack_path).exists()
        assert result_a.pack_name == "round-trip/round-trip-demo"

        # --- Sandbox B: clean import ---
        pack_mod.USER_RECIPES_DIR = sandbox_b / "recipes"
        pack_mod.USER_COMPONENTS_DIR = sandbox_b / "components"
        pack_mod.USER_BRANDS_DIR = sandbox_b / "brands"
        component_ops.USER_COMPONENTS_DIR = sandbox_b / "components"
        recipe_ops.USER_RECIPES_DIR = sandbox_b / "recipes"
        recipe_ops.USER_COMPONENTS_DIR = sandbox_b / "components"

        # Also redirect memory dirs so audit lands in sandbox B
        orig_co_memory = component_ops.MEMORY_DIR
        orig_ro_memory = recipe_ops.MEMORY_DIR
        orig_co_audit = component_ops.AUDIT_FILE
        orig_ro_audit = recipe_ops.AUDIT_FILE
        component_ops.MEMORY_DIR = sandbox_b / "memory"
        component_ops.AUDIT_FILE = sandbox_b / "memory" / "component-audit.jsonl"
        recipe_ops.MEMORY_DIR = sandbox_b / "memory"
        recipe_ops.AUDIT_FILE = sandbox_b / "memory" / "recipe-audit.jsonl"

        # Also build.py
        import scripts.build as build_mod
        orig_build_audit = build_mod.AUDIT_FILE
        orig_build_recipe_audit = build_mod.RECIPE_AUDIT_FILE
        build_mod.AUDIT_FILE = sandbox_b / "memory" / "component-audit.jsonl"
        build_mod.RECIPE_AUDIT_FILE = sandbox_b / "memory" / "recipe-audit.jsonl"

        # import_pack resolves audit paths via core.tokens.user_memory_dir()
        # which reads KATIB_MEMORY_DIR live — set it for this scope.
        orig_env_memory = os.environ.get("KATIB_MEMORY_DIR")
        os.environ["KATIB_MEMORY_DIR"] = str(sandbox_b / "memory")

        try:
            imp = pack_mod.import_pack(
                Path(result_a.pack_path), regenerate_capabilities=False
            )
            assert imp.audit_entries_added == 2  # 1 component + 1 recipe

            # The custom component now lives in sandbox B
            assert (sandbox_b / "components" / "sections" / "custom-banner" / "component.yaml").exists()
            assert (sandbox_b / "recipes" / "round-trip-demo.yaml").exists()
            assert (sandbox_b / "memory" / "component-audit.jsonl").exists()
            assert (sandbox_b / "memory" / "recipe-audit.jsonl").exists()

            # --- Sandbox B: render via subprocess (so build.py sees env vars) ---
            pdf_path = sandbox_b / "round-trip.pdf"
            r = _build_recipe("round-trip-demo", sandbox_b, pdf_path)
            assert r.returncode == 0, (
                f"build.py failed on imported recipe.\nstdout={r.stdout}\nstderr={r.stderr}"
            )
            assert pdf_path.exists(), "PDF was not produced"
            assert pdf_path.stat().st_size > 1024, (
                f"PDF too small ({pdf_path.stat().st_size} bytes) — render likely empty"
            )

            # The PDF must contain the custom component's marker text
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(pdf_path))
                full_text = "\n".join(p.extract_text() or "" for p in reader.pages)
            except ImportError:
                pytest.skip("pypdf not available")
            assert "CUSTOM-BANNER" in full_text, (
                f"PDF does not contain the custom component's text. Extract:\n{full_text[:500]}"
            )
        finally:
            component_ops.MEMORY_DIR = orig_co_memory
            recipe_ops.MEMORY_DIR = orig_ro_memory
            component_ops.AUDIT_FILE = orig_co_audit
            recipe_ops.AUDIT_FILE = orig_ro_audit
            build_mod.AUDIT_FILE = orig_build_audit
            build_mod.RECIPE_AUDIT_FILE = orig_build_recipe_audit
            if orig_env_memory is None:
                os.environ.pop("KATIB_MEMORY_DIR", None)
            else:
                os.environ["KATIB_MEMORY_DIR"] = orig_env_memory
    finally:
        pack_mod.USER_RECIPES_DIR = orig_user_recipes
        pack_mod.USER_COMPONENTS_DIR = orig_user_components
        pack_mod.USER_BRANDS_DIR = orig_user_brands
        component_ops.USER_COMPONENTS_DIR = orig_co_user
        recipe_ops.USER_RECIPES_DIR = orig_ro_user_recipes
        recipe_ops.USER_COMPONENTS_DIR = orig_ro_user_components


def test_round_trip_audit_entries_carry_provenance(tmp_path, isolated_user_dirs):
    """Cross-check the audit shape we discussed in Phase-4 design:
    every imported component+recipe gets `source_pack`, `source_pack_version`,
    `source_hash` for traceability back to the pack."""
    user_components = isolated_user_dirs / "components"
    user_recipes = isolated_user_dirs / "recipes"
    _make_user_component(user_components, "rt-comp", tier="primitive")
    _make_user_recipe(
        user_recipes,
        "rt-recipe",
        [{"component": "rt-comp"}, {"component": "module"}],
    )

    res = pack_mod.export_bundle(
        "rt-recipe",
        author={"name": "RT", "email": "rt@x"},
        out_dir=tmp_path / "out",
    )

    # Wipe and re-import
    import shutil
    shutil.rmtree(user_components / "primitives" / "rt-comp")
    (user_recipes / "rt-recipe.yaml").unlink()

    pack_mod.import_pack(Path(res.pack_path), regenerate_capabilities=False)

    import json as _json
    comp_rows = [
        _json.loads(line)
        for line in (isolated_user_dirs / "memory" / "component-audit.jsonl").read_text().splitlines()
    ]
    recipe_rows = [
        _json.loads(line)
        for line in (isolated_user_dirs / "memory" / "recipe-audit.jsonl").read_text().splitlines()
    ]

    for row in comp_rows + recipe_rows:
        assert row["action"] == "imported"
        assert row["source_pack"] == res.pack_name
        assert row["source_pack_version"] == res.version
        assert row["source_hash"] == res.content_hash
