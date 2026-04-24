"""tutorial-katib-walkthrough recipe — FIFTEENTH AND FINAL Phase-3 recipe.

**CLOSES THE PHASE-3 MIGRATE LIST AT 15/15.**

Largest recipe by section count in Phase-3 (48 sections; beats mou's 25).
Zero new components — composes 9 existing components with 5 inline density
pattern groups (SVG diagrams × 3, code blocks × 5, palette swatches × 1
section, objectives-box × 5, checklist × 1).

Production proofs:
- data-table default — 8TH production consumer (streak continues:
  white-paper Day 13, proposal 3× Day 14, invoice Day 15, quote Day 16,
  onboarding Day 20, walkthrough Day 21 = 8 recipes)
- tutorial-step — 3RD production consumer (how-to Day 9, onboarding
  Day 20, walkthrough Day 21)
- kv-list default — HEAVIEST SINGLE-RECIPE DEPLOYMENT (8 uses across
  Modules 4/5/6/7)
- pull-quote — 3RD production consumer (Phase-2 tutorial showcase,
  white-paper Day 13, walkthrough Day 21)
- cover-page minimalist-typographic — 5TH production use
- sections-grid dense cols=2 — 6TH production consumer (20-card cheat
  grid — largest items count ever)
- callout info — 3 uses in this recipe (heaviest single-recipe info
  deployment)
- callout tip — 3rd production consumer (how-to + onboarding + walkthrough)
- objectives-box — 4+ uses (module 1, 3, 5, 6 + preface = 5 total)

Content adapted from v1-reference/domains/tutorial/templates/
katib-walkthrough.en.html. Placeholder prose preserved — content is v1-
specific and references v1 CLI architecture. Phase-4 task: rewrite
content to reflect v2 architecture.

Renders to 14 pages; target_pages [8, 16], page_limit 16.

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
RECIPE_NAME = "tutorial-katib-walkthrough"


# ---------------------------------------------------------------- schema


def test_walkthrough_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_walkthrough_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_walkthrough_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [8, 16]
    assert r["page_limit"] == 16


def test_walkthrough_has_large_section_count():
    """Largest recipe in Phase-3 by section count (48 sections,
    beats mou's 25)."""
    r = load_recipe(RECIPE_NAME)
    # Single large recipe; exact count may shift minor — assert >=40 as regression guard
    assert len(r["sections"]) >= 40


def test_walkthrough_component_mix():
    r = load_recipe(RECIPE_NAME)
    from collections import Counter
    counts = Counter(s["component"] for s in r["sections"])
    assert counts["cover-page"] == 1
    assert counts["data-table"] == 1
    assert counts["tutorial-step"] == 3
    assert counts["kv-list"] >= 8
    assert counts["pull-quote"] == 2
    assert counts["sections-grid"] == 1
    assert counts["objectives-box"] >= 4
    assert counts["callout"] >= 3  # 1 tip + 3 info


# ---------------------------------------------------------------- production proofs


def test_walkthrough_is_eighth_data_table_consumer():
    """data-table 8th production consumer — streak: white-paper, proposal ×3,
    invoice, quote, onboarding, walkthrough."""
    r = load_recipe(RECIPE_NAME)
    tables = [s for s in r["sections"] if s["component"] == "data-table"]
    assert len(tables) == 1
    table = tables[0]
    # Domains quick-pick: 3 cols, 10 rows
    assert len(table["inputs"]["columns"]) == 3
    assert len(table["inputs"]["rows"]) == 10


def test_walkthrough_third_tutorial_step_consumer():
    """tutorial-step 3rd production consumer (how-to Day 9, onboarding
    Day 20, walkthrough Day 21). Module 1 install steps."""
    r = load_recipe(RECIPE_NAME)
    steps = [s for s in r["sections"] if s["component"] == "tutorial-step"]
    assert len(steps) == 3
    numbers = [s["inputs"]["number"] for s in steps]
    assert numbers == [1, 2, 3]


def test_walkthrough_heaviest_kv_list_deployment():
    """8+ kv-list uses — heaviest single-recipe deployment ever.
    Prior max: mou 0; quote 0 (kv-list not used in legal/financial).
    Walkthrough uses kv-list for cover styles, proposal types, project
    routing, mode matrix, admin scripts, exit codes, env vars, file
    layout."""
    r = load_recipe(RECIPE_NAME)
    kv_lists = [s for s in r["sections"] if s["component"] == "kv-list"]
    assert len(kv_lists) >= 8


def test_walkthrough_third_pull_quote_consumer():
    """pull-quote 3rd production consumer (Phase-2 tutorial + white-paper
    Day 13 + walkthrough Day 21). 2 uses in this recipe: reflect-is-
    read-only + CI-strict-mode markers."""
    r = load_recipe(RECIPE_NAME)
    quotes = [s for s in r["sections"] if s["component"] == "pull-quote"]
    assert len(quotes) == 2


def test_walkthrough_cover_uses_minimalist_typographic():
    """5th production use of cover-page minimalist-typographic variant."""
    r = load_recipe(RECIPE_NAME)
    cover = r["sections"][0]
    assert cover["component"] == "cover-page"
    assert cover["variant"] == "minimalist-typographic"
    assert cover["inputs"]["eyebrow"] == "The Complete Walkthrough"


def test_walkthrough_sections_grid_dense_cheat_cards():
    """sections-grid dense cols=2 with 20 cheat-cards — LARGEST items
    count in any sections-grid use."""
    r = load_recipe(RECIPE_NAME)
    grids = [s for s in r["sections"]
             if s["component"] == "sections-grid" and s.get("variant") == "dense"]
    assert len(grids) == 1
    grid = grids[0]
    assert grid["inputs"]["columns"] == 2
    assert len(grid["inputs"]["items"]) == 20


def test_walkthrough_uses_seven_module_headers():
    """7 modules (Module 1 through Module 7/Appendix) via module plain
    with eyebrow pattern. Same codified pattern as onboarding Day 20."""
    r = load_recipe(RECIPE_NAME)
    module_headers = [
        s for s in r["sections"]
        if s["component"] == "module"
        and "eyebrow" in s.get("inputs", {})
        and "Module" in s["inputs"].get("eyebrow", "")
    ]
    assert len(module_headers) == 7


def test_walkthrough_uses_objectives_box():
    """objectives-box used for 'What you'll learn' + 4 module-objectives
    blocks (Modules 1, 3, 5, 6)."""
    r = load_recipe(RECIPE_NAME)
    obj_boxes = [s for s in r["sections"] if s["component"] == "objectives-box"]
    assert len(obj_boxes) >= 4


# ---------------------------------------------------------------- validation + content-lint


def test_walkthrough_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_walkthrough_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_walkthrough_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    assert "katib-data-table" in html
    assert "katib-tutorial-step" in html
    assert "katib-kv-list" in html
    assert "katib-pullquote" in html  # note: no hyphen between pull and quote
    assert "katib-sections-grid--dense" in html
    assert "katib-callout--info" in html
    assert "katib-callout--tip" in html


def test_walkthrough_pdf_within_target_pages(tmp_path):
    """target_pages [8, 16]; renders to 14 pages."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "wk.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 8 <= len(reader.pages) <= 16


def test_walkthrough_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 walkthrough should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "wk.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Cover
    assert "Katib" in flat
    assert "TUT-KATIB-001" in flat
    # Preface objectives
    assert "What you'll learn" in flat.lower() or "WHAT YOU'LL LEARN" in flat.upper()
    assert "five minutes" in flat
    # Module 1 — Install
    assert "Install" in flat and "first render" in flat
    assert "install.sh" in flat
    assert "npm" in flat
    # Module 2 — Domains
    assert "domains" in flat.lower()
    assert "business-proposal" in flat
    assert "How routing works" in flat
    # Module 3 — Brand profiles
    assert "Brand profiles" in flat or "brand" in flat.lower()
    assert "Jasem" in flat
    assert "Newsreader" in flat
    # Module 4 — Composition
    assert "minimalist-typographic" in flat
    assert "neural-cartography" in flat
    assert "shot.py" in flat
    # Module 5 — Reflect
    assert "reflect.py" in flat
    assert "string-swap" in flat
    assert "new-domain-candidate" in flat
    assert "read-only" in flat
    # Module 6 — Vault integration
    assert "Governed by design" in flat
    assert "--project" in flat
    assert "audit_vault.py" in flat
    assert "migrate_vault.py" in flat
    # Module 7 — Appendix
    assert "Render a doc" in flat or "RENDER A DOC" in flat.upper()
    assert "KATIB_VAULT_MODE" in flat
    assert "GEMINI_API_KEY" in flat
    # Closing
    assert "Summary" in flat or "SUMMARY" in flat.upper()
    assert "full loop" in flat


def test_walkthrough_has_three_inline_svg_diagrams():
    """Regression guard: 3 inline SVG diagrams (domain taxonomy +
    screenshot pipeline + reflect data-flow)."""
    html, _ = compose(RECIPE_NAME, "en")
    # Count <svg> element opens (ignore XML namespace matches)
    svg_count = html.count("<svg viewBox")
    assert svg_count == 3


def test_walkthrough_has_multiple_code_blocks():
    """Regression guard: 5+ inline <pre> code blocks (install, config YAML,
    hello-world CLI, brand YAML, brand CLI, reflect session)."""
    html, _ = compose(RECIPE_NAME, "en")
    import re
    pre_count = len(re.findall(r"<pre\s", html))
    assert pre_count >= 5


def test_walkthrough_has_cheat_grid_with_twenty_cards():
    """Regression guard: sections-grid dense with 20 cheat-cards."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    # Cards have class katib-sections-grid__card
    cards = re.findall(r'class="katib-sections-grid__card"', html)
    assert len(cards) == 20


def test_walkthrough_has_palette_swatches():
    """Regression guard: 5 palette swatches in Module 3 Jasem brand section."""
    html, _ = compose(RECIPE_NAME, "en")
    # Palette hexes
    for hex_color in ("#F59E0B", "#FB923C", "#18181B", "#FAFAFA", "#FEF3C7"):
        assert hex_color in html, f"palette hex missing: {hex_color}"


# ---------------------------------------------------------------- audit + registration


def test_walkthrough_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_walkthrough_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1


# ---------------------------------------------------------------- Phase-3 close verification


def test_phase_3_close_marker_all_fifteen_recipes_in_capabilities():
    """Phase-3 CLOSE gate — all 15 migrated recipes present in
    capabilities.yaml."""
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    phase_3_recipes = {
        "business-proposal-letter",      # Day 4
        "personal-cover-letter",         # Day 6
        "formal-noc",                    # Day 8
        "tutorial-how-to",               # Day 9
        "tutorial-handoff",              # Day 10
        "tutorial-cheatsheet",           # Day 11
        "business-proposal-one-pager",   # Day 12
        "editorial-white-paper",         # Day 13
        "business-proposal-proposal",    # Day 14
        "financial-invoice",             # Day 15
        "financial-quote",               # Day 16
        "legal-mou",                     # Day 17
        "personal-cv",                   # Day 19
        "tutorial-onboarding",           # Day 20
        "tutorial-katib-walkthrough",    # Day 21 (this one)
    }
    missing = phase_3_recipes - set(recipes.keys())
    assert not missing, f"Phase-3 recipes missing from capabilities.yaml: {missing}"
