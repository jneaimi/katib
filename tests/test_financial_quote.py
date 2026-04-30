"""financial-quote recipe — eleventh Phase-3 recipe; FIRST production consumer
of financial-summary compact variant (Day-15 built → Day-16 shipped,
24-hour ship discipline). Closes the financial domain.

9 sections, zero new components. Production proofs:
- financial-summary COMPACT variant — FIRST PRODUCTION CONSUMER (24-hour
  ship discipline from Day-15 default-variant debut).
- letterhead commercial — 2nd production use (validates Day-2 variant
  beyond the invoice 1-off).
- callout info tone — 2nd production consumer (after handoff Day-10).
- data-table dense with {text, sub} cells — 2nd production use of the
  Day-13 cell-mapping feature; 6th overall data-table consumer.
- sections-grid bordered — 3rd bordered consumer (invoice × 2 + quote × 1).
- kv-list boxed — 4th consumer (NOC + handoff + invoice + quote).
- module numbered — 3 uses in one recipe (Scope / Pricing / Acceptance),
  bringing numbered-module to its heaviest single-recipe deployment.

Content adapted from v1-reference/domains/financial/templates/quote.en.html.
Placeholder prose preserved.

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
RECIPE_NAME = "financial-quote"


# ---------------------------------------------------------------- schema


def test_quote_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "1.0.1"


def test_quote_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_quote_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 2]
    assert r["page_limit"] == 2


def test_quote_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 9
    components = [s["component"] for s in sections]
    assert components == [
        "letterhead",         # 1. commercial masthead
        "kv-list",            # 2. meta strip (boxed)
        "callout",            # 3. Prepared For (info)
        "module",             # 4. 1 · Scope (numbered)
        "module",             # 5. 2 · Pricing header (numbered)
        "data-table",         # 6. line items (dense)
        "financial-summary",  # 7. totals (compact)
        "sections-grid",      # 8. Terms 2x2 (bordered)
        "module",             # 9. 3 · Acceptance (numbered)
    ]


# ---------------------------------------------------------------- production proofs


def test_quote_uses_letterhead_commercial():
    """2nd production use of letterhead commercial (after invoice Day-15)."""
    r = load_recipe(RECIPE_NAME)
    header = r["sections"][0]
    assert header["component"] == "letterhead"
    assert header["variant"] == "commercial"
    assert header["inputs"]["doc_title"] == "Quotation"
    assert header["inputs"]["reference_code"] == "QTE-2026-0042"


def test_quote_first_financial_summary_compact_consumer():
    """FIRST PRODUCTION CONSUMER of financial-summary compact variant —
    24-hour ship discipline from Day-15 default-variant debut.
    3 rows with the last as variant: total."""
    r = load_recipe(RECIPE_NAME)
    totals = r["sections"][6]
    assert totals["component"] == "financial-summary"
    assert totals["variant"] == "compact"
    assert totals["inputs"]["currency"] == "AED"
    rows = totals["inputs"]["rows"]
    assert len(rows) == 3
    # Last row must be variant: total
    assert rows[-1]["variant"] == "total"
    assert rows[-1]["label"] == "TOTAL"
    assert rows[-1]["value"] == "50,400.00"
    # Non-total rows don't carry variant
    for r_ in rows[:-1]:
        assert "variant" not in r_


def test_quote_data_table_uses_text_sub_cells():
    """2nd production use of data-table's {text, sub} cell feature
    (first was invoice Day-15)."""
    r = load_recipe(RECIPE_NAME)
    line_items = r["sections"][5]
    assert line_items["component"] == "data-table"
    assert line_items["variant"] == "dense"
    # 5 columns (# / Description / Qty / Unit Price / Total)
    assert len(line_items["inputs"]["columns"]) == 5
    # 3 rows
    rows = line_items["inputs"]["rows"]
    assert len(rows) == 3
    # Every row's 2nd cell (description) is a mapping with {text, sub}
    for row in rows:
        desc_cell = row[1]
        assert isinstance(desc_cell, dict)
        assert "text" in desc_cell
        assert "sub" in desc_cell


def test_quote_uses_callout_info_tone():
    """2nd production consumer of callout info tone (after handoff Day-10)."""
    r = load_recipe(RECIPE_NAME)
    client = r["sections"][2]
    assert client["component"] == "callout"
    assert client["inputs"]["tone"] == "info"
    assert client["inputs"]["title"] == "Prepared For"


def test_quote_uses_kv_list_boxed_for_meta_strip():
    """4th production consumer of kv-list boxed (NOC + handoff + invoice + quote)."""
    r = load_recipe(RECIPE_NAME)
    meta = r["sections"][1]
    assert meta["component"] == "kv-list"
    assert meta["variant"] == "boxed"
    items = meta["inputs"]["items"]
    assert len(items) == 4
    terms = [i["term"] for i in items]
    assert terms == ["Issued", "Valid Until", "Currency", "Prepared By"]


def test_quote_sections_grid_bordered_third_consumer():
    """sections-grid bordered — 3rd consumer (invoice had 2 instances).
    Quote uses one 2x2 instance for Terms (Payment / Timeline / Validity / T&C)."""
    r = load_recipe(RECIPE_NAME)
    grids = [s for s in r["sections"]
             if s["component"] == "sections-grid" and s.get("variant") == "bordered"]
    assert len(grids) == 1
    grid = grids[0]
    assert grid["inputs"]["columns"] == 2
    assert len(grid["inputs"]["items"]) == 4
    titles = [i["title"] for i in grid["inputs"]["items"]]
    # "Terms &amp; Conditions" in YAML renders as "Terms & Conditions"
    assert titles[:3] == ["Payment Schedule", "Timeline", "Validity"]
    assert "Terms" in titles[3]


def test_quote_uses_three_numbered_modules():
    """module numbered variant — 3 uses in one recipe (heaviest deployment).
    Covers Scope (1) / Pricing (2) / Acceptance (3)."""
    r = load_recipe(RECIPE_NAME)
    numbered = [s for s in r["sections"]
                if s["component"] == "module" and s.get("variant") == "numbered"]
    assert len(numbered) == 3
    numbers = [s["inputs"]["number"] for s in numbered]
    assert numbers == [1, 2, 3]
    titles = [s["inputs"]["title"] for s in numbered]
    assert titles == ["Scope", "Pricing", "Acceptance"]


# ---------------------------------------------------------------- validation + content-lint


def test_quote_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_quote_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_quote_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    assert "katib-letterhead--commercial" in html
    assert "katib-financial-summary--compact" in html
    assert "katib-financial-summary__row--total" in html
    assert "katib-data-table--dense" in html
    assert "katib-sections-grid--bordered" in html
    assert "katib-callout--info" in html


def test_quote_pdf_within_target_pages(tmp_path):
    """target_pages [1, 2]; renders to 2 pages under v2 defaults."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "q.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 1 <= len(reader.pages) <= 2


