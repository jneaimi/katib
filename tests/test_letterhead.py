"""letterhead section — schema invariants + render + variant behavior.

Phase 3 Day 2 component. Second of the 6 genuinely-new Phase-3 components.
Dependents: business-proposal/letter, business-proposal/one-pager,
formal/noc, financial/invoice, financial/quote.

Architectural role: header strip above body content on page 1 — distinct
from `front-matter` (which consumes the whole page via break_after: always).
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_letterhead_loads_against_schema():
    c = load_component("letterhead")
    assert c["tier"] == "section"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_letterhead_variants_declared():
    c = load_component("letterhead")
    variants = c.get("variants", [])
    # default is implicit (no declaration needed) — only non-default variants declared
    assert "formal" in variants
    assert "commercial" in variants


def test_letterhead_company_required():
    c = load_component("letterhead")
    company_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "company" in inp),
        None,
    )
    assert company_decl is not None
    assert company_decl["required"] is True


def test_letterhead_token_contract():
    c = load_component("letterhead")
    required = set(c["requires"]["tokens"])
    # Styles use accent (border), text (company on formal), text_secondary (ref), text_tertiary (date)
    assert {"accent", "text", "text_secondary", "text_tertiary"}.issubset(required)
    # border was pruned — must NOT re-enter unless styles.css uses it
    assert "border" not in required


def test_letterhead_does_not_force_page_break():
    """Contract: letterhead must NOT set break_after — that's front-matter's job.
    Regression guard against anyone promoting letterhead to title-page role."""
    c = load_component("letterhead")
    page_behavior = c.get("page_behavior", {})
    assert page_behavior.get("break_after") != "always"


def test_letterhead_declares_logo_brand_field():
    c = load_component("letterhead")
    brand_fields = c.get("requires", {}).get("brand_fields", [])
    assert "logo.primary" in brand_fields


# ---------------------------------------------------------------- render


def _inline_recipe(
    tmp_path: Path,
    *,
    variant: str | None = None,
    lang: str = "en",
    doc_title: str | None = None,
    meta_lines: list[str] | None = None,
) -> Path:
    variant_line = f"    variant: {variant}\n" if variant else ""
    doc_title_line = f"      doc_title: \"{doc_title}\"\n" if doc_title else ""
    meta_lines_block = ""
    if meta_lines:
        meta_lines_block = "      meta_lines:\n"
        for line in meta_lines:
            meta_lines_block += f"        - \"{line}\"\n"
    rfile = tmp_path / "lh.yaml"
    rfile.write_text(
        "name: lh-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: letterhead\n"
        + variant_line +
        "    inputs:\n"
        '      company: "Acme | Katib"\n'
        '      reference_code: "KATIB-2026-001"\n'
        '      date: "23 April 2026"\n'
        + doc_title_line
        + meta_lines_block
    )
    return rfile


def test_letterhead_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # 2-col bar structure present
    assert "katib-letterhead__bar" in html
    assert "katib-letterhead__lead" in html
    assert "katib-letterhead__meta" in html
    # Content rendered
    assert "Acme | Katib" in html
    assert "KATIB-2026-001" in html
    assert "23 April 2026" in html
    # Default variant class emitted
    assert "katib-letterhead--default" in html


def test_letterhead_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    # reference_code explicitly forced LTR inside RTL template
    assert 'class="katib-letterhead__ref" dir="ltr"' in html


def test_letterhead_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "lh.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 3000


def test_letterhead_formal_variant(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="formal", doc_title="NO OBJECTION CERTIFICATE")
    html, _ = compose(str(rfile), "en")
    assert "katib-letterhead--formal" in html
    assert "katib-letterhead__doc-title" in html
    assert "NO OBJECTION CERTIFICATE" in html


def test_letterhead_commercial_variant(tmp_path):
    rfile = _inline_recipe(tmp_path, variant="commercial", doc_title="INVOICE")
    html, _ = compose(str(rfile), "en")
    assert "katib-letterhead--commercial" in html
    assert "INVOICE" in html


def test_letterhead_meta_lines_rendered_in_order(tmp_path):
    rfile = _inline_recipe(
        tmp_path,
        meta_lines=["Due: 30 days from issue", "Strictly Confidential"],
    )
    html, _ = compose(str(rfile), "en")
    assert "Due: 30 days from issue" in html
    assert "Strictly Confidential" in html
    # Order preserved
    due_idx = html.index("Due: 30 days from issue")
    conf_idx = html.index("Strictly Confidential")
    assert due_idx < conf_idx


def test_letterhead_doc_title_optional(tmp_path):
    """doc_title is optional — default variant should render cleanly without it."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # No doc-title element when not provided
    assert '<div class="katib-letterhead__doc-title"' not in html


def test_letterhead_logo_omitted_when_no_brand(tmp_path):
    """Without a brand profile, logo.primary is None — image tag must not render.
    The class name appears in the inlined <style> block regardless; we check
    for the actual <img> element instead."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert '<img class="katib-letterhead__logo"' not in html


# ---------------------------------------------------------------- hygiene


def test_letterhead_styles_use_tokens_only():
    css = (REPO_ROOT / "components" / "sections" / "letterhead" / "styles.css").read_text()
    import re
    hex_refs = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
    assert hex_refs == [], f"hex colors in styles.css: {hex_refs}"


def test_letterhead_templates_share_semantic_structure():
    """EN and AR share the semantic skeleton; only `dir="rtl"` differs on the root."""
    base = REPO_ROOT / "components" / "sections" / "letterhead"
    en = (base / "en.html").read_text()
    ar = (base / "ar.html").read_text()
    for token in (
        "<header",
        "katib-letterhead__bar",
        "katib-letterhead__lead",
        "katib-letterhead__meta",
        "katib-letterhead__company",
    ):
        assert token in en, f"{token} missing from en.html"
        assert token in ar, f"{token} missing from ar.html"
    assert 'dir="rtl"' in ar
    # EN should NOT have an unconditional dir="rtl" on the root; the ref field
    # DOES get dir="ltr" in AR only (to keep codes LTR inside RTL).
    import re
    en_root_match = re.search(r'<section[^>]*class="katib-section katib-letterhead[^"]*"[^>]*>', en)
    assert en_root_match is not None
    assert 'dir="rtl"' not in en_root_match.group(0)
