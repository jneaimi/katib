"""personal-cover-letter recipe — second Phase-3 recipe migration.

8 sections, 0 new components. Exercises Day-3 + Day-5 component work in
production:
- masthead-personal (Day 5) — personal identity header
- callout neutral (Day 5) — subject line
- signature-block recipient variant (Day 3) — addressee
- module no-title (Day 3) — continuous prose + date-line + enclosure-line
- rule (Phase 2) — enclosure separator
- signature-block default (Phase 2) — closing signature

Content ported verbatim from v1-reference/domains/personal/templates/
cover-letter.en.html — preserves v1's placeholder-prose template style
(instructional text in square brackets for the author to replace).

AR variant deferred pending `inputs_by_lang` schema design (same as
business-proposal-letter).
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pypdf import PdfReader

from core import recipe_ops as ops
from core.compose import compose, load_recipe
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPE_NAME = "personal-cover-letter"


# ---------------------------------------------------------------- schema


def test_cover_letter_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_cover_letter_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_cover_letter_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [1, 2]
    assert r["page_limit"] == 3


def test_cover_letter_eight_sections_in_order():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 8
    components = [s["component"] for s in sections]
    assert components == [
        "masthead-personal",    # 1. header
        "module",               # 2. date line
        "signature-block",      # 3. recipient
        "callout",              # 4. subject line
        "module",               # 5. body
        "signature-block",      # 6. closing signature
        "rule",                 # 7. enclosure separator
        "module",               # 8. enclosure line
    ]


# ---------------------------------------------------------------- Day-5 + Day-3 production proofs


def test_cover_letter_uses_masthead_personal():
    """Day-5 component in production — this is the first recipe consuming
    masthead-personal. Proves the Phase-3 component queue 6→7 revision
    was justified."""
    r = load_recipe(RECIPE_NAME)
    assert r["sections"][0]["component"] == "masthead-personal"


def test_cover_letter_uses_callout_neutral_tone():
    """Day-5 callout v0.2.0 neutral tone in production — proves the
    non-status highlight box works for subject lines."""
    r = load_recipe(RECIPE_NAME)
    subject = r["sections"][3]
    assert subject["component"] == "callout"
    assert subject["inputs"]["tone"] == "neutral"


def test_cover_letter_uses_recipient_variant():
    """Day-3 signature-block extension in production."""
    r = load_recipe(RECIPE_NAME)
    recipient = r["sections"][2]
    assert recipient["component"] == "signature-block"
    assert recipient["variant"] == "recipient"


def test_cover_letter_uses_rule_hairline():
    """rule primitive + hairline variant — enclosure separator."""
    r = load_recipe(RECIPE_NAME)
    enclosure_rule = r["sections"][6]
    assert enclosure_rule["component"] == "rule"
    assert enclosure_rule["variant"] == "hairline"


def test_cover_letter_body_module_has_no_title():
    """Body module (section 5) uses module v0.3.0 heading-less mode."""
    r = load_recipe(RECIPE_NAME)
    body = r["sections"][4]
    assert body["component"] == "module"
    assert "title" not in body["inputs"]
    assert "raw_body" in body["inputs"]


# ---------------------------------------------------------------- validation + content-lint


def test_cover_letter_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_cover_letter_validates_strict_clean():
    """Content-lint predicted clean: placeholder prose uses instructional
    style, not marketing slop. Strict mode must pass."""
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_cover_letter_renders_en(tmp_path):
    html, _ = compose(RECIPE_NAME, "en")
    # All Day-3 + Day-5 components emit their marker classes
    assert "katib-masthead-personal" in html
    assert "katib-callout--neutral" in html
    assert "katib-signature--recipient" in html
    assert "katib-signature--line-over" in html
    assert "katib-rule--hairline" in html


def test_cover_letter_pdf_within_target_pages(tmp_path):
    """Target [1, 2]; v1 cover-letter was 1-page. Must not overflow to 3+."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "cover.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 1 <= len(reader.pages) <= 2


def test_cover_letter_renders_all_v1_placeholder_content(tmp_path):
    """Every placeholder and fixed phrase from the v1 template should appear
    in the rendered PDF. Whitespace is collapsed to tolerate PDF line-wrapping."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "cover.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Masthead
    assert "Jasem Al Neaimi" in flat
    assert "jasem@example.com" in flat
    assert "Dubai, UAE" in flat
    # Date
    assert "23 April 2026" in flat
    # Recipient placeholders (v1 style)
    assert "[Hiring Manager Name]" in flat
    assert "[Company Name]" in flat
    # Subject line
    assert "Application for [Role Title]" in flat
    # Salutation + placeholder body phrases
    assert "Dear [Mr. / Ms.] [Last Name]," in flat
    assert "[Opening paragraph — the why." in flat
    assert "[Middle paragraph — the what." in flat
    assert "[Closing paragraph — the next step." in flat
    # Closing + signature
    assert "Sincerely," in flat
    assert "[Title / current role]" in flat
    # Enclosure
    assert "Enclosed:" in flat
    assert "Curriculum Vitae" in flat


# ---------------------------------------------------------------- audit + registration


def test_cover_letter_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_cover_letter_audit_entry_exists():
    """build.py would refuse a recipe without an audit entry — verify register wrote one."""
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
