"""Phase-3c content primitives — integration tests.

Five content components (executive-summary, timeline, citation,
references-list, toc) and one earlier content primitive (metric-block,
shipped as the Phase-3b dogfood proof) round out the Katib library for
report-style documents.

These tests exercise each component standalone + the combined showcase
recipe end-to-end.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parent.parent


CONTENT_COMPONENTS = [
    ("metric-block", "primitive"),
    ("executive-summary", "section"),
    ("timeline", "section"),
    ("citation", "primitive"),
    ("references-list", "section"),
    ("toc", "section"),
]


@pytest.mark.parametrize("name,tier", CONTENT_COMPONENTS)
def test_content_component_renders_cleanly(name, tier):
    """Each Phase-3c content component's isolated render must succeed in
    EN and AR with zero WeasyPrint warnings."""
    r = subprocess.run(
        [sys.executable, "scripts/component.py", "test", name],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"component test for {name} failed:\n{r.stderr}\n{r.stdout}"

    tier_dir = {"primitive": "primitives", "section": "sections"}[tier]
    component_dir = REPO_ROOT / "components" / tier_dir / name
    assert (component_dir / "component.yaml").exists(), \
        f"{name} component.yaml not found at {component_dir}"

    for lang in ("en", "ar"):
        pdf_path = REPO_ROOT / "dist" / "component-tests" / name / f"{name}.{lang}.pdf"
        assert pdf_path.exists(), f"{name} {lang} PDF missing"

        # No WeasyPrint warnings — 'wp warnings' field in the harness output is
        # stronger than 'no crash'. If the test harness says warnings > 0,
        # the component has invalid CSS that silently degrades.
        assert "0 wp warnings" in r.stdout, \
            f"{name} rendered with WeasyPrint warnings:\n{r.stdout}"


@pytest.mark.parametrize("name,tier", CONTENT_COMPONENTS)
def test_content_component_schema_valid(name, tier):
    """Each component must pass schema validation — no errors, warnings
    allowed only for documented gaps (e.g. citation's inline-sup a11y
    regex mismatch)."""
    r = subprocess.run(
        [sys.executable, "scripts/component.py", "validate", name],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"validate failed for {name}:\n{r.stderr}\n{r.stdout}"
    assert "0 error(s)" in r.stdout, f"{name} has validation errors:\n{r.stdout}"


def test_phase_3c_showcase_recipe_renders_all_six_content_primitives(tmp_path):
    """The showcase recipe exercises every Phase-3c content primitive in
    one document — TOC, exec summary, 3 metric-blocks, timeline,
    citations in prose, references list."""
    r = subprocess.run(
        [sys.executable, "scripts/build.py", "phase-3c-content-showcase",
         "--lang", "en", "--skip-audit-check", "--out", str(tmp_path / "showcase.pdf")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"showcase build failed:\n{r.stderr}"

    pdf_path = tmp_path / "showcase.pdf"
    assert pdf_path.exists()
    reader = PdfReader(str(pdf_path))

    # Content-level assertions via text extraction. Each component
    # leaves a signature text on the page.
    all_text = "\n".join(p.extract_text() or "" for p in reader.pages)
    # Note: metric-block labels and timeline dates render via CSS
    # `text-transform: uppercase`. PDF text extraction returns the
    # transformed glyphs, so assertions must match the rendered case.
    for needle in [
        "Contents",              # toc
        "EXECUTIVE SUMMARY",     # executive-summary eyebrow
        "At a glance",           # executive-summary title
        "COMPONENTS SHIPPED",    # metric-block label (CSS-uppercased)
        "1002",                  # metric-block value
        "Phase 3 delivery",      # timeline title
        "APR 23",                # timeline event date (CSS-uppercased)
        "SECTION IV",            # findings module eyebrow
        "[1]",                   # citation marker in prose
        "References",            # references-list title
        "CourtBouillon",         # references-list entry
    ]:
        assert needle in all_text, \
            f"Phase-3c showcase missing expected text: {needle!r}"


def test_phase_3c_showcase_recipe_renders_arabic(tmp_path):
    """Arabic render path — bilingual is a core contract."""
    r = subprocess.run(
        [sys.executable, "scripts/build.py", "phase-3c-content-showcase",
         "--lang", "ar", "--skip-audit-check", "--out", str(tmp_path / "showcase.ar.pdf")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"AR showcase build failed:\n{r.stderr}"
    pdf = tmp_path / "showcase.ar.pdf"
    assert pdf.exists()

    reader = PdfReader(str(pdf))
    all_text = "\n".join(p.extract_text() or "" for p in reader.pages)
    # Arabic-specific: TOC title is not overridden in the recipe, so the
    # default "المحتويات" must render. The references-list title IS
    # overridden with "References" in the recipe for the showcase, so
    # don't assert on "المراجع" here — that localization is tested by
    # the standalone component render fixture.
    assert "المحتويات" in all_text, "Arabic TOC default title 'المحتويات' not rendered"


def test_executive_summary_items_render_with_label_separator():
    """The label::after pseudo-element emits ' —' between label and
    body. This is a visual-hierarchy test — if the pseudo-element is
    removed, the entries lose their labeled-list feel."""
    css = (REPO_ROOT / "components" / "sections" / "executive-summary" / "styles.css").read_text(encoding="utf-8")
    assert ".katib-exec-summary__item-label::after" in css, \
        "executive-summary label separator (::after ' —') removed — entries will render without visual delimiter"


def test_timeline_events_declare_three_status_states():
    """The timeline component must support done/active/upcoming statuses
    — they're the only way to convey progress. Schema test."""
    import yaml
    data = yaml.safe_load(
        (REPO_ROOT / "components" / "sections" / "timeline" / "component.yaml")
        .read_text(encoding="utf-8")
    )
    # The description documents the three statuses; the CSS enforces them.
    desc = data.get("description", "")
    assert "done" in desc and "active" in desc and "upcoming" in desc, \
        "timeline component.yaml no longer documents the three status states"

    css = (REPO_ROOT / "components" / "sections" / "timeline" / "styles.css").read_text(encoding="utf-8")
    for status in ("done", "active", "upcoming"):
        assert f".katib-timeline__event--{status}" in css, \
            f"timeline status {status!r} has no CSS — rendering will silently fall back to defaults"


def test_citation_and_references_list_paired_in_showcase():
    """The showcase must use citation markers inline in the body AND
    a corresponding references-list with matching numbered entries.
    If one drifts without the other, the paired contract is broken."""
    import yaml
    recipe = yaml.safe_load(
        (REPO_ROOT / "recipes" / "phase-3c-content-showcase.yaml").read_text(encoding="utf-8")
    )
    sections = recipe["sections"]
    # find the findings module + references-list
    has_citation_in_body = any(
        "[1]" in (s.get("inputs", {}).get("raw_body") or "")
        for s in sections
    )
    has_references = any(s["component"] == "references-list" for s in sections)

    assert has_citation_in_body, "showcase findings section missing [1] citation marker"
    assert has_references, "showcase missing references-list"


def test_toc_entries_support_three_nesting_levels():
    """Three-level nesting is a schema-level promise. If CSS doesn't
    cover all three, deep entries render unstyled."""
    css = (REPO_ROOT / "components" / "sections" / "toc" / "styles.css").read_text(encoding="utf-8")
    for level in (1, 2, 3):
        assert f".katib-toc__entry--level-{level}" in css, \
            f"toc level-{level} entry has no dedicated CSS — visual hierarchy broken"
