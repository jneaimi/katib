"""Phase 2 Day 12 — recipe_ops library unit tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import recipe_ops as ops  # noqa: E402


@pytest.fixture
def throwaway_name():
    name = "pytest-recipe-ephemeral"
    ops._cleanup_recipe(name)
    yield name
    ops._cleanup_recipe(name)


# ================================================================== scaffold


def test_scaffold_creates_yaml(throwaway_name):
    result = ops.scaffold_recipe(
        throwaway_name,
        languages=["en"],
        description="Test recipe",
        keywords=["test", "smoke"],
    )
    rpath = REPO_ROOT / "recipes" / f"{throwaway_name}.yaml"
    assert rpath.exists()
    data = yaml.safe_load(rpath.read_text())
    assert data["name"] == throwaway_name
    assert data["languages"] == ["en"]
    assert data["keywords"] == ["test", "smoke"]
    assert len(data["sections"]) >= 2   # default scaffold has several sections


def test_scaffold_writes_audit_entry(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"])
    audit = ops.AUDIT_FILE.read_text("utf-8").splitlines()
    entries = [json.loads(line) for line in audit if line.strip()]
    scaffold_entries = [
        e for e in entries
        if e.get("recipe") == throwaway_name and e.get("action") == "scaffold"
    ]
    assert len(scaffold_entries) == 1


def test_scaffold_graduation_warning_when_log_missing(throwaway_name, tmp_path, monkeypatch):
    """Fresh-install path: when no request log exists, the gate soft-passes.
    Monkey-patches `ops.REQUESTS_FILE` because `memory/recipe-requests.jsonl`
    is now populated (Phase 3 Day 4 created it via real graduation requests
    for business-proposal-letter). Same hygiene fix as the component-ops
    sibling test (Phase 3 Day 1)."""
    monkeypatch.setattr(ops, "REQUESTS_FILE", tmp_path / "recipe-requests.jsonl")
    assert not ops.REQUESTS_FILE.exists()
    result = ops.scaffold_recipe(throwaway_name, languages=["en"])
    assert result.graduation_warning is not None
    assert "not yet active" in result.graduation_warning.lower()


def test_scaffold_rejects_existing_recipe():
    with pytest.raises(ValueError, match="already exists"):
        ops.scaffold_recipe("tutorial")


def test_scaffold_rejects_invalid_name():
    with pytest.raises(ValueError, match="kebab-case"):
        ops.scaffold_recipe("Bad_Recipe_Name")


def test_scaffold_rejects_bad_lang():
    with pytest.raises(ValueError, match="not in"):
        ops.scaffold_recipe("x-valid", languages=["jp"])


def test_scaffold_force_requires_justification(throwaway_name):
    with pytest.raises(ValueError, match="justification"):
        ops.scaffold_recipe(throwaway_name, force=True)


def test_scaffolded_recipe_passes_schema(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    v = ops.validate_recipe_full(throwaway_name)
    schema_errors = [i for i in v.issues if i.category == "schema"]
    assert schema_errors == []


# ================================================================== validate_recipe_full


def test_validate_all_existing_recipes_pass():
    """Every existing recipe must be valid."""
    for r in (
        "phase-1-trivial",
        "phase-2-day2-showcase",
        "phase-2-day3-showcase",
        "phase-2-day4-showcase",
        "phase-2-day5-showcase",
        "phase-2-day6-showcase",
        "tutorial",
    ):
        v = ops.validate_recipe_full(r)
        assert v.ok, f"{r} has errors: {[i.message for i in v.errors]}"


def test_validate_missing_recipe():
    with pytest.raises(ValueError, match="not found"):
        ops.validate_recipe_full("does-not-exist-xyz")


def test_validate_detects_unknown_component(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    rpath = REPO_ROOT / "recipes" / f"{throwaway_name}.yaml"
    data = yaml.safe_load(rpath.read_text())
    data["sections"].append({"component": "nonexistent-component-xyz"})
    rpath.write_text(yaml.safe_dump(data, sort_keys=False))
    v = ops.validate_recipe_full(throwaway_name)
    errs = [i for i in v.errors if i.category == "component-ref"]
    assert any("nonexistent-component-xyz" in e.message for e in errs)


def test_validate_detects_unsupported_lang(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en", "ar", "bilingual"], keywords=["smoke"])
    # The default scaffold uses cover-page + module — both declare [en, ar]
    # but not bilingual, so the recipe's `bilingual` lang should surface errors.
    v = ops.validate_recipe_full(throwaway_name)
    lang_errors = [i for i in v.errors if i.category == "lang"]
    assert len(lang_errors) > 0


def test_validate_detects_bad_variant(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    rpath = REPO_ROOT / "recipes" / f"{throwaway_name}.yaml"
    data = yaml.safe_load(rpath.read_text())
    # Find cover-page section, inject an invalid variant
    for section in data["sections"]:
        if section["component"] == "cover-page":
            section["variant"] = "nonexistent-variant-xyz"
    rpath.write_text(yaml.safe_dump(data, sort_keys=False))
    v = ops.validate_recipe_full(throwaway_name)
    var_errors = [i for i in v.errors if i.category == "variant"]
    assert any("nonexistent-variant-xyz" in e.message for e in var_errors)


def test_validate_warns_on_missing_keywords(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"])   # no keywords arg -> []
    v = ops.validate_recipe_full(throwaway_name)
    kw_warns = [i for i in v.warnings if i.category == "keywords"]
    assert len(kw_warns) == 1


def test_validate_detects_inverted_target_pages(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    rpath = REPO_ROOT / "recipes" / f"{throwaway_name}.yaml"
    data = yaml.safe_load(rpath.read_text())
    data["target_pages"] = [10, 3]
    rpath.write_text(yaml.safe_dump(data, sort_keys=False))
    v = ops.validate_recipe_full(throwaway_name)
    errs = [i for i in v.errors if i.category == "pages"]
    assert any("inverted" in e.message for e in errs)


def test_validate_fuzzy_suggests_component(throwaway_name):
    """Typos in component names should get a 'did you mean' suggestion."""
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    rpath = REPO_ROOT / "recipes" / f"{throwaway_name}.yaml"
    data = yaml.safe_load(rpath.read_text())
    data["sections"].append({"component": "cover-pag"})   # typo of cover-page
    rpath.write_text(yaml.safe_dump(data, sort_keys=False))
    v = ops.validate_recipe_full(throwaway_name)
    errs = [i for i in v.errors if i.category == "component-ref"]
    assert any("cover-page" in e.message for e in errs)


def test_validate_result_as_dict_shape(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    v = ops.validate_recipe_full(throwaway_name)
    d = v.as_dict()
    assert set(d.keys()) == {"recipe", "path", "ok", "issues"}


# ================================================================== render_recipe


def test_render_recipe_scaffold_skeleton_renders(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    results = ops.render_recipe(throwaway_name)
    assert len(results) == 1
    assert results[0].lang == "en"
    assert results[0].pdf_bytes > 500
    assert results[0].weasyprint_warnings == 0


def test_render_recipe_all_langs(throwaway_name):
    # Default scaffold uses cover-page + module + summary + whats-next — all declare en+ar
    ops.scaffold_recipe(throwaway_name, languages=["en", "ar"], keywords=["smoke"])
    results = ops.render_recipe(throwaway_name, langs=["en", "ar"])
    assert {r.lang for r in results} == {"en", "ar"}


def test_render_recipe_unknown_lang(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    with pytest.raises(ValueError, match="does not declare lang"):
        ops.render_recipe(throwaway_name, langs=["ar"])


def test_render_recipe_missing():
    with pytest.raises(ValueError, match="not found"):
        ops.render_recipe("does-not-exist-xyz")


# ================================================================== register


def test_register_refuses_broken_recipe(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    rpath = REPO_ROOT / "recipes" / f"{throwaway_name}.yaml"
    data = yaml.safe_load(rpath.read_text())
    data["sections"].append({"component": "nonexistent-xyz"})
    rpath.write_text(yaml.safe_dump(data, sort_keys=False))
    with pytest.raises(ValueError, match="validation error"):
        ops.register_recipe(throwaway_name)


def test_register_writes_audit_and_regen(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    result = ops.register_recipe(throwaway_name)
    assert result.capabilities_regenerated
    assert result.audit_entry["action"] == "register"
    caps = (REPO_ROOT / "capabilities.yaml").read_text("utf-8")
    assert throwaway_name in caps


def test_register_audit_roundtrip(throwaway_name):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    ops.register_recipe(throwaway_name)
    audit = ops.AUDIT_FILE.read_text("utf-8").splitlines()
    entries = [json.loads(line) for line in audit if line.strip()]
    matching = [e for e in entries if e.get("recipe") == throwaway_name]
    actions = [e.get("action") for e in matching]
    assert "scaffold" in actions
    assert "register" in actions


# ================================================================== bundle_share_recipe


def test_share_produces_tarball(throwaway_name, tmp_path):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    result = ops.bundle_share_recipe(throwaway_name, out_dir=tmp_path)
    bundle = Path(result.bundle_path)
    assert bundle.exists()
    assert bundle.name.startswith(f"recipe-{throwaway_name}")
    assert result.bundle_bytes > 100


def test_share_refuses_broken_recipe(throwaway_name, tmp_path):
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    rpath = REPO_ROOT / "recipes" / f"{throwaway_name}.yaml"
    data = yaml.safe_load(rpath.read_text())
    data["sections"].append({"component": "nonexistent-xyz"})
    rpath.write_text(yaml.safe_dump(data, sort_keys=False))
    with pytest.raises(ValueError, match="validation error"):
        ops.bundle_share_recipe(throwaway_name, out_dir=tmp_path)


def test_share_manifest_lists_components(throwaway_name, tmp_path):
    import tarfile
    ops.scaffold_recipe(throwaway_name, languages=["en"], keywords=["smoke"])
    result = ops.bundle_share_recipe(throwaway_name, out_dir=tmp_path)
    with tarfile.open(result.bundle_path) as tar:
        names = tar.getnames()
        manifest_member = tar.getmember(f"{throwaway_name}/MANIFEST.json")
        extracted = tar.extractfile(manifest_member)
        manifest = json.loads(extracted.read().decode("utf-8"))
    assert "referenced_components" in manifest
    assert "cover-page" in manifest["referenced_components"]
    assert "module" in manifest["referenced_components"]


# ================================================================== lint_all_recipes


def test_lint_all_runs_every_recipe():
    results = ops.lint_all_recipes()
    assert len(results) >= 7
    for r in results:
        assert r.ok, f"{r.recipe} has errors: {[i.message for i in r.errors]}"
