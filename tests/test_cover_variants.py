"""Phase 2 Day 4 — cover-page image-background + neural-cartography variants."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from core.compose import compose, load_component
from core.render import render_to_pdf


def _section_class_attr(html: str) -> str:
    """Return the class attribute of the first <section> in the rendered HTML."""
    m = re.search(r'<section class="([^"]+)"', html)
    return m.group(1) if m else ""

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_BG = REPO_ROOT / "tests" / "fixtures" / "cover-bg.jpg"


def test_cover_declares_four_variants():
    c = load_component("cover-page")
    assert set(c["variants"]) == {
        "minimalist-typographic",
        "image-background",
        "neural-cartography",
        "framed-canvas",
    }
    assert c["version"] == "0.2.0"


def test_framed_canvas_variant_in_list():
    c = load_component("cover-page")
    assert "framed-canvas" in c["variants"]


def test_framed_canvas_variant_emits_image_no_scrim_visible(tmp_path):
    """framed-canvas: full-bleed image renders, scrim div is emitted but
    hidden via CSS, dark-text classes apply."""
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: framed-canvas-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: framed-canvas\n"
        "    inputs:\n"
        "      title: Framed canvas test\n"
        "      subtitle: Light editorial cover\n"
        f"      image: {{source: user-file, path: {FIXTURE_BG}}}\n"
    )
    html, _ = compose(str(rfile), "en")
    # Variant class lands on the section
    assert "katib-cover--framed-canvas" in html
    # has-image modifier applied (image was supplied)
    assert "katib-cover--has-image" in html
    # Image emitted into the cover
    assert '<img class="katib-cover__bg"' in html
    # Stylesheet defines display:none for the framed-canvas scrim — verify the
    # rule exists in the bundled CSS so the scrim is not visible.
    section_classes = _section_class_attr(html)
    assert "framed-canvas" in section_classes
    assert "image-background" not in section_classes
    assert "neural-cartography" not in section_classes
    # CSS rule that hides the scrim for this variant is in the stylesheet
    css_path = REPO_ROOT / "components" / "covers" / "cover-page" / "styles.css"
    css = css_path.read_text()
    assert ".katib-cover--framed-canvas .katib-cover__scrim" in css
    assert "display: none" in css


def test_framed_canvas_renders_to_pdf(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: framed-canvas-render\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: framed-canvas\n"
        "    inputs:\n"
        "      title: Framed render\n"
        "      subtitle: Dark text on warm canvas\n"
        f"      image: {{source: user-file, path: {FIXTURE_BG}}}\n"
    )
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "out.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 20000


def test_cover_image_input_declared():
    c = load_component("cover-page")
    decls = {
        next(iter(i.keys())): next(iter(i.values()))
        for i in c["accepts"]["inputs"]
        if isinstance(i, dict) and len(i) == 1
    }
    img = decls.get("image")
    assert img is not None
    assert img["type"] == "image"
    assert set(img["sources_accepted"]) == {"user-file", "url", "gemini"}
    assert img["required"] is False


def test_image_background_variant_emits_bg_and_scrim(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: img-bg-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: image-background\n"
        "    inputs:\n"
        "      title: Image test\n"
        f"      image: {{source: user-file, path: {FIXTURE_BG}}}\n"
    )
    html, _ = compose(str(rfile), "en")
    assert "katib-cover--image-background" in html
    assert "katib-cover--has-image" in html
    assert '<img class="katib-cover__bg"' in html
    assert 'class="katib-cover__scrim"' in html


def test_minimalist_variant_omits_bg_and_scrim(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: mini-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: minimalist-typographic\n"
        "    inputs: {title: Minimal}\n"
    )
    html, _ = compose(str(rfile), "en")
    # Check rendered HTML markup, not CSS class-name strings. The stylesheet
    # defines .katib-cover__scrim regardless of whether it's used.
    assert '<img class="katib-cover__bg"' not in html
    assert '<div class="katib-cover__scrim"' not in html
    # The cover's <section> class attribute shouldn't include the has-image modifier
    section_classes = _section_class_attr(html)
    assert "has-image" not in section_classes
    assert "minimalist-typographic" in section_classes


def test_image_background_variant_renders_to_pdf(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: img-bg-render\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: image-background\n"
        "    inputs:\n"
        "      title: Full-bleed test\n"
        "      subtitle: Scrim + overlay should render cleanly\n"
        f"      image: {{source: user-file, path: {FIXTURE_BG}}}\n"
    )
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "out.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 20000  # image embedded → real size


def test_image_background_falls_back_without_image(tmp_path):
    """variant=image-background but no image supplied → no bg markup, but
    rendering still succeeds (cover looks typographic)."""
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: missing-img\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: image-background\n"
        "    inputs: {title: Missing image}\n"
    )
    html, _ = compose(str(rfile), "en")
    assert '<img class="katib-cover__bg"' not in html
    assert "Missing image" in html


def test_neural_cartography_fail_loud_without_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: neural-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: neural-cartography\n"
        "    inputs:\n"
        "      title: Neural test\n"
        "      image:\n"
        "        source: gemini\n"
        "        prompt: editorial abstract, soft gradient\n"
        "        aspect: '3:4'\n"
    )
    with pytest.raises(Exception) as exc:
        compose(str(rfile), "en")
    msg = str(exc.value)
    assert "GEMINI_API_KEY" in msg
    assert "export" in msg


def test_image_variant_rejects_screenshot_source(tmp_path):
    # sources_accepted excludes 'screenshot' for cover-page
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: bad-src\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: cover-page\n"
        "    variant: image-background\n"
        "    inputs:\n"
        "      title: X\n"
        "      image: {source: screenshot, url: 'https://example.com'}\n"
    )
    with pytest.raises(Exception) as exc:
        compose(str(rfile), "en")
    assert "sources_accepted" in str(exc.value)


def test_day4_showcase_renders(tmp_path):
    html, _ = compose("phase-2-day4-showcase", "en")
    assert "Minimalist typographic" in html
    assert "Image background" in html
    assert "katib-cover__bg" in html  # image-background variant
    pdf = render_to_pdf(html, tmp_path / "d4.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 25000  # 3+ pages with embedded image


def test_day4_showcase_renders_ar(tmp_path):
    html, _ = compose("phase-2-day4-showcase", "ar")
    assert 'dir="rtl"' in html
    pdf = render_to_pdf(html, tmp_path / "d4.ar.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 25000
