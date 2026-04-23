"""Phase 2 Day 3 — module section + cover-page cover component."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_module_validates():
    c = load_component("module")
    assert c["tier"] == "section"
    assert set(c["languages"]) == {"en", "ar"}
    assert "numbered" in c["variants"]
    assert "plain" in c["variants"]


def test_cover_page_validates():
    c = load_component("cover-page")
    assert c["tier"] == "cover"
    # Version bumps as variants are added (Day 3: 0.1.0; Day 4: 0.2.0)
    assert c["version"].startswith("0.")
    assert c["page_behavior"]["break_after"] == "always"
    assert c["page_behavior"]["min_height"] == "253mm"


def test_day3_showcase_renders_en(tmp_path):
    html, _ = compose("phase-2-day3-showcase", "en")
    assert "<h1 " in html  # cover title
    assert "Module composition showcase" in html  # cover title text
    assert "katib-module--numbered" in html
    assert "katib-cover" in html
    pdf = render_to_pdf(html, tmp_path / "d3.en.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 10000  # real multi-page render


def test_day3_showcase_renders_ar(tmp_path):
    html, _ = compose("phase-2-day3-showcase", "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    pdf = render_to_pdf(html, tmp_path / "d3.ar.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 10000


def test_cover_page_consumes_brand_logo_context(tmp_path, monkeypatch):
    # Given a brand with logo.primary set, the cover template should include
    # an <img class="katib-cover__logo"> tag. No brand → no logo tag.
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: cover-only\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: minimalist-typographic\n"
        "    inputs:\n"
        "      title: Test\n"
    )
    html_no_brand, _ = compose(str(rfile), "en")
    # No brand → no <img> tag with the logo class (CSS class name may still
    # appear inside the stylesheet, so match on the tag open)
    assert '<img class="katib-cover__logo"' not in html_no_brand

    # Point to the repo's example brand (which has fixtures/placeholder-logo.svg)
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(REPO_ROOT / "brands"))
    html_with_brand, _ = compose(str(rfile), "en", brand="example")
    assert '<img class="katib-cover__logo"' in html_with_brand
    assert "placeholder-logo.svg" in html_with_brand


def test_module_numbered_variant_shows_number(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: mod-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: module\n"
        "    variant: numbered\n"
        "    inputs: {number: 7, title: The Seventh}\n"
    )
    html, _ = compose(str(rfile), "en")
    assert 'class="katib-module__number"' in html
    assert ">7<" in html


def test_module_plain_variant_omits_number_markup(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: mod-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: module\n"
        "    variant: plain\n"
        "    inputs: {number: 99, title: Plain Jane}\n"
    )
    html, _ = compose(str(rfile), "en")
    assert 'class="katib-module__number"' not in html


def test_cover_page_renders_in_covers_tier_dir(tmp_path):
    # Smoke test that TIER_DIRS["cover"] resolves correctly
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: cov\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    inputs: {title: Hello}\n"
    )
    html, _ = compose(str(rfile), "en")
    # cover should produce its wrapper + title
    assert "katib-cover" in html
    assert "<h1" in html
    assert "Hello" in html


def test_day3_text_extract_includes_all_three_modules(tmp_path):
    html, _ = compose("phase-2-day3-showcase", "en")
    pdf = render_to_pdf(html, tmp_path / "d3.en.pdf", base_url=REPO_ROOT)
    text = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    for needle in ("Module 1", "Module 2", "Module 3"):
        assert needle.lower() in text.lower(), f"{needle!r} missing"
