"""business-proposal-proposal recipe — ninth Phase-3 recipe.

Zero new components. data-table second-consumer validation within
24 hours (3 more production uses: 4-col deliverables, 4-col schedule,
3-col financial milestones). Completes the business-proposal domain
(letter Day 4 + one-pager Day 12 + proposal Day 14).

11 sections with 3 density-convention inline blocks (title page,
TOC, sign-row-in-acceptance). 5 × module numbered variant
(second at-scale use after white-paper Day 13's 6 instances).

Content adapted from v1-reference/domains/business-proposal/
templates/proposal.en.html. Placeholder prose preserved.

Renders to 5 pages under v2 placeholder prose; target_pages [5, 10],
page_limit 12. Real content will push to 6-10.

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
RECIPE_NAME = "business-proposal-proposal"


# ---------------------------------------------------------------- schema


def test_proposal_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_proposal_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_proposal_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [5, 10]
    assert r["page_limit"] == 12


def test_proposal_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 11
    components = [s["component"] for s in sections]
    assert components == [
        "module",       # 1. title page (inline)
        "module",       # 2. TOC (inline)
        "module",       # 3. Executive Summary (numbered)
        "module",       # 4. Program Scope intro (numbered)
        "data-table",   # 5. deliverables
        "module",       # 6. Delivery Timeline intro (numbered)
        "data-table",   # 7. schedule
        "module",       # 8. Investment & Terms intro (numbered)
        "data-table",   # 9. milestones
        "module",       # 10. Section 4 closing paragraph
        "module",       # 11. Acceptance (numbered) + inline sign-row
    ]


# ---------------------------------------------------------------- production proofs


def test_proposal_three_data_table_consumers():
    """data-table's 2nd/3rd/4th production consumers in one recipe.
    Validates the component across distinct column shapes."""
    r = load_recipe(RECIPE_NAME)
    tables = [s for s in r["sections"] if s["component"] == "data-table"]
    assert len(tables) == 3

    # Table 1 — deliverables (4 cols, 4 rows)
    t1 = tables[0]
    assert len(t1["inputs"]["columns"]) == 4
    assert len(t1["inputs"]["rows"]) == 4
    assert t1["inputs"]["caption"] == "Program modules and outcomes"

    # Table 2 — schedule (4 cols, 6 rows)
    t2 = tables[1]
    assert len(t2["inputs"]["columns"]) == 4
    assert len(t2["inputs"]["rows"]) == 6

    # Table 3 — milestones (3 cols, 4 rows — includes Total row)
    t3 = tables[2]
    assert len(t3["inputs"]["columns"]) == 3
    assert len(t3["inputs"]["rows"]) == 4
    # Total row workaround (v1 used colspan; v2 uses 3 explicit cells)
    assert t3["inputs"]["rows"][-1] == ["Total", "", "615,000"]


def test_proposal_five_numbered_module_sections():
    """5 numbered body sections (second at-scale use of module numbered
    variant after white-paper's 6)."""
    r = load_recipe(RECIPE_NAME)
    numbered = [s for s in r["sections"]
                if s["component"] == "module" and s.get("variant") == "numbered"]
    assert len(numbered) == 5
    numbers = [s["inputs"]["number"] for s in numbered]
    assert numbers == [1, 2, 3, 4, 5]
    titles = [s["inputs"]["title"] for s in numbered]
    assert titles == [
        "Executive Summary",
        "Program Scope",
        "Delivery Timeline",
        "Investment & Terms",
        "Acceptance",
    ]


def test_proposal_title_page_has_meta_block():
    """Title page is an inline-styled module containing eyebrow + h1 +
    subtitle + 4-item meta-block (Reference/Issued/Prepared by/For)."""
    r = load_recipe(RECIPE_NAME)
    title = r["sections"][0]
    assert title["component"] == "module"
    raw = title["inputs"]["raw_body"]
    assert "Commercial Proposal" in raw
    assert "Applied AI Training Program" in raw
    # Meta-block labels (4 pairs)
    for label in ("Reference", "Issued", "Prepared by", "For"):
        assert f">{label}<" in raw, f"meta label missing: {label}"
    # Page-break-after for title page
    assert "page-break-after: always" in raw


def test_proposal_toc_has_five_numbered_rows():
    """TOC is inline-styled (2 verified dependents — proposal + onboarding —
    below threshold; graduation deferred)."""
    r = load_recipe(RECIPE_NAME)
    toc = r["sections"][1]
    assert toc["component"] == "module"
    raw = toc["inputs"]["raw_body"]
    assert "Contents" in raw
    # & rendered as &amp; in the HTML entity form
    import html as _html
    decoded = _html.unescape(raw)
    for title in ("Executive Summary", "Program Scope", "Delivery Timeline",
                  "Investment & Terms", "Acceptance"):
        assert title in decoded, f"TOC entry missing: {title}"


def test_proposal_acceptance_has_inline_sign_row():
    """Acceptance section uses a module numbered with inline 3-box sign-row
    (Name & Title / Signature / Date). sign-row has 1 verified dependent —
    graduation deferred, inline."""
    r = load_recipe(RECIPE_NAME)
    acceptance = r["sections"][-1]
    assert acceptance["component"] == "module"
    assert acceptance.get("variant") == "numbered"
    assert acceptance["inputs"]["number"] == 5
    raw = acceptance["inputs"]["raw_body"]
    import html as _html
    decoded = _html.unescape(raw)
    for label in ("Name & Title", "Signature", "Date"):
        assert label in decoded, f"sign-row label missing: {label}"
    # Inline flex layout
    assert "display: flex" in raw


# ---------------------------------------------------------------- validation + content-lint


def test_proposal_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_proposal_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_proposal_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    # data-table appears 3 times (3 production uses)
    assert html.count("katib-data-table-wrap") == 3
    # module numbered — 5 instances
    assert html.count("katib-module--numbered") == 5


def test_proposal_pdf_within_target_pages(tmp_path):
    """target_pages [5, 10]; placeholder renders 5, real content pushes to 6-10."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "prop.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 5 <= len(reader.pages) <= 10


def test_proposal_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 proposal should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "prop.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Title page
    assert "COMMERCIAL PROPOSAL" in flat.upper()
    assert "Applied AI Training Program" in flat
    assert "PROP/2026/001" in flat
    assert "Jasem Al Neaimi" in flat
    assert "2026-04-24" in flat
    # TOC
    assert "Contents".upper() in flat.upper()
    # Body section titles (numbered)
    for title in ("Executive Summary", "Program Scope", "Delivery Timeline",
                  "Investment & Terms", "Acceptance"):
        assert title in flat, f"section title missing: {title}"
    # Exec summary
    assert "18 participants" in flat
    assert "AED 615,000" in flat
    assert "Hybrid Split" in flat
    # Scope table
    assert "Foundations" in flat
    assert "Agent Design" in flat
    assert "Production" in flat
    assert "Integration" in flat
    # Schedule table
    assert "Group A" in flat and "Group B" in flat
    assert "F2F (HQ)" in flat
    assert "Remote labs" in flat
    assert "Capstone" in flat
    # Milestones table
    assert "Kickoff" in flat
    assert "184,500" in flat
    assert "246,000" in flat
    assert "615,000" in flat
    # Acceptance
    assert "Countersign" in flat
    assert "Name" in flat  # sign-row labels
    assert "Signature" in flat
    assert "On behalf of the client" in flat


def test_proposal_three_captions_rendered():
    """All 3 data-tables have captions — regression guard for accessibility."""
    html, _ = compose(RECIPE_NAME, "en")
    assert html.count("<caption") == 3
    assert "Program modules and outcomes" in html
    assert "6-week schedule" in html
    assert "Payment milestones in AED" in html


def test_proposal_completes_business_proposal_domain():
    """Day 14 completes all 3 business-proposal recipes. Sentinel test —
    when this test file runs, the domain is structurally complete."""
    import os
    recipes_dir = REPO_ROOT / "recipes"
    business_recipes = sorted(
        f.name for f in recipes_dir.iterdir()
        if f.name.startswith("business-proposal")
    )
    assert business_recipes == [
        "business-proposal-letter.yaml",
        "business-proposal-one-pager.yaml",
        "business-proposal-proposal.yaml",
    ]


# ---------------------------------------------------------------- audit + registration


def test_proposal_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_proposal_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
