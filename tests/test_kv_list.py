"""kv-list section — schema invariants + render + variant behavior.

Phase 3 Day 1 component. First of the 5 genuinely-new components powering
the Phase 3 recipe migration. Dependents: cheatsheet, katib-walkthrough,
service-agreement, white-paper, quote.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_kv_list_loads_against_schema():
    c = load_component("kv-list")
    assert c["tier"] == "section"
    assert c["version"] == "0.2.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_kv_list_variants_declared():
    c = load_component("kv-list")
    variants = c.get("variants", [])
    assert "dense" in variants
    assert "spacious" in variants


def test_kv_list_items_required():
    c = load_component("kv-list")
    items_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "items" in inp),
        None,
    )
    assert items_decl is not None
    assert items_decl["required"] is True


def test_kv_list_token_contract():
    c = load_component("kv-list")
    required = set(c["requires"]["tokens"])
    # The three tokens the stylesheet actually references
    assert {"text", "text_secondary", "border"}.issubset(required)
    # text_tertiary was pruned — must NOT re-enter unless styles.css uses it
    assert "text_tertiary" not in required


# ---------------------------------------------------------------- render


def _inline_recipe(tmp_path: Path, variant: str | None = None, lang: str = "en") -> Path:
    variant_line = f"    variant: {variant}\n" if variant else ""
    rfile = tmp_path / "kv.yaml"
    rfile.write_text(
        "name: kv-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: kv-list\n"
        + variant_line +
        "    inputs:\n"
        "      eyebrow: Defined Terms\n"
        "      heading: Interpretation\n"
        "      items:\n"
        '        - {term: Agreement, value: "This MoU and attached schedules."}\n'
        '        - {term: Effective Date, value: "Date of the last signature."}\n'
        '        - {term: Party, value: "Either signatory; together, the Parties."}\n'
    )
    return rfile


def test_kv_list_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Semantic dl/dt/dd preserved
    assert "<dl" in html
    assert "<dt" in html
    assert "<dd" in html
    # Terms + values present in order
    assert "Agreement" in html
    assert "Effective Date" in html
    assert "Either signatory" in html
    # Heading + eyebrow emitted
    assert "Interpretation" in html
    assert "Defined Terms" in html


def test_kv_list_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    assert "<dl" in html


def test_kv_list_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "kv.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 4000


def test_kv_list_dense_variant_class_emitted(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="dense")
    html, _ = compose(str(rfile), "en")
    assert "katib-kv-list--dense" in html


def test_kv_list_spacious_variant_class_emitted(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="spacious")
    html, _ = compose(str(rfile), "en")
    assert "katib-kv-list--spacious" in html


def test_kv_list_default_variant_class_when_unset(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "katib-kv-list--default" in html


def test_kv_list_eyebrow_and_heading_optional(tmp_path):
    """Both heading and eyebrow are optional — recipe should render without either."""
    rfile = tmp_path / "kv-bare.yaml"
    rfile.write_text(
        "name: kv-bare\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: kv-list\n"
        "    inputs:\n"
        "      items:\n"
        '        - {term: Foo, value: Bar}\n'
        '        - {term: Baz, value: Qux}\n'
    )
    html, _ = compose(str(rfile), "en")
    assert "Foo" in html
    assert "Bar" in html
    assert "<dl" in html
    # No h3.katib-kv-list__heading element when heading is unset
    # (the class name appears in the inlined <style> block — we check the element instead)
    assert '<h3 class="katib-kv-list__heading"' not in html
    # No eyebrow div when eyebrow is unset
    assert 'katib-eyebrow--muted" lang="en"' not in html


# ---------------------------------------------------------------- hygiene


def test_kv_list_styles_use_tokens_only():
    css = (REPO_ROOT / "components" / "sections" / "kv-list" / "styles.css").read_text()
    # No hex colors leaked into the stylesheet — every color routes via var(--...)
    import re
    hex_refs = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
    assert hex_refs == [], f"hex colors in styles.css: {hex_refs}"


def test_kv_list_templates_share_semantic_structure():
    """EN and AR templates must share semantic skeleton (dl/dt/dd) — only
    direction attributes differ. Protects against accidental drift when
    adding new props."""
    base = REPO_ROOT / "components" / "sections" / "kv-list"
    en = (base / "en.html").read_text()
    ar = (base / "ar.html").read_text()
    for token in ("<dl", "<dt", "<dd", "katib-kv-list__grid", "katib-kv-list__term", "katib-kv-list__value"):
        assert token in en, f"{token} missing from en.html"
        assert token in ar, f"{token} missing from ar.html"
    # AR must declare RTL; EN must not
    assert 'dir="rtl"' in ar
    assert 'dir="rtl"' not in en