def test_quote_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 quote should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "q.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Letterhead
    assert "QUOTATION" in flat.upper()
    assert "QTE-2026-0042" in flat
    assert "Acme | Katib" in flat or "ACME | KATIB" in flat.upper()
    # Meta strip (labels uppercased by kv-list boxed CSS)
    for label in ("Issued", "Valid Until", "Currency", "Prepared By"):
        assert label.upper() in flat.upper(), f"meta label missing: {label}"
    assert "2026-04-24" in flat
    assert "2026-05-24" in flat
    assert "AED" in flat
    # Prepared For client block
    assert "Prepared For" in flat
    # Scope section
    assert "Scope" in flat
    assert "Inclusions" in flat
    assert "Exclusions" in flat
    # Pricing section
    assert "Pricing" in flat
    # Line items (data-table header "Description")
    assert "DESCRIPTION" in flat.upper()
    assert "Phase / service 1" in flat
    assert "Phase / service 2" in flat
    assert "Optional add-on" in flat
    assert "15,000.00" in flat
    assert "25,000.00" in flat
    assert "8,000.00" in flat
    # Totals
    assert "Subtotal" in flat
    assert "48,000.00" in flat
    assert "2,400.00" in flat
    assert "50,400.00" in flat
    assert "TOTAL AED" in flat or ("TOTAL" in flat and "AED" in flat)
    # Terms grid
    assert "Payment Schedule" in flat
    assert "Timeline" in flat
    assert "Validity" in flat
    # "Terms & Conditions" rendered from "Terms &amp; Conditions" YAML
    assert "Terms" in flat
    # Acceptance
    assert "Acceptance" in flat
    assert "alex@acme.test" in flat
    assert "Alex Acme" in flat
    # Signature labels uppercased by inline CSS
    assert "FOR ACME" in flat.upper()
    assert "ACCEPTED BY CLIENT" in flat.upper()


def test_quote_line_items_has_three_rows_with_sub_cells():
    """Regression guard — line-items must render 3 rows, each with a
    cell-sub span inside the description column."""
    html, _ = compose(RECIPE_NAME, "en")
    # 3 expected (one per row's description)
    assert html.count('class="katib-data-table__cell-sub"') == 3


def test_quote_totals_has_accent_total_row():
    """The Total row carries the --total modifier class in the rendered HTML."""
    html, _ = compose(RECIPE_NAME, "en")
    assert 'class="katib-financial-summary__row katib-financial-summary__row--total"' in html


def test_quote_compact_variant_class_emitted():
    """financial-summary compact variant modifier must be in the rendered HTML."""
    html, _ = compose(RECIPE_NAME, "en")
    assert "katib-financial-summary--compact" in html


def test_quote_has_three_numbered_modules_in_html():
    """3 numbered modules rendered — Scope, Pricing, Acceptance.
    Count the numbered-variant modifier class at element level."""
    html, _ = compose(RECIPE_NAME, "en")
    # Each numbered module emits a section with the modifier class
    # Use element-form assertion (avoid CSS-rule false matches)
    assert html.count('katib-module katib-module--numbered') == 3


# ---------------------------------------------------------------- audit + registration


def test_quote_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_quote_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
