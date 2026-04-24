"""legal-mou recipe — twelfth Phase-3 recipe; FIRST production consumer of
clause-list primitive. Closes the original Day-0 component queue.

25 sections, 1 new component (clause-list). Production proofs:
- clause-list — FIRST PRODUCTION CONSUMER (Day-17 debut with 7 internal uses)
- module numbered — HEAVIEST DEPLOYMENT EVER: 10 uses in one recipe (§1-§10).
  Prior record: 6 consecutive in white-paper Day 13, 5 in proposal Day 14.
- callout info — 3rd + 4th consumer (Party A + Party B)
- callout neutral — 5th + 6th consumer (Template Notice + Non-Binding block)
- Inline signature-field pattern — 3rd recipe consumer (proposal + quote +
  mou). Flagged for Phase-4 graduation to signature-field-block primitive.

Architecture decisions codified:
- `recitals-block` retired from Day-0 queue (v1 evidence shows numbered
  clauses, not WHEREAS preambles).
- `legal-disclaimer-strip` absorbed into `callout neutral` (Template Notice
  block uses neutral tone with title).
- Day-0 component queue formally closed (8 planned; 7 built + 1 absorbed).

Content adapted from v1-reference/domains/legal/templates/mou.en.html.
Placeholder prose preserved.

Renders to 4 pages under v2 defaults; target_pages [2, 4], page_limit 4.

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
RECIPE_NAME = "legal-mou"


# ---------------------------------------------------------------- schema


def test_mou_loads():
    r = load_recipe(RECIPE_NAME)
    assert r["name"] == RECIPE_NAME
    assert r["namespace"] == "katib"
    assert r["version"] == "0.1.0"


def test_mou_en_only():
    r = load_recipe(RECIPE_NAME)
    assert r["languages"] == ["en"]


def test_mou_page_targets():
    r = load_recipe(RECIPE_NAME)
    assert r["target_pages"] == [2, 4]
    assert r["page_limit"] == 4


def test_mou_has_25_sections():
    r = load_recipe(RECIPE_NAME)
    assert len(r["sections"]) == 25


def test_mou_component_mix():
    """25 sections = 13 module + 7 clause-list + 4 callout + 1 signature-field-block.

    Updated for post-Phase-3 signature-field-block graduation: §25 (signatory grid)
    migrated from inline module raw_body → dedicated signature-field-block primitive.
    """
    r = load_recipe(RECIPE_NAME)
    from collections import Counter
    counts = Counter(s["component"] for s in r["sections"])
    assert counts["module"] == 13
    assert counts["clause-list"] == 7
    assert counts["callout"] == 4
    assert counts["signature-field-block"] == 1


# ---------------------------------------------------------------- production proofs


def test_mou_first_clause_list_consumer():
    """FIRST PRODUCTION CONSUMER of clause-list primitive — 7 uses.
    Each invocation is a distinct legal-clause list (§3, §4, §5-A,
    §5-B, §7, §8, §9)."""
    r = load_recipe(RECIPE_NAME)
    clause_lists = [s for s in r["sections"] if s["component"] == "clause-list"]
    assert len(clause_lists) == 7
    # Each clause-list has items
    for cl in clause_lists:
        items = cl["inputs"]["items"]
        assert len(items) >= 2  # every list has at least 2 clauses
    # Total item count: 3+3+3+3+3+3+2 = 20
    total_items = sum(len(cl["inputs"]["items"]) for cl in clause_lists)
    assert total_items == 20


def test_mou_heaviest_module_numbered_deployment():
    """HEAVIEST module numbered deployment ever: 10 uses (§1-§10).
    Prior records: white-paper Day 13 (6 consecutive), proposal Day 14 (5)."""
    r = load_recipe(RECIPE_NAME)
    numbered = [s for s in r["sections"]
                if s["component"] == "module" and s.get("variant") == "numbered"]
    assert len(numbered) == 10
    # Numbers 1 through 10 in order
    numbers = [s["inputs"]["number"] for s in numbered]
    assert numbers == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_mou_uses_two_callout_info_blocks_for_parties():
    """3rd + 4th production consumer of callout info tone.
    Parties A and B are rendered as stacked info callouts matching v1."""
    r = load_recipe(RECIPE_NAME)
    info_callouts = [s for s in r["sections"]
                     if s["component"] == "callout"
                     and s["inputs"].get("tone") == "info"]
    assert len(info_callouts) == 2
    titles = [c["inputs"]["title"] for c in info_callouts]
    assert titles == ["Party A", "Party B"]


def test_mou_uses_two_callout_neutral_blocks():
    """5th + 6th consumer of callout neutral tone.
    Template Notice (absorbs legal-disclaimer-strip) + Non-Binding emphasis."""
    r = load_recipe(RECIPE_NAME)
    neutral_callouts = [s for s in r["sections"]
                       if s["component"] == "callout"
                       and s["inputs"].get("tone") == "neutral"]
    assert len(neutral_callouts) == 2
    # First is Template Notice (has title)
    assert neutral_callouts[0]["inputs"]["title"] == "Template Notice"
    # Second is Non-Binding emphasis (no title)
    assert "title" not in neutral_callouts[1]["inputs"]


def test_mou_costs_section_has_no_clause_list():
    """§10 Costs is prose-only (no clause-list) per v1 — validates
    that clause-list usage is evidence-driven, not mechanical."""
    r = load_recipe(RECIPE_NAME)
    # Find §10 module
    costs = next(s for s in r["sections"]
                 if s["component"] == "module"
                 and s.get("inputs", {}).get("number") == 10)
    assert costs["inputs"]["title"] == "Costs (binding)"
    assert "body" in costs["inputs"]
    # No clause-list immediately after
    costs_idx = r["sections"].index(costs)
    # §10 is last numbered section — next should be Execution (plain module)
    if costs_idx + 1 < len(r["sections"]):
        after = r["sections"][costs_idx + 1]
        assert after["component"] != "clause-list"


# ---------------------------------------------------------------- validation + content-lint


def test_mou_validates_clean():
    v = ops.validate_recipe_full(RECIPE_NAME)
    assert v.ok, f"validation failed: {[i.message for i in v.issues]}"


def test_mou_validates_strict_clean():
    v = ops.validate_recipe_full(RECIPE_NAME, strict=True)
    assert v.ok, f"strict validation failed: {[i.message for i in v.issues]}"
    content_issues = [i for i in v.issues if i.category == "content"]
    assert content_issues == []


# ---------------------------------------------------------------- render + content


def test_mou_renders_en():
    html, _ = compose(RECIPE_NAME, "en")
    assert "katib-clause-list" in html
    assert "katib-callout--info" in html
    assert "katib-callout--neutral" in html
    assert "katib-module--numbered" in html


def test_mou_pdf_within_target_pages(tmp_path):
    """target_pages [2, 4]; renders to 4 pages given clause density."""
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "mou.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    reader = PdfReader(str(pdf))
    assert 2 <= len(reader.pages) <= 4


def test_mou_renders_all_v1_content(tmp_path):
    """Every fixed phrase from v1 MoU should survive to the PDF."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    pdf = render_to_pdf(html, tmp_path / "mou.en.pdf", base_url=REPO_ROOT)
    raw = "\n".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    flat = re.sub(r"\s+", " ", raw).strip()

    # Masthead
    assert "Memorandum of Understanding".upper() in flat.upper()
    assert "MOU-2026-0042" in flat
    assert "2026-04-24" in flat
    # Template Notice
    assert "Template Notice" in flat
    assert "counsel" in flat
    # §1 The Parties
    assert "The Parties" in flat
    assert "Party A" in flat
    assert "Party B" in flat
    assert "jasem | katib" in flat
    # §2 Background
    assert "Background" in flat
    # §3 Purpose + clauses
    assert "Purpose" in flat
    assert "collaboration" in flat or "partnership" in flat
    # §4 Scope
    assert "Scope of Cooperation" in flat
    # §5 Responsibilities (both Party A and Party B)
    assert "Responsibilities" in flat
    assert "Party A shall" in flat
    assert "Party B shall" in flat
    # §6 Non-Binding
    assert "Non-Binding" in flat
    assert "non-binding" in flat
    # §7 Confidentiality
    assert "Confidentiality" in flat
    assert "confidential" in flat
    # §8 Term
    assert "Term and Termination" in flat
    # §9 Governing Law
    assert "Governing Law" in flat
    assert "United Arab Emirates" in flat
    # §10 Costs
    assert "Costs" in flat
    # Execution
    assert "EXECUTION" in flat.upper()
    # Signature fields
    assert "For Party A".upper() in flat.upper()
    assert "For Party B".upper() in flat.upper()


