"""multi-party-signature-block section — schema + render + variants.

Phase 3 Day 7 component. Day-0 queue item #3 (of 6). Enables formal
documents with 2+ signatories (NOC, MOU) to render a responsive
signature grid in one section rather than composing multiple
signature-block primitives.

Phase-3 dependents: formal/noc (Day 8), legal/mou (later). 2 firm
dependents — below automated graduation threshold, intent-verified
via ADR Day 7 entry (same pattern as Day-5 masthead-personal).
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_mps_block_loads_against_schema():
    c = load_component("multi-party-signature-block")
    assert c["tier"] == "section"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_mps_block_parties_required():
    c = load_component("multi-party-signature-block")
    parties_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "parties" in inp),
        None,
    )
    assert parties_decl is not None
    assert parties_decl["required"] is True


def test_mps_block_variants_declared():
    c = load_component("multi-party-signature-block")
    variants = c.get("variants", [])
    assert "line-over" in variants
    assert "minimal" in variants


def test_mps_block_heading_optional():
    c = load_component("multi-party-signature-block")
    heading_decl = next(
        (next(iter(inp.values())) for inp in c["accepts"]["inputs"] if "heading" in inp),
        None,
    )
    assert heading_decl is not None
    assert heading_decl["required"] is False


# ---------------------------------------------------------------- render


def _inline_recipe(tmp_path: Path, *, parties: list[dict], variant: str | None = None, lang: str = "en") -> Path:
    import yaml
    recipe = {
        "name": "mps-test",
        "version": "0.1.0",
        "namespace": "katib",
        "languages": [lang],
        "sections": [
            {
                "component": "multi-party-signature-block",
                **({"variant": variant} if variant else {}),
                "inputs": {"parties": parties},
            }
        ],
    }
    rfile = tmp_path / "mps.yaml"
    rfile.write_text(yaml.safe_dump(recipe, sort_keys=False, allow_unicode=True))
    return rfile


NOC_PARTIES = [
    {"name": "Alex Acme", "title": "HR Manager", "email": "hr@example.com"},
    {"name": "Authorised signatory", "title": "Signature & company stamp"},
]


def test_mps_block_renders_en_two_party(tmp_path):
    rfile = _inline_recipe(tmp_path, parties=NOC_PARTIES)
    html, _ = compose(str(rfile), "en")
    # Default variant is line-over
    assert "katib-multi-party-signature-block--line-over" in html
    # Both parties rendered
    assert "Alex Acme" in html
    assert "HR Manager" in html
    assert "Authorised signatory" in html
    # Email only on first party
    assert "hr@example.com" in html


def test_mps_block_renders_ar(tmp_path):
    rfile = _inline_recipe(
        tmp_path,
        parties=[
            {"name": "أليكس أكمي", "title": "مدير الموارد البشرية"},
            {"name": "الموقع المفوض", "title": "التوقيع وختم الشركة"},
        ],
        lang="ar",
    )
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert "أليكس أكمي" in html


def test_mps_block_email_forced_ltr_in_arabic(tmp_path):
    """Email addresses must render dir=ltr inside AR templates."""
    rfile = _inline_recipe(
        tmp_path,
        parties=[{"name": "أليكس", "email": "alex@acme.test"}],
        lang="ar",
    )
    html, _ = compose(str(rfile), "ar")
    assert 'class="katib-multi-party-signature-block__email" dir="ltr">alex@acme.test' in html


def test_mps_block_renders_three_party_grid(tmp_path):
    """Flexbox grid must accommodate 3+ parties (not hardcoded 2-column)."""
    rfile = _inline_recipe(
        tmp_path,
        parties=[
            {"name": "Party A"},
            {"name": "Party B"},
            {"name": "Witness"},
        ],
    )
    html, _ = compose(str(rfile), "en")
    # All three parties rendered
    assert "Party A" in html
    assert "Party B" in html
    assert "Witness" in html
    # Count actual `__box` div elements — class name also appears in the
    # inlined <style> block, so we count element-opening substrings instead
    box_count = html.count('<div class="katib-multi-party-signature-block__box">')
    assert box_count == 3


def test_mps_block_line_over_variant_has_top_border_rule(tmp_path):
    """line-over variant must emit the class; stylesheet provides the top border."""
    rfile = _inline_recipe(tmp_path, parties=NOC_PARTIES, variant="line-over")
    html, _ = compose(str(rfile), "en")
    assert "katib-multi-party-signature-block--line-over" in html
    # Stylesheet contract — line-over rule present in the emitted CSS
    assert ".katib-multi-party-signature-block--line-over" in html
    assert "border-top" in html


def test_mps_block_minimal_variant_strips_border(tmp_path):
    """minimal variant declares the class but no border-top rule applies."""
    rfile = _inline_recipe(tmp_path, parties=NOC_PARTIES, variant="minimal")
    html, _ = compose(str(rfile), "en")
    assert "katib-multi-party-signature-block--minimal" in html


def test_mps_block_heading_rendered_when_set(tmp_path):
    import yaml
    recipe = {
        "name": "mps-test",
        "version": "0.1.0",
        "namespace": "katib",
        "languages": ["en"],
        "sections": [{
            "component": "multi-party-signature-block",
            "inputs": {
                "heading": "Signed by the Parties",
                "parties": NOC_PARTIES,
            },
        }],
    }
    rfile = tmp_path / "mps.yaml"
    rfile.write_text(yaml.safe_dump(recipe, sort_keys=False))
    html, _ = compose(str(rfile), "en")
    assert "Signed by the Parties" in html
    assert "katib-multi-party-signature-block__heading" in html


def test_mps_block_heading_omitted_when_unset(tmp_path):
    rfile = _inline_recipe(tmp_path, parties=NOC_PARTIES)
    html, _ = compose(str(rfile), "en")
    # The class string appears in inlined <style>; check for the h3 element itself
    assert '<h3 class="katib-multi-party-signature-block__heading"' not in html


# ---------------------------------------------------------------- hygiene


def test_mps_block_styles_use_tokens_only():
    css = (REPO_ROOT / "components" / "sections" / "multi-party-signature-block" / "styles.css").read_text()
    import re
    hex_refs = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
    assert hex_refs == [], f"hex colors in styles.css: {hex_refs}"


def test_mps_block_templates_share_semantic_structure():
    base = REPO_ROOT / "components" / "sections" / "multi-party-signature-block"
    en = (base / "en.html").read_text()
    ar = (base / "ar.html").read_text()
    for token in (
        "katib-multi-party-signature-block__grid",
        "katib-multi-party-signature-block__box",
        "katib-multi-party-signature-block__name",
    ):
        assert token in en
        assert token in ar
    assert 'dir="rtl"' in ar
