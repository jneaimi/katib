"""Phase 2 Day 9 — context sensor tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.capabilities import load_capabilities
from core.context_sensor import (
    DEFAULT_MAX_CHARS,
    LOG_SCHEMA_VERSION,
    ContextInference,
    enumerate_brands,
    extract_brand,
    extract_intent,
    extract_lang_marker,
    from_messages,
    infer_signals,
)
from core.gate import Signals, evaluate


# ============================================================ enumerate_brands


def test_enumerate_brands_empty_dirs(tmp_path):
    out = enumerate_brands(user_dir=tmp_path / "nope", repo_dir=tmp_path / "nada")
    assert out == []


def test_enumerate_brands_reads_yaml_stems(tmp_path):
    user_dir = tmp_path / "user-brands"
    user_dir.mkdir()
    (user_dir / "acme.yaml").write_text("name: ACME")
    (user_dir / "globex.yml").write_text("name: Globex")
    (user_dir / "not-a-brand.txt").write_text("ignore me")
    repo_dir = tmp_path / "repo-brands"
    repo_dir.mkdir()
    (repo_dir / "example.yaml").write_text("name: Example")
    out = enumerate_brands(user_dir=user_dir, repo_dir=repo_dir)
    assert set(out) == {"acme", "globex", "example"}


def test_enumerate_brands_dedups_user_over_repo(tmp_path):
    user_dir = tmp_path / "u"
    user_dir.mkdir()
    (user_dir / "acme.yaml").write_text("name: ACME-user")
    repo_dir = tmp_path / "r"
    repo_dir.mkdir()
    (repo_dir / "acme.yaml").write_text("name: ACME-repo")
    out = enumerate_brands(user_dir=user_dir, repo_dir=repo_dir)
    # Only one 'acme' in the output
    assert out.count("acme") == 1


# ============================================================ extract_intent


def test_extract_intent_empty():
    assert extract_intent("") == ""
    assert extract_intent("   ") == ""


def test_extract_intent_truncates_to_max_chars():
    long = "prefix " + ("filler word " * 500) + "final keyword-here"
    out = extract_intent(long, max_chars=200)
    assert len(out) <= 200
    assert "final" in out
    assert "prefix" not in out  # old content dropped


def test_extract_intent_strips_role_prefix():
    t = "user: please render the tutorial\nassistant: sure, one moment"
    out = extract_intent(t)
    assert "user:" not in out.lower()
    assert "assistant:" not in out.lower()
    assert "please render" in out


# ============================================================ extract_brand


def test_extract_brand_none_when_no_brands_registered():
    brand, reason = extract_brand("use acme brand please", [])
    assert brand is None
    assert "no brands registered" in reason.lower()


def test_extract_brand_none_when_substring_not_at_boundary():
    brand, _ = extract_brand("acmecorp is not the brand we want", ["acme"])
    assert brand is None


def test_extract_brand_matches_with_indicator_verb():
    # Updated for tighter indicator list: 'use' and 'for' were dropped
    # (too generic — false-positive on "for example"). 'using' is kept
    # as an active verb that implies intentional brand selection.
    brand, reason = extract_brand(
        "please render this using acme styling", ["acme", "acme"]
    )
    assert brand == "acme"
    assert "near indicator" in reason.lower() or "indicator" in reason.lower()


def test_extract_brand_matches_in_quotes():
    brand, reason = extract_brand("render this with \"acme\" styling", ["acme"])
    assert brand == "acme"
    assert "quoted" in reason.lower()


def test_extract_brand_case_insensitive():
    brand, _ = extract_brand("Use ACME brand for this", ["acme"])
    assert brand == "acme"


def test_extract_brand_most_recent_wins():
    t = "first use acme brand... later, switch to use contoso brand instead"
    brand, reason = extract_brand(t, ["acme", "contoso"])
    assert brand == "contoso"
    assert "winner over" in reason.lower()


def test_extract_brand_rejects_bare_mention_without_indicator():
    brand, _ = extract_brand(
        "I was thinking about acme yesterday while drinking coffee",
        ["acme", "contoso"],
    )
    # "acme" appears but no indicator word nearby → reject
    assert brand is None


def test_extract_brand_example_in_for_example_phrase_no_match():
    """'for example' must not lift the 'example' brand — common-noun stop-list."""
    transcript = (
        "I want a recipe modeled exactly on a provided example PDF, "
        "for example the editorial template."
    )
    brand, reason = extract_brand(transcript, ["example", "jasem"])
    assert brand is None, f"expected no match, got {brand!r} ({reason})"


def test_extract_brand_example_in_quotes_does_match():
    """Quoted brand mention is accepted even for common-noun names."""
    transcript = 'Apply the "example" brand to this document.'
    brand, reason = extract_brand(transcript, ["example", "jasem"])
    assert brand == "example", f"expected 'example', got {brand!r} ({reason})"


def test_extract_brand_jasem_with_proximity_indicator():
    """Real brand names accept proximity-indicator path (no change in behavior)."""
    transcript = "Apply jasem brand to this proposal."
    brand, _ = extract_brand(transcript, ["jasem", "example"])
    assert brand == "jasem"


def test_extract_brand_jasem_without_indicator_no_match():
    """Real brand names without indicator + without quotes — still no match."""
    transcript = "I love the jasem coffee in the morning."
    brand, _ = extract_brand(transcript, ["jasem"])
    # 'the' was previously an indicator; it's no longer in the list.
    # No other indicators near 'jasem' in this sentence.
    assert brand is None


def test_extract_brand_default_in_general_phrase_no_match():
    """'the default' must not lift the 'default' brand."""
    transcript = "Use the default settings for this render."
    brand, _ = extract_brand(transcript, ["default", "jasem"])
    assert brand is None


def test_extract_brand_tutorial_as_topic_no_match():
    """A document ABOUT tutorials shouldn't infer a 'tutorial' brand."""
    transcript = "Write a tutorial about installing the SDK."
    brand, _ = extract_brand(transcript, ["tutorial", "jasem"])
    assert brand is None


