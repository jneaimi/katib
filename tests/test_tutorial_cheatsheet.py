"""tutorial-cheatsheet recipe — sixth Phase-3 recipe; first production consumer
of sections-grid (Day 11's new component).

3 sections, 1 new component (sections-grid). Production proofs:
- sections-grid dense variant — FIRST PRODUCTION CONSUMER (Day 11's
  new section component — Phase-3 component #5 built)
- 6 cards in a 2-col grid, each card with inline-styled dl / ul / div
  raw_body for keyboard shortcuts + commands + troubleshooting

Cheatsheet is a dense single-page reference card. No cover page; compact
module header; footer strip. Content adapted from v1-reference/domains/
tutorial/templates/cheatsheet.en.html.

Renders to 1 page; target_pages [1, 2], page_limit 2.

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
RECIPE_NAME = "tutorial-cheatsheet"


# ---------------------------------------------------------------- schema


def test_cheatsheet_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_cheatsheet_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_cheatsheet_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 2]
    assert r["page_limit"] == 2


def test_cheatsheet_has_no_cover_page():
    """Cheatsheet is a dense reference card — no cover."""
    r = load_recipe(RECIPE_NAME)
    components = [s["component"] for s in r["sections"]]
    assert "cover-page" not in components


def test_cheatsheet_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 3
    components = [s["component"] for s in sections]
    assert components == ["module", "sections-grid", "module"]


# ---------------------------------------------------------------- production proofs


def test_cheatsheet_first_sections_grid_consumer():
    """sections-grid Day-11 debut — first production consumer.
    Must use dense variant, columns=2, 6 cards."""
    r = load_recipe(RECIPE_NAME)
    grid = r["sections"][1]
    assert grid["component"] == "sections-grid"
    assert grid["variant"] == "dense"
    assert grid["inputs"]["columns"] == 2
    items = grid["inputs"]["items"]
    assert len(items) == 6
    titles = [i["title"] for i in items]
    assert titles == [
        "Quick actions",
        "Navigation",
        "Vault",
        "Terminal",
        "Common flags",
        "Troubleshooting",
    ]


def test_cheatsheet_module_header_uses_eyebrow_pattern():
    """Second recipe to use the no-cover module-with-eyebrow header (first
    was handoff Day 10)."""
    r = load_recipe(RECIPE_NAME)
    header = r["sections"][0]
    assert header["component"] == "module"
    assert header["inputs"]["eyebrow"] == "Cheatsheet"


# ---------------------------------------------------------------- validation + content-lint


def test_cheatsheet_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_cheatsheet_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_cheatsheet_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    assert "katib-sections-grid--dense" in html
    assert "katib-sections-grid__grid--cols-2" in html
    # No cover
    assert "katib-cover" not in html


def test_cheatsheet_pdf_within_target_pages(tmp_path):
    """target_pages [1, 2]; designed to fit one page but allow overflow."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "cheatsheet.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 1 <= len(reader.pages) <= 2


def test_cheatsheet_six_cards_rendered():
    """Regression guard — sections-grid's first production use must render
    exactly 6 card articles."""
    html, _ = compose(RECIPE_NAME, "en")
    card_markers = html.count('class="katib-sections-grid__card"')
    assert card_markers == 6


def test_cheatsheet_renders_all_v1_content(tmp_path):
    """Every card's content from v1 cheatsheet should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "cheatsheet.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Card titles
    for title in ("Quick actions", "Navigation", "Vault", "Terminal",
                  "Common flags", "Troubleshooting"):
        assert title in flat, f"card title missing: {title}"
    # Quick actions shortcuts
    assert "⌘K" in flat
    assert "Quick-create anywhere" in flat
    assert "Global search" in flat
    # Navigation
    assert "Go home" in flat
    assert "Go to vault" in flat
    # Vault
    assert "new note" in flat
    assert "new folder" in flat
    assert "full-text search" in flat
    # Terminal
    assert "new terminal tab" in flat
    assert "interrupt running process" in flat
    # Common flags
    assert "--dry-run" in flat
    assert "Preview action without writing" in flat
    assert "--verbose" in flat
    # Troubleshooting
    assert "Build fails" in flat
    assert "Server won't start" in flat
    assert "Missing deps" in flat
    assert "lsof -i :2400" in flat


# ---------------------------------------------------------------- audit + registration


def test_cheatsheet_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_cheatsheet_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
