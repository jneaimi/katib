"""skill-bar-list primitive — schema invariants + render + level-bar behavior.

Phase 3 Day 18 component (1 of 3 for the CV infra sprint). Auto-graduated
through the request log (3 verified dependents: personal-cv primary +
Deferred portfolio/bio). Used in CV sidebar for Languages + Core Skills
sections.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_skill_bar_list_loads_against_schema():
    c = load_component("skill-bar-list")
    assert c["tier"] == "primitive"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_skill_bar_list_items_required():
    c = load_component("skill-bar-list")
    inputs_by_name = {
        next(iter(inp.keys())): next(iter(inp.values()))
        for inp in c["accepts"]["inputs"]
    }
    assert inputs_by_name["items"]["required"] is True


def test_skill_bar_list_token_contract():
    c = load_component("skill-bar-list")
    required = set(c["requires"]["tokens"])
    assert {"text", "accent", "border"}.issubset(required)


def test_skill_bar_list_has_no_variants():
    c = load_component("skill-bar-list")
    assert c.get("variants", []) == []


# ---------------------------------------------------------------- render


def _inline_recipe(tmp_path: Path, lang: str = "en") -> Path:
    rfile = tmp_path / "sbl.yaml"
    rfile.write_text(
        "name: sbl-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: skill-bar-list\n"
        "    inputs:\n"
        "      items:\n"
        '        - {name: "English", level: 5}\n'
        '        - {name: "Arabic", level: 5}\n'
        '        - {name: "Python", level: 4}\n'
        '        - {name: "Rust", level: 2}\n'
    )
    return rfile


def test_skill_bar_list_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Semantic structure
    assert "<ul" in html
    assert 'class="katib-skill-bar-list"' in html
    # 4 items
    assert html.count('class="katib-skill-bar-list__item"') == 4
    # Content preserved
    assert "English" in html
    assert "Python" in html
    assert "Rust" in html


def test_skill_bar_list_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html


def test_skill_bar_list_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "sbl.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 2000


def test_skill_bar_list_emits_level_modifier_classes(tmp_path):
    """Levels 1-5 each emit a distinct modifier class for CSS fill width."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Two items at level 5
    assert html.count("katib-skill-bar-list__level--l5") >= 2
    # One item at level 4
    assert "katib-skill-bar-list__level--l4" in html
    # One item at level 2
    assert "katib-skill-bar-list__level--l2" in html


def test_skill_bar_list_name_and_level_spans_present(tmp_path):
    """Each item renders a __name span + a __level span."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert html.count('class="katib-skill-bar-list__name"') == 4
    # Level span count: 4 (each item has one)
    import re
    level_spans = re.findall(r'class="katib-skill-bar-list__level katib-skill-bar-list__level--l\d"', html)
    assert len(level_spans) == 4


def test_skill_bar_list_wrap_section_has_lang_attr(tmp_path):
    """Root wrapper for validator a11y check — same pattern as clause-list/data-table."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert 'katib-skill-bar-list-wrap' in html
    assert 'lang="en"' in html
