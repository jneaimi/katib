"""tag-chips primitive — schema invariants + render + RTL chip mirroring.

Phase 3 Day 18 component (2 of 3 for the CV infra sprint). Auto-graduated
through the request log (3 verified dependents: personal-cv primary +
Deferred bio/blog). Inline tag-pill list for tags, tools, keywords.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_tag_chips_loads_against_schema():
    c = load_component("tag-chips")
    assert c["tier"] == "primitive"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_tag_chips_items_required():
    c = load_component("tag-chips")
    inputs_by_name = {
        next(iter(inp.keys())): next(iter(inp.values()))
        for inp in c["accepts"]["inputs"]
    }
    assert inputs_by_name["items"]["required"] is True


def test_tag_chips_token_contract():
    c = load_component("tag-chips")
    required = set(c["requires"]["tokens"])
    assert {"text", "tag_bg"}.issubset(required)


def test_tag_chips_has_no_variants():
    c = load_component("tag-chips")
    assert c.get("variants", []) == []


# ---------------------------------------------------------------- render


def _inline_recipe(tmp_path: Path, lang: str = "en") -> Path:
    rfile = tmp_path / "tc.yaml"
    rfile.write_text(
        "name: tc-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: tag-chips\n"
        "    inputs:\n"
        "      items:\n"
        '        - "Python"\n'
        '        - "TypeScript"\n'
        '        - "PostgreSQL"\n'
    )
    return rfile


def test_tag_chips_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert "<ul" in html
    assert 'class="katib-tag-chips"' in html
    # 3 chips
    assert html.count('class="katib-tag-chips__chip"') == 3
    assert "Python" in html
    assert "TypeScript" in html


def test_tag_chips_renders_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html


def test_tag_chips_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "tc.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 1800


def test_tag_chips_accepts_mapping_form(tmp_path):
    """Items can be strings OR {text} mappings (primitive consistency
    with clause-list + data-table)."""
    rfile = tmp_path / "tc.yaml"
    rfile.write_text(
        "name: tc-map\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: tag-chips\n"
        "    inputs:\n"
        "      items:\n"
        '        - {text: "Mapping-form tag"}\n'
        '        - "String-form tag"\n'
    )
    html, _ = compose(str(rfile), "en")
    assert "Mapping-form tag" in html
    assert "String-form tag" in html
    assert html.count('class="katib-tag-chips__chip"') == 2


def test_tag_chips_wrap_section_has_lang_attr(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert 'katib-tag-chips-wrap' in html
    assert 'lang="en"' in html


def test_tag_chips_ul_has_lang_attr(tmp_path):
    """Inner <ul> also carries lang= so RTL scoping in styles.css
    applies correctly."""
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    # The ul itself should have lang="ar"
    import re
    matches = re.findall(r'<ul class="katib-tag-chips" lang="ar"', html)
    assert len(matches) == 1
