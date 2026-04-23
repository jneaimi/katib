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
