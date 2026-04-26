"""Phase 2 Day 13 — core/content_lint.py unit tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core import content_lint as cl  # noqa: E402


# ================================================================ extract_text


def test_extract_text_strips_html_tags():
    raw = "<p>Hello <b>world</b></p>"
    assert "<p>" not in cl.extract_text(raw)
    assert "Hello" in cl.extract_text(raw)
    assert "world" in cl.extract_text(raw)


def test_extract_text_strips_jinja():
    raw = "{{ input.title }} is visible"
    text = cl.extract_text(raw)
    assert "{{" not in text
    assert "visible" in text


def test_extract_text_removes_style_blocks():
    raw = "<style>body { color: red; }</style><p>visible</p>"
    text = cl.extract_text(raw)
    assert "color: red" not in text
    assert "visible" in text


def test_extract_text_removes_script_blocks():
    raw = "<script>alert('x')</script><p>visible</p>"
    text = cl.extract_text(raw)
    assert "alert" not in text


# ================================================================ guess_language


def test_guess_language_by_suffix_en(tmp_path):
    p = tmp_path / "module.en.html"
    p.write_text("<p>anything</p>")
    assert cl.guess_language(p, "anything") == "en"


def test_guess_language_by_suffix_ar(tmp_path):
    p = tmp_path / "module.ar.html"
    p.write_text("<p>anything</p>")
    assert cl.guess_language(p, "anything") == "ar"


def test_guess_language_by_chars_arabic():
    text = "مرحبا بالعالم هذا نص عربي طويل لاختبار اللغة"
    assert cl.guess_language(None, text) == "ar"


def test_guess_language_by_chars_english():
    text = "Hello world this is a long english sentence to test language detection"
    assert cl.guess_language(None, text) == "en"


# ================================================================ English rules


def test_en_banned_opener():
    text = "In today's world of rapid change, we must adapt."
    v = cl.lint_english(text)
    assert any(x.rule == "banned-opener" for x in v)


def test_en_emphasis_crutch():
    text = "Let me be clear: this is a test."
    v = cl.lint_english(text)
    assert any(x.rule == "emphasis-crutch" for x in v)


def test_en_vague_declarative():
    text = "The results are amazing. Truly unprecedented."
    v = cl.lint_english(text)
    assert any(x.rule == "vague-declarative" for x in v)


def test_en_meta_commentary():
    text = "In this article we will explore three topics."
    v = cl.lint_english(text)
    assert any(x.rule == "meta-commentary" for x in v)


def test_en_clean_text_returns_empty():
    text = "The team shipped the feature on Tuesday. Two customers reported issues."
    assert cl.lint_english(text) == []


def test_en_severities_correct():
    text = "In today's world, we live in an era of constant change."
    v = cl.lint_english(text)
    for x in v:
        assert x.severity in ("error", "warn")


# ================================================================ Arabic rules


def test_ar_banned_opener():
    text = "في عالمنا اليوم نواجه تحديات جديدة."
    v = cl.lint_arabic(text)
    assert any(x.rule == "banned-opener" for x in v)


def test_ar_emphasis_crutch():
    text = "وهنا تكمن المفارقة في كل ما نفعله."
    v = cl.lint_arabic(text)
    assert any(x.rule == "emphasis-crutch" for x in v)


def test_ar_vague_declarative():
    text = "النتائج مذهلة والمستقبل واعد."
    v = cl.lint_arabic(text)
    rules = {x.rule for x in v}
    assert "vague-declarative" in rules


def test_ar_meta_commentary():
    text = "في هذا المقال سنتناول ثلاثة محاور."
    v = cl.lint_arabic(text)
    assert any(x.rule == "meta-commentary" for x in v)


def test_ar_waw_chain():
    text = "ذهبنا وأكلنا وشربنا ورجعنا إلى المنزل."
    v = cl.lint_arabic(text)
    assert any(x.rule == "waw-chain" for x in v)


def test_ar_ambiguous_tech_term():
    text = "الوكيل يحتاج إلى تعريف أوضح."
    v = cl.lint_arabic(text)
    assert any(x.rule == "ambiguous-tech-term" for x in v)


def test_ar_untranslated_abbrev_flagged():
    text = "نحن نستخدم API في كل مكان. لم نترجمه."
    v = cl.lint_arabic(text)
    assert any(x.rule == "untranslated-abbreviation" for x in v)


def test_ar_translated_abbrev_passes():
    text = "نستخدم واجهة برمجة التطبيقات (API) في كل مكان."
    v = cl.lint_arabic(text)
    assert not any(x.rule == "untranslated-abbreviation" for x in v)


def test_ar_clean_text_returns_empty():
    text = "شحنّا الميزة يوم الثلاثاء. أبلغنا عميلان عن مشاكل."
    v = cl.lint_arabic(text)
    # Filter out warn-level noise (tech term/jargon) — clean text should have no errors
    errors = [x for x in v if x.severity == "error"]
    assert errors == []


# ================================================================ lint dispatcher


def test_lint_dispatches_en():
    v = cl.lint("The results are amazing.", "en")
    assert any(x.rule == "vague-declarative" for x in v)


def test_lint_dispatches_ar():
    v = cl.lint("النتائج مذهلة.", "ar")
    assert any(x.rule == "vague-declarative" for x in v)


def test_lint_unknown_lang_raises():
    with pytest.raises(ValueError, match="unsupported lang"):
        cl.lint("text", "jp")


# ================================================================ Violation.as_dict


def test_violation_as_dict_shape():
    v = cl.Violation("r", "error", "p", 1, "snippet")
    d = v.as_dict()
    assert set(d.keys()) == {"rule", "severity", "pattern", "line", "snippet"}


# ================================================================ lint_file


def test_lint_file_reads_and_dispatches(tmp_path):
    p = tmp_path / "test.en.html"
    p.write_text("<p>In today's world, we live in an era of change.</p>")
    violations, lang = cl.lint_file(p)
    assert lang == "en"
    assert len(violations) > 0


def test_lint_file_respects_forced_lang(tmp_path):
    p = tmp_path / "unknown.html"
    p.write_text("<p>The results are amazing</p>")
    violations, lang = cl.lint_file(p, lang="en")
    assert lang == "en"
    assert any(x.rule == "vague-declarative" for x in violations)


# ================================================================ ARABIC_IN_SVG_TEXT


def test_arabic_in_svg_text_fires():
    """Arabic inside <svg><text> is a hard error."""
    html = '<svg viewBox="0 0 100 100"><text x="10" y="20">المستوى السادس</text></svg>'
    v = cl.lint_html_arabic_in_svg_text(html)
    assert len(v) == 1
    assert v[0].rule == "ARABIC_IN_SVG_TEXT"
    assert v[0].severity == "error"
    assert "المستوى" in v[0].snippet


def test_arabic_in_svg_text_html_overlay_does_not_fire():
    """HTML-overlay pattern: Arabic label is outside SVG, not inside <text>."""
    html = (
        '<figure style="position:relative;">'
        '<svg viewBox="0 0 560 400"><rect x="40" y="36" width="480" height="44"/></svg>'
        '<div style="position:absolute;top:50pt;left:60pt;">المستوى</div>'
        "</figure>"
    )
    v = cl.lint_html_arabic_in_svg_text(html)
    assert v == []


def test_english_in_svg_text_does_not_fire():
    """English inside SVG <text> is fine — only Arabic triggers the rule."""
    html = '<svg viewBox="0 0 100 100"><text x="10" y="20">Level Six</text></svg>'
    v = cl.lint_html_arabic_in_svg_text(html)
    assert v == []


def test_arabic_in_svg_text_multiline_svg_fires():
    """Arabic in <text> inside a multi-line, deeply nested SVG block still fires."""
    html = (
        '<svg\n  viewBox="0 0 200 200"\n  xmlns="http://www.w3.org/2000/svg">\n'
        "  <g>\n    <g>\n"
        '      <text\n        x="10"\n        y="50"\n      >الإبداع</text>\n'
        "    </g>\n  </g>\n</svg>"
    )
    v = cl.lint_html_arabic_in_svg_text(html)
    assert len(v) == 1
    assert v[0].rule == "ARABIC_IN_SVG_TEXT"


def test_arabic_outside_svg_does_not_fire():
    """Arabic in body prose (outside SVG) must not trigger ARABIC_IN_SVG_TEXT."""
    html = "<p>هذا نص عربي في الجسم الرئيسي للمستند</p>"
    v = cl.lint_html_arabic_in_svg_text(html)
    assert v == []


def test_arabic_in_svg_text_multiple_offenders():
    """Multiple <text> elements with Arabic produce multiple violations."""
    html = (
        '<svg viewBox="0 0 200 200">'
        '<text x="10" y="20">العمل</text>'
        '<text x="10" y="40">المالك</text>'
        '<text x="10" y="60">المستوى</text>'
        "</svg>"
    )
    v = cl.lint_html_arabic_in_svg_text(html)
    assert len(v) == 3
    assert all(x.rule == "ARABIC_IN_SVG_TEXT" for x in v)


def test_arabic_in_svg_text_empty_text_does_not_fire():
    """Empty <text> elements are skipped (no real content to flag)."""
    html = '<svg viewBox="0 0 100 100"><text x="10" y="20"></text></svg>'
    v = cl.lint_html_arabic_in_svg_text(html)
    assert v == []


def test_lint_file_runs_html_rules(tmp_path):
    """lint_file must surface HTML-level rules alongside text-level rules."""
    p = tmp_path / "broken.ar.html"
    p.write_text(
        '<svg viewBox="0 0 100 100"><text x="10" y="20">المستوى</text></svg>'
    )
    violations, _ = cl.lint_file(p)
    assert any(x.rule == "ARABIC_IN_SVG_TEXT" for x in violations)


# ================================================================ FIGCAPTION_INSIDE_RELATIVE


def test_figcaption_inside_relative_fires():
    """figure[position:relative] containing both <svg> and <figcaption> is a hard error."""
    html = (
        '<figure style="position: relative; margin: 0;">'
        '<svg viewBox="0 0 100 100"><rect/></svg>'
        '<figcaption>caption</figcaption>'
        '</figure>'
    )
    v = cl.lint_html_figcaption_inside_relative(html)
    assert len(v) == 1
    assert v[0].rule == "FIGCAPTION_INSIDE_RELATIVE"
    assert v[0].severity == "error"


def test_figcaption_outside_relative_div_does_not_fire():
    """The safe pattern: relative div wraps svg only, figcaption sibling outside."""
    html = (
        '<figure style="margin: 0;">'
        '<div style="position: relative;">'
        '<svg viewBox="0 0 100 100"><rect/></svg>'
        '</div>'
        '<figcaption>caption</figcaption>'
        '</figure>'
    )
    v = cl.lint_html_figcaption_inside_relative(html)
    assert v == []


def test_figure_relative_without_figcaption_does_not_fire():
    """figure[position:relative] with only <svg> (no figcaption) is fine."""
    html = (
        '<figure style="position: relative;">'
        '<svg><rect/></svg>'
        '</figure>'
    )
    v = cl.lint_html_figcaption_inside_relative(html)
    assert v == []


def test_figure_relative_with_figcaption_no_svg_does_not_fire():
    """figure[position:relative] with only <figcaption> (no svg) is fine."""
    html = (
        '<figure style="position: relative;">'
        '<img src="x.png">'
        '<figcaption>cap</figcaption>'
        '</figure>'
    )
    v = cl.lint_html_figcaption_inside_relative(html)
    assert v == []


def test_figure_no_relative_does_not_fire():
    """figure without position:relative — no anchor-context bug to detect."""
    html = (
        '<figure>'
        '<svg><rect/></svg>'
        '<figcaption>cap</figcaption>'
        '</figure>'
    )
    v = cl.lint_html_figcaption_inside_relative(html)
    assert v == []


def test_lint_file_runs_figcaption_rule(tmp_path):
    """lint_file must surface FIGCAPTION_INSIDE_RELATIVE alongside other HTML rules."""
    p = tmp_path / "broken.en.html"
    p.write_text(
        '<figure style="position: relative;">'
        '<svg viewBox="0 0 100 100"><rect/></svg>'
        '<figcaption>caption</figcaption>'
        '</figure>'
    )
    violations, _ = cl.lint_file(p)
    assert any(x.rule == "FIGCAPTION_INSIDE_RELATIVE" for x in violations)
