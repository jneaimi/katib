"""tutorial-onboarding recipe — fourteenth Phase-3 recipe.

**Day-13 data-table triage prediction FULFILLED.** data-table was built
Day 13 with onboarding listed as a verified dependent ("3-col text-only
windows" — 30/60/90-day milestone table). 7-day build-to-consumer gap.

Zero-new-component day. 26 sections, 8 components, 3 inline density blocks
(TOC + accounts checklist + combined 5-day checklists).

Production proofs:
- data-table default — 7TH production consumer (Day-13 triage prediction)
- tutorial-step — 2ND production consumer (first was tutorial-how-to Day 9;
  11-day wait between consumers validates primitive's reuse value)
- callout tip — 2nd production consumer (first: tutorial-how-to Day 9)
- callout warn — 2nd production consumer (first: tutorial-how-to Day 9)
- cover-page minimalist-typographic — 4th production use
- sections-grid bordered cols=2 — 4th + 5th consumers (2 uses in recipe)
- module (plain + eyebrow for section dividers) — 5 dividers Parts I-IV + Closing

Content adapted from v1-reference/domains/tutorial/templates/onboarding.en.html.
Placeholder prose preserved.

Renders to 5 pages; target_pages [3, 6], page_limit 6.

AR variant deferred — pending inputs_by_lang schema resolution.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pypdf import PdfReader

from core import recipe_ops as ops
from core.compose import compose, load_recipe
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPE_NAME = "tutorial-onboarding"


# ---------------------------------------------------------------- schema


def test_onboarding_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_onboarding_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_onboarding_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [3, 6]
    assert r["page_limit"] == 6


def test_onboarding_has_twenty_six_sections():
    r = load_recipe(RECIPE_NAME)
    assert len(r["sections"]) == 26


def test_onboarding_component_mix():
    """26 sections = 17 module + 2 sections-grid + 3 tutorial-step + 2 callout
    + 1 cover-page + 1 data-table."""
    r = load_recipe(RECIPE_NAME)
    from collections import Counter
    counts = Counter(s["component"] for s in r["sections"])
    assert counts["module"] == 17
    assert counts["sections-grid"] == 2
    assert counts["tutorial-step"] == 3
    assert counts["callout"] == 2
    assert counts["cover-page"] == 1
    assert counts["data-table"] == 1


# ---------------------------------------------------------------- production proofs


def test_onboarding_cover_uses_minimalist_typographic():
    """4th production use of cover-page minimalist-typographic variant."""
    r = load_recipe(RECIPE_NAME)
    cover = r["sections"][0]
    assert cover["component"] == "cover-page"
    assert cover["variant"] == "minimalist-typographic"
    assert cover["inputs"]["eyebrow"] == "Onboarding"


def test_onboarding_seventh_data_table_consumer():
    """Day-13 TRIAGE PREDICTION FULFILLED: data-table was built for onboarding's
    3-col text-only windows. 7-day build-to-consumer gap."""
    r = load_recipe(RECIPE_NAME)
    tables = [s for s in r["sections"] if s["component"] == "data-table"]
    assert len(tables) == 1
    table = tables[0]
    # 3 columns: Window / Focus / Signal of success
    assert len(table["inputs"]["columns"]) == 3
    col_labels = [c["label"] for c in table["inputs"]["columns"]]
    assert col_labels == ["Window", "Focus", "Signal of success"]
    # 3 rows: Days 1-30, 31-60, 61-90
    assert len(table["inputs"]["rows"]) == 3
    first_cells = [row[0] for row in table["inputs"]["rows"]]
    assert first_cells == ["Days 1–30", "Days 31–60", "Days 61–90"]


def test_onboarding_uses_three_tutorial_steps():
    """2nd production consumer of tutorial-step (first: tutorial-how-to Day 9).
    3 consecutive steps for Software to install section."""
    r = load_recipe(RECIPE_NAME)
    steps = [s for s in r["sections"] if s["component"] == "tutorial-step"]
    assert len(steps) == 3
    numbers = [s["inputs"]["number"] for s in steps]
    assert numbers == [1, 2, 3]


def test_onboarding_uses_callout_tip():
    """2nd production consumer of callout tip tone (after tutorial-how-to Day 9).
    "Why this matters" async-first reinforcement."""
    r = load_recipe(RECIPE_NAME)
    tips = [s for s in r["sections"]
            if s["component"] == "callout" and s["inputs"].get("tone") == "tip"]
    assert len(tips) == 1
    assert tips[0]["inputs"]["title"] == "Why this matters"


def test_onboarding_uses_callout_warn():
    """2nd production consumer of callout warn tone (after tutorial-how-to Day 9).
    "Security basics" 2FA reinforcement."""
    r = load_recipe(RECIPE_NAME)
    warns = [s for s in r["sections"]
             if s["component"] == "callout" and s["inputs"].get("tone") == "warn"]
    assert len(warns) == 1
    assert warns[0]["inputs"]["title"] == "Security basics"


def test_onboarding_uses_two_sections_grid_bordered():
    """4th + 5th production consumer of sections-grid bordered cols=2.
    Stakeholders (Part II) + Who-to-ask (Closing) cards."""
    r = load_recipe(RECIPE_NAME)
    grids = [s for s in r["sections"]
             if s["component"] == "sections-grid" and s.get("variant") == "bordered"]
    assert len(grids) == 2
    for grid in grids:
        assert grid["inputs"]["columns"] == 2
        assert len(grid["inputs"]["items"]) == 4


def test_onboarding_section_divider_pattern():
    """5 section dividers (Part I-IV + Closing) use module plain with
    eyebrow + title + intro. Validates module's eyebrow input as
    section-separator pattern."""
    r = load_recipe(RECIPE_NAME)
    dividers = [
        s for s in r["sections"]
        if s["component"] == "module"
        and "eyebrow" in s.get("inputs", {})
        and s["inputs"].get("eyebrow", "").startswith(("Part", "Closing"))
    ]
    assert len(dividers) == 5
    eyebrows = [d["inputs"]["eyebrow"] for d in dividers]
    assert eyebrows == ["Part I", "Part II", "Part III", "Part IV", "Closing"]


# ---------------------------------------------------------------- validation + content-lint


def test_onboarding_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_onboarding_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_onboarding_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    # Critical marker classes
    assert "katib-data-table" in html
    assert "katib-tutorial-step" in html
    assert "katib-callout--tip" in html
    assert "katib-callout--warn" in html
    assert "katib-sections-grid--bordered" in html


def test_onboarding_pdf_within_target_pages(tmp_path):
    """target_pages [3, 6]; renders to 5 pages with placeholder content."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "ob.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 3 <= len(reader.pages) <= 6


