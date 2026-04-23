"""editorial-white-paper recipe — eighth Phase-3 recipe; first production
consumer of data-table (Day 13 new primitive).

12 sections, 1 new component (data-table). Production proofs:
- data-table default variant — FIRST PRODUCTION CONSUMER
- callout neutral tone — THIRD production consumer (cover-letter subject,
  NOC purpose, now abstract)
- pull-quote rule-leading variant — FIRST Phase-3 production consumer
  (was used in tutorial.yaml Phase-2 but this is first Phase-3 use)
- module numbered variant — 6 consumers in one recipe (sections 1-6)

Content adapted from v1-reference/domains/editorial/templates/
white-paper.en.html. Placeholder prose preserved.

Renders to 4 pages under v2 defaults; target_pages [4, 8], page_limit 10.

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
RECIPE_NAME = "editorial-white-paper"


# ---------------------------------------------------------------- schema


def test_white_paper_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_white_paper_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_white_paper_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [4, 8]
    assert r["page_limit"] == 10


def test_white_paper_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 12
    components = [s["component"] for s in sections]
    assert components == [
        "module",       # 1. title page (inline)
        "callout",      # 2. abstract (neutral)
        "module",       # 3. section 1 Introduction
        "module",       # 4. section 2 The State of the Problem
        "data-table",   # 5. indicator trends
        "module",       # 6. section 3 The Argument
        "pull-quote",   # 7. central claim
        "module",       # 8. section 4 Counterarguments
        "module",       # 9. section 5 Implications
        "module",       # 10. section 6 Conclusion
        "module",       # 11. footnotes (inline)
        "module",       # 12. about author (inline)
    ]


# ---------------------------------------------------------------- production proofs


def test_white_paper_first_data_table_consumer():
    """data-table Day-13 debut — first production consumer.
    5 columns (Indicator + 4 years), 3 rows, 4 numeric-aligned columns."""
    r = load_recipe(RECIPE_NAME)
    table = r["sections"][4]
    assert table["component"] == "data-table"
    assert len(table["inputs"]["columns"]) == 5
    # 4 numeric columns (2020, 2022, 2024, 2026)
    numeric_cols = [c for c in table["inputs"]["columns"] if c.get("align") == "num"]
    assert len(numeric_cols) == 4
    assert len(table["inputs"]["rows"]) == 3
    assert table["inputs"]["caption"] == "Indicator trends, 2020–2026"


def test_white_paper_third_callout_neutral_consumer():
    """callout neutral tone — third production consumer (cover-letter + NOC
    were prior)."""
    r = load_recipe(RECIPE_NAME)
    abstract = r["sections"][1]
    assert abstract["component"] == "callout"
    assert abstract["inputs"]["tone"] == "neutral"
    assert abstract["inputs"]["title"] == "Executive Summary"


def test_white_paper_uses_pull_quote_rule_leading():
    """pull-quote rule-leading variant — first Phase-3 production use."""
    r = load_recipe(RECIPE_NAME)
    pq = r["sections"][6]
    assert pq["component"] == "pull-quote"
    assert pq["variant"] == "rule-leading"
    assert pq["inputs"]["attribution"] == "The central claim of this paper"


def test_white_paper_six_numbered_module_sections():
    """Sections 1-6 use module numbered variant with sequential numbers."""
    r = load_recipe(RECIPE_NAME)
    numbered = [s for s in r["sections"] if s["component"] == "module" and s.get("variant") == "numbered"]
    assert len(numbered) == 6
    numbers = [s["inputs"]["number"] for s in numbered]
    assert numbers == [1, 2, 3, 4, 5, 6]
    titles = [s["inputs"]["title"] for s in numbered]
    assert titles == [
        "Introduction",
        "The State of the Problem",
        "The Argument",
        "Counterarguments & Limits",
        "Implications & Recommendations",
        "Conclusion",
    ]


# ---------------------------------------------------------------- validation + content-lint


def test_white_paper_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_white_paper_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_white_paper_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    assert "katib-data-table" in html
    assert "katib-callout--neutral" in html
    assert "katib-pullquote--rule-leading" in html
    assert "katib-module--numbered" in html


def test_white_paper_pdf_within_target_pages(tmp_path):
    """target_pages [4, 8]; renders to 4 at defaults with placeholder prose."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "wp.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 4 <= len(reader.pages) <= 8


def test_white_paper_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 white-paper should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "wp.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Title page (eyebrow is uppercased by inline CSS)
    assert "White Paper".upper() in flat.upper()
    assert "Primary Title" in flat
    assert "Jasem Al Neaimi" in flat
    assert "2026-04-24" in flat
    # Abstract
    assert "Executive Summary" in flat
    assert "thesis in one sentence" in flat
    # Numbered section titles
    for title in ("Introduction", "The State of the Problem", "The Argument",
                  "Counterarguments", "Implications", "Conclusion"):
        assert title in flat, f"section title missing: {title}"
    # Body phrases
    assert "opening paragraph" in flat
    assert "Evidence paragraph" in flat
    assert "compressed sentence" in flat
    assert "strongest objection" in flat
    assert "stakeholder group" in flat
    assert "most important takeaway" in flat
    # Data table
    assert "Indicator trends" in flat  # caption
    assert "2020" in flat and "2026" in flat
    assert "1,200" in flat
    assert "2,600" in flat
    assert "28%" in flat and "49%" in flat
    # Pull-quote
    assert "central claim of this paper" in flat
    # Footnotes
    assert "Notes" in flat.upper() or "NOTES" in flat
    # About author
    assert "About the Author" in flat or "ABOUT THE AUTHOR" in flat
    assert "jasem@jneaimi.com" in flat


def test_white_paper_data_table_has_five_columns_rendered():
    """Regression guard — data-table must render 5 <th> headers."""
    html, _ = compose(RECIPE_NAME, "en")
    # Count scope="col" (one per rendered header cell) — data-table has 5 cols
    data_table_section = html.split("katib-data-table-wrap")[1].split("</table>")[0]
    assert data_table_section.count('scope="col"') == 5


def test_white_paper_three_data_rows_rendered():
    """Regression guard — 3 data rows (Metric 1, 2, 3)."""
    html, _ = compose(RECIPE_NAME, "en")
    data_table_section = html.split("katib-data-table-wrap")[1].split("</table>")[0]
    # Each row has at least one <td>; count tbody rows via <tr> inside tbody
    tbody = data_table_section.split("<tbody")[1]
    assert tbody.count("<tr>") == 3


def test_white_paper_drop_cap_inline_styled():
    """First body section uses an inline-styled drop cap on its opening T."""
    html, _ = compose(RECIPE_NAME, "en")
    # Drop cap span with 28pt accent color
    assert 'font-size: 28pt' in html and 'color: var(--accent)' in html


# ---------------------------------------------------------------- audit + registration


def test_white_paper_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_white_paper_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
