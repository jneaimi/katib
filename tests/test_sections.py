"""Tier 2 scaffolding sections — render + schema invariants."""
from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent

SCAFFOLDING_SECTIONS = [
    "front-matter",
    "objectives-box",
    "summary",
    "whats-next",
    "reference-strip",
]


@pytest.mark.parametrize("name", SCAFFOLDING_SECTIONS)
def test_section_loads_against_schema(name):
    c = load_component(name)
    assert c["tier"] == "section"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_showcase_recipe_renders_en(tmp_path):
    html, _ = compose("phase-2-day2-showcase", "en")
    pdf = render_to_pdf(html, tmp_path / "showcase.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 5000

    text = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages).lower()
    # Content from each of the 5 sections should appear
    assert "scaffolding sections showcase" in text  # front-matter title
    assert "what this document proves" in text  # objectives-box label
    assert "day 2 recap" in text  # summary heading
    assert "after day 2 lands" in text  # whats-next heading
    assert "further reading" in text  # reference-strip heading


def test_showcase_recipe_renders_ar(tmp_path):
    html, _ = compose("phase-2-day2-showcase", "ar")
    pdf = render_to_pdf(html, tmp_path / "showcase.ar.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 5000
    # Arabic render always emits RTL direction
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html


def test_front_matter_page_break_declared():
    c = load_component("front-matter")
    assert c["page_behavior"]["break_after"] == "always"
    assert c["page_behavior"]["mode"] == "atomic"


def test_objectives_box_requires_items():
    c = load_component("objectives-box")
    # Find `items` input in schema
    items_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "items" in inp),
        None,
    )
    assert items_decl is not None
    assert items_decl["required"] is True


def test_whats_next_supports_numbered_variant():
    c = load_component("whats-next")
    assert "numbered" in c.get("variants", [])
    assert "bullet" in c.get("variants", [])


def test_reference_strip_tagged_variant_supported(tmp_path):
    # End-to-end: tagged variant with tag field renders a tag badge
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: tag-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: reference-strip\n"
        "    variant: tagged\n"
        "    inputs:\n"
        "      items:\n"
        "        - {label: Test, url: example.com, tag: SPEC}\n"
    )
    html, _ = compose(str(rfile), "en")
    assert "katib-tag" in html
    assert "SPEC" in html
    assert "example.com" in html


def test_sections_produce_heading_markup():
    # Summary and whats-next emit h2; reference-strip emits h3
    html, _ = compose("phase-2-day2-showcase", "en")
    assert "<h1" in html  # front-matter title
    assert "<h2" in html  # summary + whats-next headings
    assert "<h3" in html  # reference-strip heading


def test_primitives_styles_always_loaded():
    """Page shell must include every primitive's styles even when the recipe
    only uses sections (sections reference primitive CSS classes)."""
    html, _ = compose("phase-2-day2-showcase", "en")
    # Every primitive class name used by any section should be stylable
    for class_name in (
        ".katib-eyebrow",
        ".katib-rule",
        ".katib-tag",
    ):
        assert class_name in html, f"missing primitive styles for {class_name}"
