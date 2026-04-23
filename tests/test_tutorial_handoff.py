"""tutorial-handoff recipe — fifth Phase-3 recipe, continues zero-new-component streak.

11 sections, 0 new components. Production proofs:
- kv-list boxed (second consumer after NOC — validates status-grid use case
  alongside NOC's field-summary use case)
- callout info tone — FIRST PRODUCTION CONSUMER (NOC/cover-letter used
  neutral; how-to used tip + warn)
- callout tip tone (second consumer after how-to)

No cover page — handoff is a working doc, not a presentation. First
Phase-3 recipe to validate the "headerless" no-cover composition.

2 density-style inline-styled module raw_body blocks (known-issues
severity cards, contacts 2x2 grid) + 1 structural raw_body with inline
code-block styling (runbook h3 + pre). Within NOC's 4-block ceiling.

Content adapted from v1-reference/domains/tutorial/templates/
handoff.en.html with placeholder-style prose preserved.

Renders 3 pages under v2 defaults; target_pages [2, 3], page_limit 3.

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
RECIPE_NAME = "tutorial-handoff"


# ---------------------------------------------------------------- schema


def test_handoff_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_handoff_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_handoff_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [2, 3]
    assert r["page_limit"] == 3


def test_handoff_has_no_cover_page():
    """Handoff is a working doc, not a presentation — no cover section."""
    r = load_recipe(RECIPE_NAME)
    components = [s["component"] for s in r["sections"]]
    assert "cover-page" not in components


def test_handoff_section_ordering():
    r = load_recipe(RECIPE_NAME)
    sections = r["sections"]
    assert len(sections) == 11
    components = [s["component"] for s in sections]
    assert components == [
        "module",       # 1. header
        "kv-list",      # 2. status meta
        "module",       # 3. summary
        "module",       # 4. what shipped
        "module",       # 5. architecture
        "callout",      # 6. key decision (info)
        "module",       # 7. runbook
        "module",       # 8. known issues
        "module",       # 9. contacts
        "module",       # 10. next steps
        "callout",      # 11. closing tip
    ]


# ---------------------------------------------------------------- production proofs


def test_handoff_uses_kv_list_boxed_status_grid():
    """kv-list boxed's second production consumer — status-grid shape
    (NOC used it for 7-field employee details; handoff uses it for 4-field
    status meta)."""
    r = load_recipe(RECIPE_NAME)
    meta = r["sections"][1]
    assert meta["component"] == "kv-list"
    assert meta["variant"] == "boxed"
    items = meta["inputs"]["items"]
    assert len(items) == 4
    terms = [i["term"] for i in items]
    assert terms == ["Status", "Reference", "Handoff date", "Owner going forward"]


def test_handoff_first_callout_info_consumer():
    """callout info tone — first production consumer (prior callout consumers
    were neutral, tip, warn)."""
    r = load_recipe(RECIPE_NAME)
    key_decision = r["sections"][5]
    assert key_decision["component"] == "callout"
    assert key_decision["inputs"]["tone"] == "info"
    assert key_decision["inputs"]["title"] == "Key decision"


def test_handoff_second_callout_tip_consumer():
    """callout tip — second production consumer after how-to (Day 9)."""
    r = load_recipe(RECIPE_NAME)
    closing = r["sections"][-1]
    assert closing["component"] == "callout"
    assert closing["inputs"]["tone"] == "tip"


def test_handoff_module_header_uses_eyebrow_pattern():
    """No cover page; header is a module with eyebrow + title + intro —
    testing module 0.3.0's optional-title feature is *not* used here
    (title present) but eyebrow-first header pattern is validated."""
    r = load_recipe(RECIPE_NAME)
    header = r["sections"][0]
    assert header["component"] == "module"
    assert header["inputs"]["eyebrow"] == "Handoff"
    assert "title" in header["inputs"]
    assert "intro" in header["inputs"]


# ---------------------------------------------------------------- validation + content-lint


def test_handoff_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_handoff_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_handoff_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    # Component marker classes for production consumers
    assert "katib-kv-list--boxed" in html
    assert "katib-callout--info" in html
    assert "katib-callout--tip" in html
    # No cover class rendered
    assert "katib-cover" not in html


def test_handoff_pdf_within_target_pages(tmp_path):
    """target_pages [2, 3]; no cover + ~10 body sections → 2-3 pages."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "handoff.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 2 <= len(reader.pages) <= 3


def test_handoff_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 handoff template should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "handoff.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Header
    assert "Handoff".upper() in flat.upper()
    # Status meta
    for label in ("Status", "Reference", "Handoff date", "Owner going forward"):
        assert label.upper() in flat.upper(), f"status label missing: {label}"
    assert "HT-0001" in flat
    assert "2026-04-23" in flat
    # Summary
    assert "hands over ownership" in flat
    # What shipped
    assert "Core feature released" in flat
    assert "Monitoring dashboards" in flat
    # Architecture
    assert "entry-point service" in flat
    assert "eventually-consistent" in flat
    # Key decision
    assert "Key decision" in flat
    assert "eventual consistency" in flat
    # Runbook
    assert "Runbook" in flat
    assert "Deploy" in flat
    assert "Rollback" in flat
    assert "Health checks" in flat
    assert "git push origin main" in flat
    assert "/healthz" in flat
    # Known issues
    assert "Known issues" in flat
    assert "duplicate in rare race conditions" in flat
    assert "50k records" in flat
    assert "export CSV" in flat
    # Contacts
    assert "Handing off" in flat.replace("HANDING OFF", "Handing off")  # case-insensitive
    assert "Taking over" in flat.replace("TAKING OVER", "Taking over")
    assert "Escalation" in flat.replace("ESCALATION", "Escalation")
    assert "Rotating engineer" in flat
    # Next steps
    assert "Next steps" in flat
    assert "30-day check-in" in flat
    # Closing callout
    assert "One last note" in flat
    assert "best handoff" in flat


def test_handoff_known_issues_inline_block_present():
    """Known-issues density block: 3 severity cards as inline-styled divs
    inside a module raw_body."""
    html, _ = compose(RECIPE_NAME, "en")
    assert "Medium" in html
    # 3 severity cards — 2 "Low" + 1 "Medium"
    assert html.count(">Low<") == 2
    assert html.count(">Medium<") == 1
    # Uses callout-warn-bg for Medium, callout-info-bg for Low
    assert "callout-warn-bg" in html
    assert "callout-info-bg" in html


def test_handoff_contacts_inline_block_present():
    """Contacts 2x2 grid — 4 inline-styled cards inside a module raw_body."""
    html, _ = compose(RECIPE_NAME, "en")
    for label in ("Handing off", "Taking over", "Escalation", "On-call"):
        assert label in html, f"contact card label missing: {label}"


# ---------------------------------------------------------------- audit + registration


def test_handoff_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_handoff_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
