"""sections-grid section — schema invariants + render + variant behavior.

Phase 3 Day 11 component. Fifth of the genuinely-new Phase-3 section
components (after kv-list, letterhead, masthead-personal,
multi-party-signature-block). Dependents: tutorial/cheatsheet (Day 11 —
6 cards), business-proposal/one-pager (future — 2x2 body grid + metrics),
possibly tutorial/handoff retrofit (contact cards currently inlined).
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_sections_grid_loads_against_schema():
    c = load_component("sections-grid")
    assert c["tier"] == "section"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_sections_grid_variants_declared():
    c = load_component("sections-grid")
    variants = c.get("variants", [])
    assert "dense" in variants
    assert "bordered" in variants


def test_sections_grid_items_required():
    c = load_component("sections-grid")
    items_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "items" in inp),
        None,
    )
    assert items_decl is not None
    assert items_decl["required"] is True


def test_sections_grid_token_contract():
    c = load_component("sections-grid")
    required = set(c["requires"]["tokens"])
    # Tokens the stylesheet actually references
    assert {"text", "accent", "border"}.issubset(required)


# ---------------------------------------------------------------- render


def _inline_recipe(
    tmp_path: Path,
    variant: str | None = None,
    columns: int | None = None,
    lang: str = "en",
) -> Path:
    variant_line = f"    variant: {variant}\n" if variant else ""
    columns_line = f"      columns: {columns}\n" if columns else ""
    rfile = tmp_path / "sg.yaml"
    rfile.write_text(
        "name: sg-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: sections-grid\n"
        + variant_line +
        "    inputs:\n"
        + columns_line +
        "      heading: Key areas\n"
        "      items:\n"
        "        - {title: Card A, body: \"First card body text.\"}\n"
        "        - {title: Card B, body: \"Second card body text.\"}\n"
        "        - {title: Card C, body: \"Third card body text.\"}\n"
        "        - {title: Card D, body: \"Fourth card body text.\"}\n"
    )
    return rfile


def test_sections_grid_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Semantic structure
    assert "katib-sections-grid" in html
    assert "<article" in html
    assert html.count('class="katib-sections-grid__card"') == 4
    # Content preserved
    assert "Card A" in html
    assert "First card body text." in html
    # Heading emitted
    assert "Key areas" in html


def test_sections_grid_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    assert "katib-sections-grid" in html


def test_sections_grid_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "sg.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 3000


def test_sections_grid_dense_variant_class_emitted(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="dense")
    html, _ = compose(str(rfile), "en")
    assert "katib-sections-grid--dense" in html


def test_sections_grid_bordered_variant_class_emitted(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="bordered")
    html, _ = compose(str(rfile), "en")
    assert "katib-sections-grid--bordered" in html


def test_sections_grid_default_variant_class_when_unset(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "katib-sections-grid--default" in html


def test_sections_grid_column_count_emitted(tmp_path):
    """Column count drives the grid modifier class. 2 (default), 3, 4 supported."""
    for cols in (2, 3, 4):
        rfile = _inline_recipe(tmp_path, columns=cols)
        html, _ = compose(str(rfile), "en")
        assert f"katib-sections-grid__grid--cols-{cols}" in html


def test_sections_grid_default_columns_is_2(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "katib-sections-grid__grid--cols-2" in html


def test_sections_grid_raw_body_takes_precedence_over_body(tmp_path):
    """raw_body is trusted HTML (for cheatsheet's <dl>/<ul> card contents);
    should take precedence over body when both set."""
    rfile = tmp_path / "sg.yaml"
    rfile.write_text(
        "name: sg-precedence\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: sections-grid\n"
        "    inputs:\n"
        "      items:\n"
        "        - title: Card\n"
        "          body: PLAIN_TEXT\n"
        "          raw_body: \"<dl><dt>K</dt><dd>V</dd></dl>\"\n"
    )
    html, _ = compose(str(rfile), "en")
    assert "<dl>" in html
    assert "PLAIN_TEXT" not in html  # body suppressed


def test_sections_grid_optional_eyebrow_and_heading_and_card_eyebrow(tmp_path):
    """Grid-level eyebrow/heading optional; card-level eyebrow optional."""
    rfile = tmp_path / "sg.yaml"
    rfile.write_text(
        "name: sg-opt\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: sections-grid\n"
        "    variant: bordered\n"
        "    inputs:\n"
        "      eyebrow: CONTACTS\n"
        "      items:\n"
        "        - {eyebrow: \"Handing off\", title: \"Outgoing owner\", body: \"Available for 30 days.\"}\n"
        "        - {eyebrow: \"Taking over\", title: \"Incoming owner\", body: \"Primary POC.\"}\n"
    )
    html, _ = compose(str(rfile), "en")
    # Grid-level eyebrow rendered, heading element absent
    assert ">CONTACTS<" in html
    assert '<h2 class="katib-sections-grid__heading"' not in html
    # Card-level eyebrows rendered
    assert ">Handing off<" in html
    assert ">Taking over<" in html
    assert html.count('<div class="katib-sections-grid__card-eyebrow">') == 2


def test_sections_grid_page_break_inside_avoid_styles_present(tmp_path):
    """Each card should be marked page-break-inside: avoid (via CSS)."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # The CSS rule is emitted in the <style> block
    assert "page-break-inside: avoid" in html
