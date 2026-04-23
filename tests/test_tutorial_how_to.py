"""tutorial-how-to recipe — fourth Phase-3 recipe, continues zero-new-component streak.

9 logical sections / 12 recipe entries, 0 new components. Production proofs:
- cover-page minimalist-typographic (second consumer after tutorial.yaml;
  first Phase-3 recipe to use the covers tier)
- objectives-box boxed (second consumer after tutorial.yaml)
- tutorial-step × 4 — FIRST PRODUCTION CONSUMER (was showcase-only)
- callout tone=tip — FIRST PRODUCTION CONSUMER (cover-letter + noc used neutral)
- callout tone=warn — FIRST PRODUCTION CONSUMER
- whats-next bullet (second consumer after tutorial.yaml)
- 2 inline-styled module raw_body blocks: lead paragraph, Do/Don't 2-col
  compare (single-recipe use; density convention — validates we wait for
  a second consumer before graduating compare-box).

Content adapted from v1-reference/domains/tutorial/templates/how-to.en.html
(placeholder template, same procedural structure).

Renders to 3 pages (cover + body); target_pages [2, 3] permits.

AR variant deferred — NOC remains designated first bilingual recipe that
triggers inputs_by_lang schema design.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pypdf import PdfReader

from core import recipe_ops as ops
from core.compose import compose, load_recipe
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPE_NAME = "tutorial-how-to"


# ---------------------------------------------------------------- schema


def test_how_to_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_how_to_en_only():
    """AR variant deferred until inputs_by_lang schema lands."""
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_how_to_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [2, 3]
    assert r["page_limit"] == 3


def test_how_to_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 12
    components = [s["component"] for s in sections]
    assert components == [
        "cover-page",           # 1. minimalist-typographic cover
        "module",               # 2. lead paragraph
        "objectives-box",       # 3. before you start
        "tutorial-step",        # 4. step 1
        "tutorial-step",        # 5. step 2
        "tutorial-step",        # 6. step 3
        "tutorial-step",        # 7. step 4
        "callout",              # 8. tip
        "callout",              # 9. warn
        "module",               # 10. Do/Don't compare
        "module",               # 11. troubleshooting
        "whats-next",           # 12. forward CTA
    ]


# ---------------------------------------------------------------- production proofs


def test_how_to_uses_cover_page_minimalist():
    """First Phase-3 recipe to use the covers tier."""
    r = load_recipe(RECIPE_NAME)
    cover = r["sections"][0]
    assert cover["component"] == "cover-page"
    assert cover["variant"] == "minimalist-typographic"


def test_how_to_uses_objectives_box_boxed():
    """Second production consumer of objectives-box (tutorial.yaml was first)."""
    r = load_recipe(RECIPE_NAME)
    prereqs = r["sections"][2]
    assert prereqs["component"] == "objectives-box"
    assert prereqs["variant"] == "boxed"
    assert len(prereqs["inputs"]["items"]) == 3


def test_how_to_first_tutorial_step_production_consumer():
    """tutorial-step was showcase-only before this recipe — Day 9 promotes it
    to production. Four steps, 1-4 numbered."""
    r = load_recipe(RECIPE_NAME)
    steps = [s for s in r["sections"] if s["component"] == "tutorial-step"]
    assert len(steps) == 4
    numbers = [s["inputs"]["number"] for s in steps]
    assert numbers == [1, 2, 3, 4]
    # Each step has a title + body
    for s in steps:
        assert s["inputs"]["title"]
        assert s["inputs"]["body"]


def test_how_to_first_callout_tip_and_warn_consumers():
    """First production consumers of callout tip + warn tones
    (prior consumers — cover-letter + noc — used neutral)."""
    r = load_recipe(RECIPE_NAME)
    callouts = [s for s in r["sections"] if s["component"] == "callout"]
    assert len(callouts) == 2
    tones = [c["inputs"]["tone"] for c in callouts]
    assert tones == ["tip", "warn"]


def test_how_to_uses_whats_next_bullet():
    """Second consumer of whats-next (tutorial.yaml was first)."""
    r = load_recipe(RECIPE_NAME)
    nxt = r["sections"][-1]
    assert nxt["component"] == "whats-next"
    assert nxt["variant"] == "bullet"
    assert len(nxt["inputs"]["items"]) == 3


# ---------------------------------------------------------------- validation + content-lint


def test_how_to_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_how_to_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_how_to_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    # Component marker classes for production consumers
    assert "katib-cover--minimalist-typographic" in html
    assert "katib-objectives--boxed" in html
    assert "katib-tutorial-step" in html
    assert "katib-callout--tip" in html
    assert "katib-callout--warn" in html
    assert "katib-whats-next--bullet" in html


def test_how_to_pdf_within_target_pages(tmp_path):
    """target_pages [2, 3]; cover takes 1 full page, body fits in 1-2."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "how-to.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 2 <= len(reader.pages) <= 3


def test_how_to_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 how-to template should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "how-to.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Cover
    assert "HOW-TO" in flat
    assert "How-to Guide".upper() in flat.upper() or "How-to" in flat
    # Lead
    assert "step by step" in flat
    # Prerequisites (objectives-box label is uppercased by CSS)
    assert "Before you start".upper() in flat.upper()
    assert "access to the system" in flat
    assert "5 minutes" in flat
    # Steps — titles
    for title in ("Open the target screen", "Locate the entry point",
                  "Fill in the details", "Confirm and verify"):
        assert title in flat, f"step title missing: {title}"
    # Step 1 body phrase
    assert "Navigate to the page" in flat
    # Tip callout
    assert "quick-create dialog" in flat
    # Warn callout
    assert "red banner" in flat
    # Do/Don't
    assert "client-onboarding-v2" in flat
    assert "collide in search results" in flat
    # Troubleshooting
    assert "If it doesn't work" in flat
    assert "Page doesn't load" in flat
    assert "Button greyed out" in flat
    assert "Changes don't persist" in flat
    # What's next
    assert "What's next" in flat
    assert "Bookmark" in flat


def test_how_to_four_tutorial_steps_rendered(tmp_path):
    """Regression guard — tutorial-step's first production use must render
    exactly 4 step circles."""
    html, _ = compose(RECIPE_NAME, "en")
    # tutorial-step renders a numbered step-circle marker per step
    # Count the rendered <div> element (not the CSS rule)
    step_markers = html.count('<div class="katib-tutorial-step__circle">')
    assert step_markers == 4


def test_how_to_do_dont_inline_block_present():
    """The Do/Don't 2-col compare is an inline-styled module (single-use, per
    density convention). Verify both halves render."""
    html, _ = compose(RECIPE_NAME, "en")
    assert ">Do<" in html
    assert ">Don&#39;t<" in html or ">Don't<" in html
    # The inline flex layout uses callout-tip + callout-danger token colours
    assert "callout-tip-bg" in html
    assert "callout-danger-bg" in html


# ---------------------------------------------------------------- audit + registration


def test_how_to_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_how_to_audit_entry_exists():
    """build.py would refuse a recipe without an audit entry."""
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
