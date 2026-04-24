"""Phase-3d migrated recipes — render + seed-manifest integration tests.

Phase 3d ports 6 v1 doc-types to v2 recipes, composed from the
Phase-3a layout + Phase-3c content component libraries. These tests
prove each new recipe renders end-to-end in both EN and AR, and that
every one is wired into the seed manifest so fresh installs ship with
them pre-seeded under ~/.katib/recipes/.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


PHASE_3D_RECIPES = [
    "legal-nda",
    "legal-service-agreement",
    "personal-bio",
    "formal-authority-letter",
    "report-progress",
    "editorial-article",
]


@pytest.mark.parametrize("name", PHASE_3D_RECIPES)
@pytest.mark.parametrize("lang", ["en", "ar"])
def test_phase_3d_recipe_renders(name, lang, tmp_path):
    """Each migrated recipe must render cleanly in both languages."""
    out = tmp_path / f"{name}.{lang}.pdf"
    r = subprocess.run(
        [sys.executable, "scripts/build.py", name,
         "--lang", lang, "--skip-audit-check", "--out", str(out)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"build failed for {name} {lang}:\n{r.stderr}"
    assert out.exists()
    # A zero-byte render indicates a template rendering bug that didn't
    # raise but produced nothing. WeasyPrint shouldn't produce tiny
    # PDFs — even a one-page doc weighs ~5KB.
    assert out.stat().st_size > 2000, \
        f"{name} {lang} PDF suspiciously small: {out.stat().st_size} bytes"


@pytest.mark.parametrize("name", PHASE_3D_RECIPES)
def test_phase_3d_recipe_is_seeded(name):
    """Every migrated recipe must be listed in seed-manifest.yaml so
    fresh-install users get it in their ~/.katib/recipes/ tier."""
    manifest = yaml.safe_load(
        (REPO_ROOT / "seed-manifest.yaml").read_text(encoding="utf-8")
    )
    assert name in manifest["recipes"], \
        f"recipe {name!r} not listed in seed-manifest.yaml — users won't get it on fresh install"


@pytest.mark.parametrize("name", PHASE_3D_RECIPES)
def test_phase_3d_recipe_declares_bilingual_support(name):
    """Every migrated recipe must declare `languages: [en, ar]` —
    bilingual is a core v2 contract. Recipe files that silently
    drop to EN-only betray the contract."""
    data = yaml.safe_load(
        (REPO_ROOT / "recipes" / f"{name}.yaml").read_text(encoding="utf-8")
    )
    langs = data.get("languages", [])
    assert "en" in langs and "ar" in langs, \
        f"recipe {name!r} declares languages {langs} — must include both en and ar"


def test_legal_nda_composes_from_expected_components():
    """Shape-test: legal-nda must use the legal-domain components that
    make it a real NDA — module numbered, callout, clause-list,
    signature-field-block. If a refactor strips any of these, the
    document stops being a recognizable NDA."""
    data = yaml.safe_load(
        (REPO_ROOT / "recipes" / "legal-nda.yaml").read_text(encoding="utf-8")
    )
    components_used = {s["component"] for s in data["sections"]}
    for required in ("module", "callout", "clause-list", "signature-field-block"):
        assert required in components_used, \
            f"legal-nda missing required component {required!r} — " \
            f"uses: {sorted(components_used)}"


def test_report_progress_uses_phase_3c_content_library():
    """report-progress is the acceptance test for the Phase-3c
    content components. If it stops using exec-summary, timeline, or
    metric-block, the Phase-3c library has regressed in practice."""
    data = yaml.safe_load(
        (REPO_ROOT / "recipes" / "report-progress.yaml").read_text(encoding="utf-8")
    )
    components_used = {s["component"] for s in data["sections"]}
    for required in ("executive-summary", "timeline", "metric-block"):
        assert required in components_used, \
            f"report-progress missing Phase-3c component {required!r} — " \
            f"uses: {sorted(components_used)}"


def test_editorial_article_uses_citations_and_references():
    """The editorial-article recipe demonstrates the citation +
    references-list pairing. If one is dropped without the other, the
    paired contract is broken for all future recipes."""
    data = yaml.safe_load(
        (REPO_ROOT / "recipes" / "editorial-article.yaml").read_text(encoding="utf-8")
    )
    components_used = {s["component"] for s in data["sections"]}
    assert "two-column-page" in components_used, \
        "editorial-article must use two-column-page for the article body"
    assert "references-list" in components_used, \
        "editorial-article must include references-list"

    # Inline citation markers must appear in the two-column-page raw_body
    two_col = next(s for s in data["sections"] if s["component"] == "two-column-page")
    en_body = two_col["inputs_by_lang"]["en"]["raw_body"]
    assert "katib-citation" in en_body, \
        "editorial-article EN body must include inline citation markers " \
        "to pair with the references-list"
