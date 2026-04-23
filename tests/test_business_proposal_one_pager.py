"""business-proposal-one-pager recipe — seventh Phase-3 recipe; resumes the
zero-new-component streak (broken intentionally on Day 11 for sections-grid).

5 sections, 0 new components. Production proofs:
- sections-grid default variant — SECOND PRODUCTION CONSUMER after Day-11
  cheatsheet (dense). Validates the component handles both dense 6-card
  and default 2x2 shapes.

No cover page. Designed to fit on a single A4 (target_pages [1, 1],
page_limit 1). 4 density-convention inline blocks (eyebrow-row, hero,
metrics, footer) — at NOC's ceiling. metrics-grid deliberately NOT
graduated: only 1 verified dependent (one-pager itself); deferred until
a second recipe needs the 4-col big-number shape.

Content adapted from v1-reference/domains/business-proposal/templates/
one-pager.en.html. Placeholder-style prose preserved.

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
RECIPE_NAME = "business-proposal-one-pager"


# ---------------------------------------------------------------- schema


def test_one_pager_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_one_pager_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_one_pager_single_page_target():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 1]
    assert r["page_limit"] == 1


def test_one_pager_has_no_cover_page():
    """One-pager is by definition a single page — no cover."""
    r = load_recipe(RECIPE_NAME)
    components = [s["component"] for s in r["sections"]]
    assert "cover-page" not in components


def test_one_pager_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 5
    components = [s["component"] for s in sections]
    assert components == [
        "module",          # 1. eyebrow row
        "module",          # 2. hero
        "module",          # 3. metrics block (inline, deferred graduation)
        "sections-grid",   # 4. 2x2 body
        "module",          # 5. footer
    ]


# ---------------------------------------------------------------- production proofs


def test_one_pager_second_sections_grid_consumer():
    """sections-grid's second production consumer (cheatsheet was first).
    Validates default variant + columns=2 + 4 cards."""
    r = load_recipe(RECIPE_NAME)
    grid = r["sections"][3]
    assert grid["component"] == "sections-grid"
    # Default variant — not dense, not bordered
    assert grid.get("variant") in (None, "default")
    assert grid["inputs"]["columns"] == 2
    items = grid["inputs"]["items"]
    assert len(items) == 4
    titles = [i["title"] for i in items]
    assert titles == ["Program scope", "Delivery model", "Outcomes", "Next step"]


def test_one_pager_metrics_block_inline_styled():
    """Metrics block uses inline-styled module raw_body because metrics-grid
    has only 1 verified dependent (below graduation threshold). Regression
    guard for the deferred-graduation decision."""
    r = load_recipe(RECIPE_NAME)
    metrics = r["sections"][2]
    assert metrics["component"] == "module"
    raw = metrics["inputs"]["raw_body"]
    # 4 metrics with accent number + small label
    assert "Participants" in raw
    assert "Duration" in raw
    assert "Training days" in raw
    assert "Investment" in raw
    # 4-col inline grid
    assert "grid-template-columns: repeat(4, 1fr)" in raw


# ---------------------------------------------------------------- validation + content-lint


def test_one_pager_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_one_pager_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_one_pager_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    # sections-grid default variant present on the rendered section element
    assert 'katib-sections-grid katib-sections-grid--default' in html
    # No cover
    assert "katib-cover" not in html


def test_one_pager_pdf_fits_one_page(tmp_path):
    """target_pages [1, 1] — must be exactly one page."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "one-pager.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert len(reader.pages) == 1


def test_one_pager_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 one-pager should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "one-pager.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Eyebrow row
    assert "jasem | katib" in flat or "JASEM | KATIB" in flat.upper()
    assert "PROP/2026/001" in flat
    assert "2026-04-24" in flat
    # Hero
    assert "Proposal title" in flat
    assert "Subtitle" in flat
    # Metrics
    for metric_label in ("Participants", "Duration", "Training days", "Investment"):
        assert metric_label in flat, f"metric label missing: {metric_label}"
    assert "18" in flat
    assert "6 wk" in flat
    assert "24" in flat
    assert "AED 615K" in flat
    # Body sections
    for section in ("Program scope", "Delivery model", "Outcomes", "Next step"):
        assert section in flat, f"body section missing: {section}"
    assert "Full-stack AI engineering" in flat
    assert "Hybrid split" in flat
    assert "working agent + deploy pipeline" in flat
    assert "Countersign" in flat
    # CTA
    assert "Accept proposal" in flat


def test_one_pager_four_metric_blocks_rendered():
    """Regression guard — inline metrics block must render 4 big-number + label
    pairs."""
    html, _ = compose(RECIPE_NAME, "en")
    # Count accent-color 20pt number divs (inline-styled) — 4 expected
    metric_number_markers = html.count('font-size: 20pt; font-weight: 500; color: var(--accent)')
    assert metric_number_markers == 4


def test_one_pager_sections_grid_four_cards():
    """Regression guard — sections-grid must render 4 cards."""
    html, _ = compose(RECIPE_NAME, "en")
    card_markers = html.count('class="katib-sections-grid__card"')
    assert card_markers == 4


def test_one_pager_cta_rendered_in_last_card():
    """The 'Accept proposal' CTA is inline-styled inside the Next step card."""
    html, _ = compose(RECIPE_NAME, "en")
    assert "Accept proposal" in html
    # CTA uses accent bg + accent-on text
    assert "background: var(--accent); color: var(--accent-on)" in html


# ---------------------------------------------------------------- audit + registration


def test_one_pager_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_one_pager_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
