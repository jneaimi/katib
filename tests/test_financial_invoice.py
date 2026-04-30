"""financial-invoice recipe — tenth Phase-3 recipe; first production consumer
of financial-summary (Day 15 new component) AND letterhead commercial variant
(Day 2 built, never used in production until now).

8 sections, 1 new component. Production proofs:
- financial-summary default — FIRST PRODUCTION CONSUMER
- letterhead commercial variant — FIRST PRODUCTION CONSUMER (Day-2 variant
  waited ~13 days for first real use)
- data-table dense with {text, sub} cells — FIRST PRODUCTION USE of the
  cell-mapping feature Day-13 built specifically for invoice. 5th overall
  production use of data-table.
- sections-grid bordered variant — FIRST PRODUCTION CONSUMER (prior
  consumers: cheatsheet dense, one-pager default, proposal default×3).
  Two uses in this recipe: Bill From/Bill To parties + Payment Terms/
  Bank Details.
- kv-list boxed — third production consumer (after NOC + handoff)
- callout neutral — 4th production consumer

Content adapted from v1-reference/domains/financial/templates/
invoice.en.html. Placeholder prose preserved.

Renders to 2 pages under v2 defaults; target_pages [1, 2], page_limit 2.

AR variant deferred — NOC remains designated first bilingual recipe.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pypdf import PdfReader

from core import recipe_ops as ops
from core.compose import compose, load_recipe
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPE_NAME = "financial-invoice"


# ---------------------------------------------------------------- schema


def test_invoice_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "1.0.1"


def test_invoice_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_invoice_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 2]
    assert r["page_limit"] == 2


def test_invoice_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 8
    components = [s["component"] for s in sections]
    assert components == [
        "letterhead",         # 1. commercial masthead
        "sections-grid",      # 2. Bill From / Bill To (bordered)
        "kv-list",            # 3. 4-field meta strip (boxed)
        "data-table",         # 4. line items (dense)
        "financial-summary",  # 5. totals
        "callout",            # 6. amount in words (neutral)
        "sections-grid",      # 7. payment + bank (bordered)
        "module",             # 8. footer (inline)
    ]


# ---------------------------------------------------------------- production proofs


def test_invoice_uses_letterhead_commercial_variant():
    """Day-2 commercial variant finally hits production (Day-8 NOC used formal;
    this is the first commercial use)."""
    r = load_recipe(RECIPE_NAME)
    header = r["sections"][0]
    assert header["component"] == "letterhead"
    assert header["variant"] == "commercial"
    assert header["inputs"]["doc_title"] == "Tax Invoice"


def test_invoice_first_financial_summary_consumer():
    """Day-15 financial-summary debut — first production consumer.
    4 rows with the last as variant: total."""
    r = load_recipe(RECIPE_NAME)
    totals = r["sections"][4]
    assert totals["component"] == "financial-summary"
    assert totals["inputs"]["currency"] == "AED"
    rows = totals["inputs"]["rows"]
    assert len(rows) == 4
    # Last row must be variant: total
    assert rows[-1]["variant"] == "total"
    assert rows[-1]["label"] == "TOTAL"
    # Non-total rows don't carry variant
    for r_ in rows[:-1]:
        assert "variant" not in r_


def test_invoice_data_table_uses_text_sub_cells():
    """First production use of data-table's {text, sub} cell feature —
    built Day 13 specifically for invoice's description column."""
    r = load_recipe(RECIPE_NAME)
    line_items = r["sections"][3]
    assert line_items["component"] == "data-table"
    assert line_items["variant"] == "dense"
    # 7 columns (# / Description / Qty / Unit / VAT% / VAT / Total)
    assert len(line_items["inputs"]["columns"]) == 7
    # 3 rows
    rows = line_items["inputs"]["rows"]
    assert len(rows) == 3
    # Every row's 2nd cell (description) is a mapping with {text, sub}
    for row in rows:
        desc_cell = row[1]
        assert isinstance(desc_cell, dict)
        assert "text" in desc_cell
        assert "sub" in desc_cell


