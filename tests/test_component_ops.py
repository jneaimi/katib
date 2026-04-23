"""Phase 2 Day 11 — component_ops library unit tests.

Covers every library entry point: scaffold, validate_full, render_isolated,
register, bundle_share, lint_all.

Each test that mutates disk cleans up after itself via _cleanup_component_dir
so it's safe to run in any order alongside the rest of the suite.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import component_ops as ops   # noqa: E402


# ================================================================== helpers


@pytest.fixture
def throwaway_name():
    """Generate a unique component name per test and clean up after."""
    name = "pytest-widget-ephemeral"
    # Pre-clean in case an earlier crashed test left residue
    ops._cleanup_component_dir(name)
    yield name
    ops._cleanup_component_dir(name)


# ================================================================== scaffold


def test_scaffold_creates_files(throwaway_name):
    result = ops.scaffold(
        throwaway_name,
        tier="primitive",
        languages=["en", "ar"],
        requires_tokens=["accent"],
        description="Sample primitive for testing",
    )
    assert result.component == throwaway_name
    assert result.tier == "primitive"
    cdir = REPO_ROOT / "components" / "primitives" / throwaway_name
    assert (cdir / "component.yaml").exists()
    assert (cdir / "en.html").exists()
    assert (cdir / "ar.html").exists()
    assert (cdir / "README.md").exists()
    fixture = REPO_ROOT / "tests" / "fixtures" / "components" / throwaway_name / "test-inputs.yaml"
    assert fixture.exists()


def test_scaffold_writes_audit_entry(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive")
    audit = ops.AUDIT_FILE.read_text("utf-8").splitlines()
    entries = [json.loads(line) for line in audit if line.strip()]
    scaffold_entries = [
        e for e in entries
        if e.get("component") == throwaway_name and e.get("action") == "scaffold"
    ]
    assert len(scaffold_entries) == 1
    assert scaffold_entries[0]["namespace"] == "katib"
    assert "at" in scaffold_entries[0]


def test_scaffold_graduation_warning_when_log_missing(throwaway_name, tmp_path, monkeypatch):
    """Fresh-install path: when no request log exists, the gate soft-passes with a warning.

    Previously the repo's `memory/component-requests.jsonl` was absent (through
    Phase-2 Day-12); Phase-3 Day-1 created it via real graduation requests.
    To preserve the first-install contract under test, point the log at a
    throwaway path that intentionally does not exist."""
    monkeypatch.setattr(ops, "REQUESTS_FILE", tmp_path / "component-requests.jsonl")
    assert not ops.REQUESTS_FILE.exists()
    result = ops.scaffold(throwaway_name, tier="primitive")
    assert result.graduation_warning is not None
    assert "not yet active" in result.graduation_warning.lower()


def test_scaffold_rejects_existing_component():
    with pytest.raises(ValueError, match="already exists"):
        ops.scaffold("eyebrow", tier="primitive")


def test_scaffold_rejects_invalid_name():
    with pytest.raises(ValueError, match="kebab-case"):
        ops.scaffold("Bad_Name", tier="primitive")


def test_scaffold_rejects_invalid_tier():
    with pytest.raises(ValueError, match="tier must be"):
        ops.scaffold("x-valid-name", tier="banana")


def test_scaffold_force_requires_justification(throwaway_name):
    with pytest.raises(ValueError, match="justification"):
        ops.scaffold(throwaway_name, tier="primitive", force=True)


def test_scaffolded_component_passes_schema(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", requires_tokens=["accent"])
    # The freshly-scaffolded component should at least pass schema validation
    v = ops.validate_full(throwaway_name)
    schema_errors = [i for i in v.issues if i.severity == "error" and i.category == "schema"]
    assert schema_errors == []


def test_scaffold_bilingual(throwaway_name):
    ops.scaffold(throwaway_name, tier="section", languages=["bilingual"])
    cdir = REPO_ROOT / "components" / "sections" / throwaway_name
    assert (cdir / "bilingual.html").exists()
    assert not (cdir / "en.html").exists()


# ================================================================== validate_full


def test_validate_full_existing_component_no_schema_errors():
    """Every existing component must pass schema validation."""
    for name in ("eyebrow", "callout", "module", "cover-page", "chart-donut"):
        v = ops.validate_full(name)
        schema_errors = [i for i in v.issues if i.severity == "error" and i.category == "schema"]
        assert schema_errors == [], f"{name} has schema errors: {schema_errors}"


def test_validate_full_missing_component():
    with pytest.raises(ValueError, match="not found"):
        ops.validate_full("does-not-exist-12345")


def test_validate_full_detects_missing_lang_html(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en", "ar"])
    # Delete ar.html to simulate a broken component
    (REPO_ROOT / "components" / "primitives" / throwaway_name / "ar.html").unlink()
    v = ops.validate_full(throwaway_name)
    errs = [i for i in v.errors if i.category == "lang"]
    assert len(errs) == 1
    assert "ar.html is missing" in errs[0].message


def test_validate_full_detects_undeclared_input(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    cdir = REPO_ROOT / "components" / "primitives" / throwaway_name
    # Inject an undeclared input reference into en.html
    html = (cdir / "en.html").read_text()
    html = html.replace(
        "{{ input.title }}", "{{ input.title }} — {{ input.undeclared_field }}"
    )
    (cdir / "en.html").write_text(html)
    v = ops.validate_full(throwaway_name)
    errs = [i for i in v.errors if i.category == "inputs"]
    assert any("undeclared_field" in e.message for e in errs)


def test_validate_full_detects_undeclared_html_token(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"], requires_tokens=["accent"])
    cdir = REPO_ROOT / "components" / "primitives" / throwaway_name
    html = (cdir / "en.html").read_text()
    html = html.replace("{{ input.title }}", "{{ colors.rogue_token }} {{ input.title }}")
    (cdir / "en.html").write_text(html)
    v = ops.validate_full(throwaway_name)
    errs = [i for i in v.errors if i.category == "tokens"]
    assert any("rogue_token" in e.message for e in errs)


def test_validate_full_detects_missing_lang_attr(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    cdir = REPO_ROOT / "components" / "primitives" / throwaway_name
    # Remove lang= from root section
    html = (cdir / "en.html").read_text()
    html = html.replace('lang="en"', "")
    (cdir / "en.html").write_text(html)
    v = ops.validate_full(throwaway_name)
    warns = [i for i in v.warnings if i.category == "a11y"]
    assert any("lang= attribute" in w.message for w in warns)


def test_validate_full_flags_missing_readme(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    cdir = REPO_ROOT / "components" / "primitives" / throwaway_name
    (cdir / "README.md").unlink()
    v = ops.validate_full(throwaway_name)
    errs = [i for i in v.errors if i.category == "docs"]
    assert any("README.md missing" in e.message for e in errs)


def test_validate_result_as_dict_shape(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    v = ops.validate_full(throwaway_name)
    d = v.as_dict()
    assert set(d.keys()) == {"component", "tier", "path", "ok", "issues"}
    for issue in d["issues"]:
        assert set(issue.keys()) == {"severity", "category", "message"}


# ================================================================== render_isolated


def test_render_isolated_scaffolded_component(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    results = ops.render_isolated(throwaway_name)
    assert len(results) == 1
    assert results[0].lang == "en"
    assert results[0].pdf_bytes > 100
    assert results[0].weasyprint_warnings == 0
    assert Path(results[0].pdf_path).exists()


def test_render_isolated_rejects_undeclared_lang(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    with pytest.raises(ValueError, match="does not declare lang"):
        ops.render_isolated(throwaway_name, lang="ar")


def test_render_isolated_handles_existing_component():
    """Sanity check: a real production component renders in isolation."""
    results = ops.render_isolated("eyebrow", lang="en")
    assert len(results) == 1
    assert results[0].pdf_bytes > 500


# ================================================================== register


def test_register_requires_clean_validation(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en", "ar"])
    # Delete ar.html — validation fails, register must refuse
    (REPO_ROOT / "components" / "primitives" / throwaway_name / "ar.html").unlink()
    with pytest.raises(ValueError, match="validation error"):
        ops.register(throwaway_name)


def test_register_writes_audit_and_regen(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    result = ops.register(throwaway_name)
    assert result.capabilities_regenerated is True
    assert result.audit_entry["action"] == "register"

    # capabilities.yaml should now include the new component
    caps = (REPO_ROOT / "capabilities.yaml").read_text("utf-8")
    assert throwaway_name in caps

    # cleanup: regenerate capabilities after fixture tears down
    # (finalizer will remove the component; we also regen to keep caps accurate)


def test_register_audit_roundtrip(throwaway_name):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    ops.register(throwaway_name)
    audit = ops.AUDIT_FILE.read_text("utf-8").splitlines()
    entries = [json.loads(line) for line in audit if line.strip()]
    matching = [e for e in entries if e.get("component") == throwaway_name]
    actions = [e.get("action") for e in matching]
    assert "scaffold" in actions
    assert "register" in actions


# ================================================================== bundle_share


def test_bundle_share_produces_tarball(throwaway_name, tmp_path):
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    result = ops.bundle_share(throwaway_name, out_dir=tmp_path)
    bundle = Path(result.bundle_path)
    assert bundle.exists()
    assert bundle.suffix == ".gz"
    assert result.bundle_bytes > 100


def test_bundle_share_excludes_audit_and_capabilities(throwaway_name, tmp_path):
    import tarfile
    ops.scaffold(throwaway_name, tier="primitive", languages=["en"])
    result = ops.bundle_share(throwaway_name, out_dir=tmp_path)
    with tarfile.open(result.bundle_path) as tar:
        names = tar.getnames()
    assert not any("audit" in n for n in names)
    assert not any("capabilities" in n for n in names)
    # Manifest is included
    assert f"{throwaway_name}/MANIFEST.json" in names


def test_bundle_share_missing_component(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        ops.bundle_share("does-not-exist-xyz", out_dir=tmp_path)


# ================================================================== lint_all


def test_lint_all_runs_over_every_component():
    results = ops.lint_all()
    assert len(results) >= 20
    # All existing components should pass schema/lang/input/brand/a11y checks
    # (token warnings are acceptable; only errors break the build)
    for r in results:
        assert r.ok, f"{r.component} has errors: {[i.message for i in r.errors]}"