def test_mou_has_seven_clause_list_elements_in_html():
    """Regression guard: 7 distinct clause-list <ol> elements in rendered HTML."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    ol_count = len(re.findall(r'<ol class="katib-clause-list"', html))
    assert ol_count == 7


def test_mou_has_twenty_clause_list_items_in_html():
    """Regression guard: 3+3+3+3+3+3+2 = 20 clause-list <li> items rendered."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    li_count = len(re.findall(r'<li class="katib-clause-list__item">', html))
    assert li_count == 20


def test_mou_has_ten_numbered_modules_in_html():
    """Regression guard: 10 module numbered sections (§1-§10)."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    matches = re.findall(
        r'<section class="katib-section katib-module katib-module--numbered"',
        html,
    )
    assert len(matches) == 10


def test_mou_has_two_info_callouts_in_html():
    """Regression guard: 2 callout info elements (Party A + Party B)."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    matches = re.findall(r'class="katib-callout katib-callout--info"', html)
    assert len(matches) == 2


def test_mou_has_two_neutral_callouts_in_html():
    """Regression guard: 2 callout neutral elements (Template Notice + Non-Binding)."""
    import re
    html, _ = compose(RECIPE_NAME, "en")
    matches = re.findall(r'class="katib-callout katib-callout--neutral"', html)
    assert len(matches) == 2


# ---------------------------------------------------------------- audit + registration


def test_mou_in_capabilities():
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    recipes = caps.get("recipes", {})
    assert RECIPE_NAME in recipes
    assert recipes[RECIPE_NAME]["namespace"] == "katib"


def test_mou_audit_entry_exists():
    audit = (REPO_ROOT / "memory" / "recipe-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("recipe") == RECIPE_NAME and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1


def test_clause_list_in_capabilities():
    """clause-list component registered in capabilities.yaml."""
    caps_path = REPO_ROOT / "capabilities.yaml"
    caps = yaml.safe_load(caps_path.read_text(encoding="utf-8"))
    components = caps.get("components", {})
    assert "clause-list" in components
    assert components["clause-list"]["tier"] == "primitive"


def test_clause_list_audit_entry_exists():
    """clause-list component register audit entry exists."""
    audit = (REPO_ROOT / "memory" / "component-audit.jsonl").read_text(encoding="utf-8")
    import json
    lines = [json.loads(line) for line in audit.splitlines() if line.strip()]
    register_entries = [
        e for e in lines
        if e.get("component") == "clause-list" and e.get("action") == "register"
    ]
    assert len(register_entries) >= 1
