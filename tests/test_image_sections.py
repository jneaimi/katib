"""Phase 2 Day 5 — two-column-image-text + tutorial-step."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_BG = REPO_ROOT / "tests" / "fixtures" / "cover-bg.jpg"
FIXTURE_STEP = REPO_ROOT / "tests" / "fixtures" / "tutorial-step.png"


# -------- two-column-image-text --------

def test_two_col_validates():
    c = load_component("two-column-image-text")
    assert c["tier"] == "section"
    assert set(c["variants"]) == {"image-left", "image-right", "image-top"}


def test_two_col_accepts_four_sources():
    c = load_component("two-column-image-text")
    img = next(
        (next(iter(i.values())) for i in c["accepts"]["inputs"] if "image" in i),
        None,
    )
    assert set(img["sources_accepted"]) == {"user-file", "url", "gemini", "screenshot"}


@pytest.mark.parametrize("variant", ["image-left", "image-right", "image-top"])
def test_two_col_renders_all_variants(variant, tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: two-col-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: two-column-image-text\n"
        f"    variant: {variant}\n"
        "    inputs:\n"
        "      heading: Test heading\n"
        "      body: Body paragraph.\n"
        f"      image: {{source: user-file, path: {FIXTURE_BG}}}\n"
        "      alt_text: fixture\n"
    )
    html, _ = compose(str(rfile), "en")
    assert f"katib-two-col--{variant}" in html
    assert "<img " in html


def test_two_col_requires_image_input(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: no-img\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: two-column-image-text\n"
        "    inputs: {heading: X, alt_text: Y}\n"
    )
    with pytest.raises(Exception, match="required image input"):
        compose(str(rfile), "en")


def test_two_col_ar_flips_flex_direction():
    html, _ = compose("phase-2-day5-showcase", "ar")
    assert 'dir="rtl"' in html
    # image-left in AR should still emit the image-left class — CSS handles flip
    assert "katib-two-col--image-left" in html


# -------- tutorial-step --------

def test_tutorial_step_validates():
    c = load_component("tutorial-step")
    assert c["tier"] == "section"
    assert c["languages"] == ["en", "ar"]


def test_tutorial_step_screenshot_excludes_gemini():
    c = load_component("tutorial-step")
    shot = next(
        (
            next(iter(i.values()))
            for i in c["accepts"]["inputs"]
            if "screenshot" in i
        ),
        None,
    )
    assert shot is not None
    assert set(shot["sources_accepted"]) == {"screenshot", "user-file"}
    assert "gemini" not in shot["sources_accepted"]


def test_tutorial_step_renders_text_only(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: step-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: tutorial-step\n"
        "    inputs:\n"
        "      number: 1\n"
        "      title: Install\n"
        "      body: Run the installer.\n"
    )
    html, _ = compose(str(rfile), "en")
    assert "katib-tutorial-step" in html
    assert ">1<" in html
    assert "<figure" not in html  # no screenshot


def test_tutorial_step_renders_with_screenshot(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: step-shot\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: tutorial-step\n"
        "    inputs:\n"
        "      number: 2\n"
        "      title: Verify\n"
        "      body: Open settings.\n"
        f"      screenshot: {{source: user-file, path: {FIXTURE_STEP}}}\n"
        "      screenshot_alt: Settings page\n"
    )
    html, _ = compose(str(rfile), "en")
    assert "<figure" in html
    assert 'alt="Settings page"' in html


def test_tutorial_step_rejects_gemini_source(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: step-bad\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: tutorial-step\n"
        "    inputs:\n"
        "      number: 1\n"
        "      title: Bad\n"
        "      screenshot: {source: gemini, prompt: fake UI screenshot}\n"
    )
    with pytest.raises(Exception, match="sources_accepted"):
        compose(str(rfile), "en")


# -------- end-to-end --------

def test_day5_showcase_renders_en(tmp_path):
    html, _ = compose("phase-2-day5-showcase", "en")
    assert "katib-two-col--image-left" in html
    assert "katib-two-col--image-right" in html
    assert "katib-two-col--image-top" in html
    assert "katib-tutorial-step" in html
    pdf = render_to_pdf(html, tmp_path / "d5.pdf", base_url=REPO_ROOT)
    # Three fixture images + one tutorial screenshot embedded
    assert pdf.stat().st_size > 40000


def test_day5_showcase_renders_ar(tmp_path):
    html, _ = compose("phase-2-day5-showcase", "ar")
    assert 'dir="rtl"' in html
    pdf = render_to_pdf(html, tmp_path / "d5.ar.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 40000