def test_invoice_uses_kv_list_boxed_for_meta_strip():
    """Third production consumer of kv-list boxed (NOC field-summary,
    handoff status-grid, now invoice meta strip)."""
    r = load_recipe(RECIPE_NAME)
    meta = r["sections"][2]
    assert meta["component"] == "kv-list"
    assert meta["variant"] == "boxed"
    items = meta["inputs"]["items"]
    assert len(items) == 4
    terms = [i["term"] for i in items]
    assert terms == ["Invoice Date", "Supply Date", "Due Date", "Currency"]


def test_invoice_sections_grid_bordered_first_consumer():
    """sections-grid bordered variant — first production consumer.
    Two instances in this recipe: Bill From/Bill To + Payment Terms/Bank Details."""
    r = load_recipe(RECIPE_NAME)
    grids = [s for s in r["sections"]
             if s["component"] == "sections-grid" and s.get("variant") == "bordered"]
    assert len(grids) == 2
    # Both are 2-col
    for g in grids:
        assert g["inputs"]["columns"] == 2


def test_invoice_fourth_callout_neutral_consumer():
    """callout neutral — fourth production consumer (cover-letter subject,
    NOC purpose, white-paper abstract, now invoice amount-in-words)."""
    r = load_recipe(RECIPE_NAME)
    amount_words = r["sections"][5]
    assert amount_words["component"] == "callout"
    assert amount_words["inputs"]["tone"] == "neutral"
    assert amount_words["inputs"]["title"] == "Amount in Words"


# ---------------------------------------------------------------- validation + content-lint


def test_invoice_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_invoice_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_invoice_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    assert "katib-letterhead--commercial" in html
    assert "katib-financial-summary" in html
    assert "katib-financial-summary__row--total" in html
    assert "katib-data-table--dense" in html
    assert "katib-sections-grid--bordered" in html


def test_invoice_pdf_within_target_pages(tmp_path):
    """target_pages [1, 2]; renders to 2 pages given content density."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "inv.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 1 <= len(reader.pages) <= 2


def test_invoice_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 invoice should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "inv.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Letterhead (doc_title uppercased by letterhead commercial variant CSS)
    assert "Tax Invoice".upper() in flat.upper()
    assert "INV-2026-0042" in flat
    assert "Acme | Katib" in flat or "ACME | KATIB" in flat.upper()
    # Parties
    assert "Bill From".upper() in flat.upper()
    assert "Bill To".upper() in flat.upper()
    assert "TRN" in flat
    assert "100000000000003" in flat
    assert "100000000000004" in flat
    # Meta strip (labels uppercased by kv-list boxed)
    for label in ("Invoice Date", "Supply Date", "Due Date", "Currency"):
        assert label.upper() in flat.upper(), f"meta label missing: {label}"
    assert "2026-04-24" in flat
    assert "2026-05-24" in flat
    assert "AED" in flat
    # Line items (data-table header "Description")
    assert "DESCRIPTION" in flat.upper()
    assert "Service / product name" in flat
    assert "zero-rated example" in flat
    assert "10,000.00" in flat
    assert "17,000.00" in flat or "17,600.00" in flat
    # Totals box
    assert "Subtotal" in flat
    assert "TOTAL AED" in flat or ("TOTAL" in flat and "AED" in flat)
    assert "17,600.00" in flat
    # Amount in Words
    assert "Amount in Words" in flat
    assert "Seventeen Thousand" in flat
    # Payment + bank
    assert "Payment Terms" in flat
    assert "Bank Details" in flat
    assert "IBAN" in flat
    # Footer
    assert "Thank you for your business" in flat
    assert "VAT Law" in flat
    assert "Authorised signatory" in flat


def test_invoice_line_items_has_three_rows_with_sub_cells():
    """Regression guard — line-items must render 3 rows, each with a
    cell-sub span inside the description column (invoice-specific feature)."""
    html, _ = compose(RECIPE_NAME, "en")
    # The data-table section is identifiable by --dense class
    # Count cell-sub spans: 3 expected (one per row's description)
    assert html.count('class="katib-data-table__cell-sub"') == 3


def test_invoice_totals_has_accent_total_row():
    """The Total row carries the --total modifier class in the rendered HTML."""
    html, _ = compose(RECIPE_NAME, "en")
    assert 'class="katib-financial-summary__row katib-financial-summary__row--total"' in html


# ---------------------------------------------------------------- audit + registration


def test_invoice_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_invoice_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