def test_onboarding_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 onboarding should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "ob.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Cover
    assert "Welcome to the" in flat and "team" in flat
    assert "ONBOARDING" in flat.upper()
    # Reference code visible (cover-page minimalist-typographic renders reference_code
    # in the footer strip; no date auto-rendered in v2)
    assert "ONBOARDING-2026-0042" in flat
    # TOC
    assert "Contents" in flat or "CONTENTS" in flat.upper()
    assert "PART I" in flat.upper()
    assert "PART II" in flat.upper()
    assert "PART III" in flat.upper()
    assert "PART IV" in flat.upper()
    assert "CLOSING" in flat.upper()
    # Part I content
    assert "Welcome aboard" in flat
    assert "Who we are" in flat or "WHO WE ARE" in flat.upper()
    assert "async-first" in flat
    assert "Why this matters" in flat
    # Part II — 30/60/90
    assert "Your role" in flat
    assert "Responsibilities" in flat or "RESPONSIBILITIES" in flat.upper()
    assert "30 / 60 / 90" in flat
    assert "Days 1–30" in flat or "Days 1-30" in flat or "1–30" in flat
    assert "PR is merged" in flat
    assert "Stakeholders" in flat
    # Part III — tools
    assert "Tools and environment" in flat
    assert "Accounts to set up" in flat or "ACCOUNTS" in flat.upper()
    assert "2FA" in flat
    assert "INSTALL.md" in flat
    assert "Security basics" in flat
    # Part IV — first week
    assert "first week" in flat.lower() or "FIRST WEEK" in flat.upper()
    assert "Day 1" in flat
    assert "Day 5" in flat
    assert "onboarding buddy" in flat
    # Closing
    assert "Who to ask" in flat
    assert "Engineering lead" in flat
    assert "Product lead" in flat
    assert "Welcome. We're glad you're here" in flat


def test_onboarding_has_one_data_table_in_html():
    """Regression guard: 1 data-table element."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    tables = re.findall(r'<table class="katib-data-table', html)
    assert len(tables) == 1


def test_onboarding_has_three_tutorial_step_elements_in_html():
    """Regression guard: 3 tutorial-step elements (Steps 1, 2, 3)."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    steps = re.findall(
        r'<section class="katib-section katib-tutorial-step',
        html,
    )
    assert len(steps) == 3


def test_onboarding_has_two_sections_grid_bordered_elements_in_html():
    """Regression guard: 2 sections-grid bordered elements (stakeholders +
    who-to-ask)."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    grids = re.findall(
        r'<section class="katib-section katib-sections-grid katib-sections-grid--bordered"',
        html,
    )
    assert len(grids) == 2


def test_onboarding_data_table_has_three_columns_in_html():
    """Regression guard: 30/60/90 table has 3 <th> column headers."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    # Find the data-table's thead and count its th elements
    # The simplest check: at least 3 th tags total in the data-table section
    ths = re.findall(r'<th class="katib-data-table__th"', html)
    # Expect exactly 3 from the one table (one per column, no numeric alignment)
    assert len(ths) == 3


# ---------------------------------------------------------------- audit + registration


def test_onboarding_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_onboarding_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
