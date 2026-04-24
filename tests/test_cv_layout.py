"""cv-layout section — schema invariants + 2-column grid behavior.

Phase 3 Day 18 component (3 of 3 for the CV infra sprint). Auto-graduated
through the request log (3 verified dependents: personal-cv primary +
Deferred portfolio/profile). Fundamental structural departure from the
single-column linear-flow pattern every other Phase-3 recipe uses —
70mm accent-bg sidebar + 1fr main column via CSS grid.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_cv_layout_loads_against_schema():
    c = load_component("cv-layout")
    assert c["tier"] == "section"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_cv_layout_inputs_required():
    c = load_component("cv-layout")
    inputs_by_name = {
        next(iter(inp.keys())): next(iter(inp.values()))
        for inp in c["accepts"]["inputs"]
    }
    assert inputs_by_name["sidebar_html"]["required"] is True
    assert inputs_by_name["main_html"]["required"] is True


def test_cv_layout_token_contract():
    c = load_component("cv-layout")
    required = set(c["requires"]["tokens"])
    assert {"text", "accent", "accent_on"}.issubset(required)


def test_cv_layout_has_no_variants():
    c = load_component("cv-layout")
    assert c.get("variants", []) == []


# ---------------------------------------------------------------- render


def _inline_recipe(tmp_path: Path, lang: str = "en") -> Path:
    rfile = tmp_path / "cvl.yaml"
    rfile.write_text(
        "name: cvl-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: cv-layout\n"
        "    inputs:\n"
        "      sidebar_html: |\n"
        '        <div class="name-block">Jane Doe</div>\n'
        '        <section><h3>Contact</h3><p>email@example.com</p></section>\n'
        "      main_html: |\n"
        '        <section><h2>Summary</h2><p>Placeholder summary.</p></section>\n'
        '        <section><h2>Experience</h2><p>Placeholder experience.</p></section>\n'
    )
    return rfile


def test_cv_layout_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Semantic structure
    assert 'class="katib-cv-layout"' in html
    assert 'class="katib-cv-layout__sidebar"' in html
    assert 'class="katib-cv-layout__main"' in html
    # Semantic HTML5 elements
    assert "<aside" in html
    assert "<main" in html
    # Content passthrough
    assert "Jane Doe" in html
    assert "Placeholder summary" in html
    assert "Placeholder experience" in html


def test_cv_layout_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html


def test_cv_layout_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "cvl.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 3000


def test_cv_layout_grid_in_styles(tmp_path):
    """CSS grid declaration is present in rendered HTML (via inlined styles)."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "grid-template-columns: 70mm 1fr" in html
    assert "min-height: 257mm" in html


def test_cv_layout_sidebar_styling_present(tmp_path):
    """Sidebar uses accent background + accent-on foreground (dark theme)."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Both rules should appear in the inlined <style> block
    assert "katib-cv-layout__sidebar" in html
    assert "background: var(--accent)" in html
    assert "color: var(--accent-on)" in html


def test_cv_layout_html_passthrough_preserves_structure(tmp_path):
    """Complex nested HTML passes through sidebar_html and main_html
    unchanged (raw_body semantics)."""
    rfile = tmp_path / "cvl-complex.yaml"
    rfile.write_text(
        "name: cvl-complex\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cv-layout\n"
        "    inputs:\n"
        "      sidebar_html: |\n"
        '        <ul class="custom-list">\n'
        '          <li><strong>Email:</strong> test@example.com</li>\n'
        '          <li><strong>Phone:</strong> +971 50 000 0000</li>\n'
        '        </ul>\n'
        "      main_html: |\n"
        '        <h2>Experience</h2>\n'
        '        <article><h3>Role A</h3><p>Description</p></article>\n'
    )
    html, _ = compose(str(rfile), "en")
    # HTML tags pass through without escaping
    assert "<ul class=\"custom-list\">" in html
    assert "<strong>Email:</strong>" in html
    assert "<article><h3>Role A</h3>" in html
