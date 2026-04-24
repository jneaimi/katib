"""business-proposal-letter recipe — first Phase-3 recipe migration.

Proves the recipe-migration flow end-to-end: v1 template → v2 recipe
using only existing (or Phase-3-extended) components. Four sections:
letterhead (Day 2) + signature-block recipient variant (Day 3) + module
heading-less (Day 3) + signature-block default.

Content ported verbatim from v1-reference/domains/business-proposal/
templates/letter.en.html.

AR variant is deferred to NOC-day when `inputs_by_lang` schema is
introduced (content differs culturally between EN and AR, not a
machine translation).
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pypdf import PdfReader

from core import recipe_ops as ops
from core.compose import compose, load_recipe
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPE_NAME = "business-proposal-letter"


# ---------------------------------------------------------------- schema


def test_letter_recipe_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_letter_recipe_en_only():
    """AR deferred pending inputs_by_lang schema design."""
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]
    assert "ar" not in r["languages"]


def test_letter_recipe_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 2]
    assert r["page_limit"] == 3


def test_letter_recipe_four_sections_in_order():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 4
    components = [s["component"] for s in sections]
    assert components == [
        "letterhead",
        "signature-block",
        "module",
        "signature-block",
    ]


def test_letter_recipe_has_recipient_variant():
    """Second section (addressee) uses the new recipient variant."""
    r = load_recipe(RECIPE_NAME)
    assert r["sections"][1]["variant"] == "recipient"


def test_letter_recipe_body_module_has_no_title():
    """Third section proves module v0.3.0 in production use — continuous prose
    with raw_body only, no title/eyebrow/intro."""
    r = load_recipe(RECIPE_NAME)
    body_inputs = r["sections"][2]["inputs"]
    assert "title" not in body_inputs
    assert "eyebrow" not in body_inputs
    assert "intro" not in body_inputs
    assert "raw_body" in body_inputs


def test_letter_recipe_closing_signature_default_variant():
    """Last section is the closing signature — default line-over (no explicit variant)."""
    r = load_recipe(RECIPE_NAME)
    assert "variant" not in r["sections"][3]


# ---------------------------------------------------------------- keywords + metadata


def test_letter_recipe_keywords():
    r = load_recipe(RECIPE_NAME)
    expected = {"letter", "business", "proposal", "formal", "correspondence", "cover"}
    assert expected.issubset(set(r["keywords"]))


# ---------------------------------------------------------------- validation + content-lint


def test_letter_recipe_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_letter_recipe_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_letter_recipe_renders_en(tmp_path):
    html, _ = compose(RECIPE_NAME, "en")
    # All four sections emit their marker classes
    assert "katib-letterhead" in html
    assert "katib-signature--recipient" in html
    assert "katib-module" in html
    # Default closing signature is line-over
    assert "katib-signature--line-over" in html


def test_letter_recipe_pdf_one_page(tmp_path):
    """Letter should fit on 1 page per v1 behavior. Target range [1, 2] — upper
    bound is a safety guardrail, not the expected output."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "letter.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 5000
    reader = PdfReader(str(pdf))
    assert 1 <= len(reader.pages) <= 2


def test_letter_recipe_renders_all_v1_content(tmp_path):
    """Every identifiable piece of v1 prose should appear in the rendered PDF text.
    PDF text extraction can split phrases across line breaks, so we collapse
    whitespace before asserting."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "letter.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    # Collapse whitespace (spaces + newlines) to make phrase assertions line-wrap tolerant
    flat = re.sub(r"\s+", " ", raw).strip()

    # Letterhead
    assert "Acme | Katib" in flat
    assert "KATIB-2026-001" in flat
    assert "23 April 2026" in flat
    # Recipient
    assert "Ms. Sara Al-Hashimi" in flat
    assert "VP of Learning & Development" in flat
    assert "ACME Corp" in flat
    assert "Dubai" in flat
    # Body prose — key phrases from each paragraph
    assert "Dear Ms. Al-Hashimi," in flat
    assert "Applied AI Training Program" in flat
    assert "Hybrid Split delivery model" in flat
    assert "6-week program split into two groups" in flat
    assert "30-minute alignment call" in flat
    assert "Kind regards," in flat
    # Closing signature
    assert "Alex Acme" in flat
    assert "Managing Director" in flat


# ---------------------------------------------------------------- audit + registration


def test_letter_recipe_in_capabilities():
    """Regression: recipe must appear in capabilities.yaml after register."""
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_letter_recipe_audit_entry_exists():
    """build.py will refuse a recipe without an audit entry — verify register wrote one."""
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
