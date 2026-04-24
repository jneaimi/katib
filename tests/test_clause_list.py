"""clause-list primitive — schema invariants + render + RTL behavior.

Phase 3 Day 17 component. 8th Phase-3 component built; replaces the
original Day-0 queue's `recitals-block` per v1 evidence showing legal
domain uses numbered-clause ordered lists (mou 7×, nda 7×,
service-agreement 10×, engagement-letter 1×) rather than WHEREAS
preambles. Honest-intent graduation (1 recipe dependent at ship time;
7 internal MoU instances + 3 Deferred legal recipes justify the build).

FIRST PRODUCTION CONSUMER: legal/mou Day 17.
"""
from __future__ import annotations

from pathlib import Path

from core.compose import compose, load_component
from core.render import render_to_pdf

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------- schema


def test_clause_list_loads_against_schema():
    c = load_component("clause-list")
    assert c["tier"] == "primitive"
    assert c["version"] == "0.1.0"
    assert c["namespace"] == "katib"
    assert set(c["languages"]) == {"en", "ar"}


def test_clause_list_items_required():
    c = load_component("clause-list")
    inputs_by_name = {
        next(iter(inp.keys())): next(iter(inp.values()))
        for inp in c["accepts"]["inputs"]
    }
    assert inputs_by_name["items"]["required"] is True
    assert inputs_by_name["start"]["required"] is False


def test_clause_list_token_contract():
    c = load_component("clause-list")
    required = set(c["requires"]["tokens"])
    assert {"text", "accent"}.issubset(required)


def test_clause_list_has_no_variants():
    """Initial version has no variants — shape is stable across legal docs."""
    c = load_component("clause-list")
    assert c.get("variants", []) == []


# ---------------------------------------------------------------- render


def _inline_recipe(tmp_path: Path, lang: str = "en", with_start: bool = False) -> Path:
    start_line = "      start: 4\n" if with_start else ""
    rfile = tmp_path / "cl.yaml"
    rfile.write_text(
        "name: cl-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        f"languages: [{lang}]\n"
        "sections:\n"
        "  - component: clause-list\n"
        "    inputs:\n"
        + start_line +
        "      items:\n"
        '        - "First clause text."\n'
        '        - "Second clause text."\n'
        '        - "Third clause text."\n'
    )
    return rfile


def test_clause_list_renders_en(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    # Semantic structure
    assert "<ol" in html
    assert 'class="katib-clause-list"' in html
    # 3 items
    assert html.count('class="katib-clause-list__item"') == 3
    # Content preserved
    assert "First clause text." in html
    assert "Second clause text." in html
    assert "Third clause text." in html


def test_clause_list_renders_ar(tmp_path):
    """AR render: dir='rtl' declared on the <ol> so physical-property CSS
    flips correctly (number on the right side)."""
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    assert 'class="katib-clause-list"' in html


def test_clause_list_renders_to_pdf(tmp_path):
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    pdf = render_to_pdf(html, tmp_path / "cl.en.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 2000


def test_clause_list_renders_to_pdf_ar(tmp_path):
    rfile = _inline_recipe(tmp_path, lang="ar")
    html, _ = compose(str(rfile), "ar")
    pdf = render_to_pdf(html, tmp_path / "cl.ar.pdf", base_url=REPO_ROOT)
    assert pdf.exists()
    assert pdf.stat().st_size > 2000


def test_clause_list_start_attribute_when_set(tmp_path):
    """start input continues numbering from a specified value —
    useful for split clause-lists within a section."""
    rfile = _inline_recipe(tmp_path, with_start=True)
    html, _ = compose(str(rfile), "en")
    assert 'start="4"' in html
    # counter-reset style attribute reflects the continuation
    assert "counter-reset: clause 3" in html


def test_clause_list_no_start_when_unset(tmp_path):
    """No start attr + no inline counter-reset override when start is unset.
    The base CSS rule .katib-clause-list { counter-reset: clause } always
    applies — only the inline override (for continuation) should be absent."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert 'start="' not in html
    # The inline override style attribute should not be present on <ol>
    assert 'style="counter-reset: clause' not in html


def test_clause_list_items_render_as_li_elements(tmp_path):
    """Every item becomes a <li class="katib-clause-list__item">."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    import re
    li_count = len(re.findall(r'<li class="katib-clause-list__item">', html))
    assert li_count == 3


def test_clause_list_wrap_section_has_lang_attr(tmp_path):
    """Root wrapper section carries lang= for validator a11y check
    (same pattern as data-table — validator regex only accepts
    section/div/article/main as root element)."""
    rfile = _inline_recipe(tmp_path)
    html, _ = compose(str(rfile), "en")
    assert 'katib-clause-list-wrap' in html
    assert 'lang="en"' in html


def test_clause_list_items_accept_mapping_form(tmp_path):
    """Items can be strings OR {text} mappings (primitive consistency
    with data-table). Mapping form reads .text."""
    rfile = tmp_path / "cl.yaml"
    rfile.write_text(
        "name: cl-map\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: clause-list\n"
        "    inputs:\n"
        "      items:\n"
        '        - {text: "Mapping-form clause."}\n'
        '        - "String-form clause."\n'
    )
    html, _ = compose(str(rfile), "en")
    assert "Mapping-form clause." in html
    assert "String-form clause." in html
    assert html.count('class="katib-clause-list__item"') == 2