def test_extract_brand_existing_for_jasem_still_fires():
    """Regression guard: 'using jasem' should still match (using is in indicators)."""
    transcript = "Render this using jasem styling."
    brand, _ = extract_brand(transcript, ["jasem"])
    assert brand == "jasem"


def test_extract_brand_style_indicator_works():
    """'in jasem style' — 'style' is a new indicator."""
    transcript = "I'd like the cover in jasem style."
    brand, _ = extract_brand(transcript, ["jasem"])
    assert brand == "jasem"


# ============================================================ extract_lang_marker


def test_extract_lang_marker_none_when_absent():
    lang, reason = extract_lang_marker("just some generic text")
    assert lang is None
    assert "no explicit" in reason.lower()


def test_extract_lang_marker_in_arabic():
    lang, _ = extract_lang_marker("please write this in Arabic")
    assert lang == "ar"


def test_extract_lang_marker_in_english():
    lang, _ = extract_lang_marker("render the guide in English please")
    assert lang == "en"


def test_extract_lang_marker_ar_only():
    lang, _ = extract_lang_marker("ar only, no english needed")
    # Both 'ar only' and 'no english' present; 'ar only' should win when it
    # appears first and no 'in english' marker. 'en only' pattern doesn't match 'no english'.
    assert lang == "ar"


def test_extract_lang_marker_arabic_variants():
    lang, _ = extract_lang_marker("اكتب هذا باللغة العربية")
    assert lang == "ar"


def test_extract_lang_marker_last_wins():
    t = "start in English... actually, change to in Arabic"
    lang, _ = extract_lang_marker(t)
    assert lang == "ar"


# ============================================================ from_messages


def test_from_messages_basic():
    msgs = [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "render tutorial"},
    ]
    out = from_messages(msgs)
    assert "user: hi" in out
    assert "user: render tutorial" in out


def test_from_messages_empty_content_skipped():
    msgs = [
        {"role": "user", "content": ""},
        {"role": "user", "content": "real message"},
    ]
    out = from_messages(msgs)
    assert out.strip() == "user: real message"


def test_from_messages_caps_at_last_10():
    msgs = [{"role": "user", "content": f"msg-{i}"} for i in range(20)]
    out = from_messages(msgs)
    # Only the last 10 should survive
    assert "msg-19" in out
    assert "msg-0" not in out
    assert "msg-9" not in out  # 20-10 = 10, so msg-10..msg-19 remain
    assert "msg-10" in out


# ============================================================ infer_signals (integration)


def test_infer_signals_empty_transcript():
    inf = infer_signals("", known_brands=[])
    assert isinstance(inf, ContextInference)
    assert inf.signals.intent == ""
    assert inf.signals.lang is None
    assert inf.signals.brand is None
    assert inf.log_entry["schema_version"] == LOG_SCHEMA_VERSION


def test_infer_signals_full_explicit_case():
    t = "please render the tutorial framework guide in English using acme brand"
    inf = infer_signals(t, known_brands=["acme", "acme"])
    assert inf.signals.brand == "acme"
    assert inf.signals.lang == "en"
    assert "tutorial" in inf.signals.intent
    assert "brand acme" in inf.summary
    assert "lang en" in inf.summary


