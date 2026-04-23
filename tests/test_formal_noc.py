"""formal-noc recipe — third Phase-3 recipe migration.

10 sections, 0 new components. Exercises Day-2, Day-5, Day-7 component
work in production:
- letterhead formal variant (Day 2) — austere organizational header
- module raw_body × 5 (doc-marker, opener, opening body, closing body,
  footer note) — 4 of these with inline-styled typographic shapes
  (banner labels, validity box, footer). First recipe to test the
  "inline-style budget scales with recipe density" convention.
- kv-list boxed variant (Day 7) — field-summary employee details
- callout neutral tone (Day 5) — purpose block
- multi-party-signature-block (Day 7) — 2-party HR-signatory layout
- module raw_body (inline-styled validity-line div with dashed border)

Content ported verbatim from v1-reference/domains/formal/templates/
noc.en.html. Placeholder-style template (v1's instructional prose
with square-bracket placeholders) preserved.

Renders to 2 pages under v2 defaults — v1 fit 1 page with 30mm margins;
v2 components add structural whitespace that pushes signatures + footer
to page 2. Documented in ADR Day 8 as acceptable visual divergence;
target_pages [1, 2] permits either outcome.

AR variant deferred — NOC is the expected first genuinely-bilingual
recipe (per Day 4 ADR entry), triggering the `inputs_by_lang` schema
design when that day arrives.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pypdf import PdfReader

from core import recipe_ops as ops
from core.compose import compose, load_recipe
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPE_NAME = "formal-noc"


# ---------------------------------------------------------------- schema


def test_noc_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_noc_en_only():
    """AR variant deferred until inputs_by_lang schema lands."""
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_noc_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 2]
    assert r["page_limit"] == 2


def test_noc_ten_sections_in_order():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 10
    components = [s["component"] for s in sections]
    assert components == [
        "letterhead",                       # 1. formal header
        "module",                           # 2. doc-marker
        "module",                           # 3. opener
        "module",                           # 4. opening body
        "kv-list",                          # 5. employee details
        "callout",                          # 6. purpose
        "module",                           # 7. validity line
        "module",                           # 8. closing body
        "multi-party-signature-block",      # 9. 2-party signature
        "module",                           # 10. footer note
    ]


# ---------------------------------------------------------------- Day-2/5/7 production proofs


def test_noc_uses_letterhead_formal_variant():
    """Day-2 letterhead formal variant in production."""
    r = load_recipe(RECIPE_NAME)
    header = r["sections"][0]
    assert header["component"] == "letterhead"
    assert header["variant"] == "formal"


def test_noc_uses_kv_list_boxed_variant():
    """Day-7 kv-list v0.2.0 boxed variant — first production consumer of the
    field-summary field-box-style inversion."""
    r = load_recipe(RECIPE_NAME)
    employee = r["sections"][4]
    assert employee["component"] == "kv-list"
    assert employee["variant"] == "boxed"
    assert len(employee["inputs"]["items"]) == 7


def test_noc_uses_multi_party_signature_block():
    """Day-7 multi-party-signature-block in production — first consumer."""
    r = load_recipe(RECIPE_NAME)
    sig = r["sections"][8]
    assert sig["component"] == "multi-party-signature-block"
    assert len(sig["inputs"]["parties"]) == 2


def test_noc_uses_callout_neutral_tone():
    """Day-5 callout neutral tone — second production consumer (cover-letter was first)."""
    r = load_recipe(RECIPE_NAME)
    purpose = r["sections"][5]
    assert purpose["component"] == "callout"
    assert purpose["inputs"]["tone"] == "neutral"


# ---------------------------------------------------------------- validation + content-lint


def test_noc_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_noc_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_noc_renders_en(tmp_path):
    html, _ = compose(RECIPE_NAME, "en")
    # Component marker classes for the 4 new production consumers
    assert "katib-letterhead--formal" in html
    assert "katib-kv-list--boxed" in html
    assert "katib-multi-party-signature-block" in html
    assert "katib-callout--neutral" in html


def test_noc_pdf_within_target_pages(tmp_path):
    """target_pages [1, 2]; v2 renders to 2 pages (v1 was 1 with 30mm margins)
    due to component-level whitespace. Architecturally acceptable; documented
    in ADR Day 8."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "noc.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 1 <= len(reader.pages) <= 2


def test_noc_renders_all_v1_content(tmp_path):
    """Every placeholder + fixed phrase from v1 NOC should appear in the
    rendered PDF. Whitespace collapsed to tolerate PDF line-wrapping."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "noc.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Letterhead
    assert "NOC/2026/042" in flat
    assert "23 April 2026" in flat
    # Banners
    assert "NO OBJECTION CERTIFICATE" in flat
    assert "TO WHOM IT MAY CONCERN" in flat
    # Opening body phrase
    assert "confirm that the following individual is currently employed" in flat
    # Employee-details placeholders (7 fields)
    for label in ("Name", "Nationality", "Passport No.", "Emirates ID",
                  "Position", "Date of Joining", "Employment Status"):
        assert label.upper() in flat.upper(), f"{label} missing"
    assert "[Full name as per passport]" in flat
    assert "Active — Full Time" in flat
    # Purpose block
    assert "Purpose of this letter" in flat
    assert "visa application to [country]" in flat
    # Validity
    assert "valid for [30 / 60 / 90] days" in flat
    # Closing paragraph
    assert "further verification or clarification" in flat
    # Signature
    assert "[Authorised signatory name]" in flat
    assert "Signature & company stamp" in flat
    # Footer
    assert "Unauthorised alteration or reproduction is prohibited" in flat


def test_noc_employee_details_has_seven_fields(tmp_path):
    """Regression guard — NOC's employee-details block is the shape that drove
    kv-list's boxed variant. Must render 7 field rows."""
    html, _ = compose(RECIPE_NAME, "en")
    # Each item renders as a <dt> + <dd> pair
    dt_count = html.count("<dt class=\"katib-kv-list__term\">")
    assert dt_count == 7


# ---------------------------------------------------------------- audit + registration


def test_noc_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_noc_audit_entry_exists():
    """build.py would refuse a recipe without an audit entry."""
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