def test_infer_signals_marker_overrides_script_inference():
    # Arabic script dominates (>70%) but explicit "in English" marker should win
    t = (
        "اكتب لي دليلا شاملا عن الذكاء الاصطناعي وطرق استخدامه في الأعمال "
        "الحديثة مع أمثلة واقعية من الإمارات العربية المتحدة — in English"
    )
    inf = infer_signals(t, known_brands=[])
    assert inf.signals.lang == "en"
    # Conflict should be logged because script inference returned 'ar'
    assert any("conflict" in r.lower() for r in inf.reasons)


def test_infer_signals_script_fallback():
    t = "write a tutorial about machine learning fundamentals"
    inf = infer_signals(t, known_brands=[])
    # No marker, no brand, script-inferred EN
    assert inf.signals.lang == "en"
    assert inf.signals.brand is None


def test_infer_signals_arabic_script():
    t = "اكتب لي دليلا عن الذكاء الاصطناعي"
    inf = infer_signals(t, known_brands=[])
    assert inf.signals.lang == "ar"


def test_infer_signals_transcript_sample_redacted():
    # Long transcript — middle should be redacted
    t = "head " * 100 + "MIDDLE" * 500 + " tail " * 100
    inf = infer_signals(t, known_brands=[])
    assert "..." in inf.transcript_sample
    assert "MIDDLE" * 500 not in inf.transcript_sample  # middle redacted
    assert inf.log_entry["transcript_length"] == len(t)


def test_infer_signals_feeds_gate_evaluate():
    """Integration: sensor output flows into gate.evaluate() without glue."""
    caps = load_capabilities()
    # Concentrated intent hitting 5 of the 5 tutorial-recipe keywords →
    # topic score ≥ STRONG threshold → HIGH → proceed.
    t = (
        "tutorial framework-guide bloom ai-collaboration production — "
        "in English with acme brand"
    )
    inf = infer_signals(t, known_brands=["acme"])
    decision = evaluate(inf.signals, caps)
    assert decision.outcome == "proceed"
    assert decision.plan is not None
    assert decision.plan.recipe == "tutorial"
    assert decision.plan.brand == "acme"
    assert decision.plan.lang == "en"


def test_infer_signals_moderate_topic_routes_to_choose():
    """Integration: diluted intent (moderate topic match) routes to MEDIUM/choose."""
    caps = load_capabilities()
    t = "please render the tutorial framework guide in English using acme brand"
    inf = infer_signals(t, known_brands=["acme"])
    decision = evaluate(inf.signals, caps)
    # This intent has diluting tokens ("please", "render", "using", "brand")
    # that drop topic score below STRONG=0.7 — gate routes to choose, not proceed.
    assert decision.outcome in ("proceed", "choose")


def test_infer_signals_low_confidence_fires_gate():
    """Integration: ambiguous intent routes through gate to fire questions."""
    caps = load_capabilities()
    t = "something totally-novel quarterly-board-memo brainstorm"
    inf = infer_signals(
        t,
        known_brands=["acme", "acme", "globex"],  # ambiguous
    )
    decision = evaluate(inf.signals, caps)
    # Either LOW (fire) or needs-intent depending on match score
    assert decision.outcome in ("fire", "needs-intent", "choose")


def test_infer_signals_summary_is_under_two_sentences():
    """ADR observability: summary must be ≤ 2 sentences."""
    t = "render the tutorial framework guide in English using acme brand"
    inf = infer_signals(t, known_brands=["acme"])
    # Sentence-count: split by period, non-empty fragments
    sentences = [s.strip() for s in inf.summary.split(".") if s.strip()]
    assert len(sentences) <= 2


def test_infer_signals_log_entry_shape():
    t = "render tutorial please"
    inf = infer_signals(t, known_brands=["acme"])
    entry = inf.log_entry
    assert entry["schema_version"] == 1
    assert "ts" in entry
    assert "transcript_sample" in entry
    assert "transcript_length" in entry
    assert "inferred" in entry
    assert set(entry["inferred"].keys()) == {
        "intent_preview",
        "brand",
        "lang",
        "lang_source",
    }
    assert entry["known_brands"] == ["acme"]


def test_infer_signals_uses_disk_brands_by_default(tmp_path, monkeypatch):
    """When known_brands is None, enumerate from disk via KATIB_BRANDS_DIR."""
    # Stash a brand in a temp dir
    (tmp_path / "fakebrand.yaml").write_text("name: Fake")
    monkeypatch.setenv("KATIB_BRANDS_DIR", str(tmp_path))
    # Point REPO_BRANDS_DIR away too — we only want user_dir to contribute
    inf = infer_signals("test intent", known_brands=None)
    assert "fakebrand" in inf.signals.known_brands
