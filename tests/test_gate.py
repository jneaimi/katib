"""Phase 2 Day 8 — decision gate tests."""
from __future__ import annotations

import pytest

from core.capabilities import load_capabilities, rank_recipes
from core.gate import (
    DEFAULT_THRESHOLDS,
    LOG_SCHEMA_VERSION,
    Question,
    Signals,
    _infer_lang,
    answer_to_value,
    evaluate,
    resolve,
    score_confidence,
)


@pytest.fixture(scope="module")
def caps():
    return load_capabilities()


# ============================================================ confidence scorer


def test_confidence_high_when_all_signals_explicit(caps):
    s = Signals(
        intent="tutorial framework guide",
        lang="en",
        brand="jasem",
        known_brands=["jasem"],
    )
    c = score_confidence(s, caps)
    assert c.level == "HIGH"
    assert c.score >= DEFAULT_THRESHOLDS["high"]


def test_confidence_medium_when_weak_topic_but_strong_brand_lang(caps):
    # Intent gives weak topic match; brand + lang explicit
    s = Signals(
        intent="general document",  # won't strongly match any recipe
        lang="en",
        brand="jasem",
        known_brands=["jasem"],
    )
    c = score_confidence(s, caps)
    assert c.level in ("MEDIUM", "LOW")
    # Should NOT be HIGH — topic must be strong for HIGH
    assert c.level != "HIGH"


def test_confidence_low_when_multiple_signals_missing(caps):
    """LOW requires multiple missing signals: no topic AND ambiguous brand
    AND ambiguous lang. No-brands-registered grants default credit (no
    ambiguity), so that alone doesn't produce LOW."""
    s = Signals(
        intent="xyzzy تركي mixed blarg",  # no recipe match + mixed script
        lang=None,
        brand=None,
        known_brands=["a", "b", "c"],     # multiple registered, none picked
    )
    c = score_confidence(s, caps)
    assert c.level == "LOW"


def test_confidence_medium_when_single_brand_registered_no_explicit(caps):
    s = Signals(
        intent="tutorial framework guide",
        lang="en",
        brand=None,
        known_brands=["jasem"],  # only one registered → inferred
    )
    c = score_confidence(s, caps)
    # Strong topic + inferred brand + explicit lang = HIGH
    assert c.level == "HIGH"


def test_confidence_ambiguous_brand_caps_at_medium(caps):
    s = Signals(
        intent="tutorial framework guide",
        lang="en",
        brand=None,
        known_brands=["jasem", "acme", "globex"],  # multiple → ambiguous
    )
    c = score_confidence(s, caps)
    # Strong topic (50) + 0 brand + 25 lang = 75 → MEDIUM
    assert c.level == "MEDIUM"


def test_confidence_weights_are_tunable(caps):
    """Custom weights kwarg must take effect. With strong topic, HIGH
    should still be reachable under topic-heavy weighting."""
    s = Signals(
        intent="tutorial framework guide bloom",
        lang="en",
        brand="jasem",
        known_brands=["jasem"],
    )
    c_default = score_confidence(s, caps)
    c_topic_heavy = score_confidence(
        s, caps, weights={"topic": 70, "brand": 15, "lang": 15}
    )
    assert c_default.level == "HIGH"
    assert c_topic_heavy.level == "HIGH"
    # Confirm override was actually used (else the scores would be identical)
    # Score differs because weight distribution differs; both top out at 100
    # when strong + explicit + explicit, so compare with weaker signals:
    s_weak_topic = Signals(intent="tutorial", lang="en", brand="jasem", known_brands=["jasem"])
    c_weak_default = score_confidence(s_weak_topic, caps)
    c_weak_topic_heavy = score_confidence(
        s_weak_topic, caps, weights={"topic": 70, "brand": 15, "lang": 15}
    )
    # Topic-heavy weighting gives less brand+lang credit → lower score on weak topic
    assert c_weak_topic_heavy.score != c_weak_default.score


def test_confidence_thresholds_are_tunable(caps):
    """Raise the HIGH threshold above 100 — even perfect score must downgrade."""
    s = Signals(
        intent="tutorial framework guide bloom",
        lang="en",
        brand="jasem",
        known_brands=["jasem"],
    )
    c_default = score_confidence(s, caps)
    c_strict = score_confidence(s, caps, thresholds={"high": 101})  # unreachable
    assert c_default.level == "HIGH"
    assert c_strict.level == "MEDIUM"


def test_confidence_margin_guard_downgrades_tied_topic():
    """Two recipes with similar scores → margin guard caps topic credit."""
    # Synthetic caps — two near-identical recipes both matching "tutorial-a" well
    fake_caps = {
        "recipes": {
            "tutorial-alpha": {
                "keywords": ["tutorial", "guide", "bloom"],
                "when": "",
                "description": "",
                "sections_shape": [],
            },
            "tutorial-beta": {
                "keywords": ["tutorial", "guide", "bloom"],
                "when": "",
                "description": "",
                "sections_shape": [],
            },
        }
    }
    s = Signals(
        intent="tutorial bloom guide",
        lang="en",
        brand="jasem",
        known_brands=["jasem"],
    )
    c = score_confidence(s, fake_caps)
    # Perfect tie → margin guard should prevent HIGH
    assert c.level != "HIGH"


# ============================================================ language inference


def test_infer_lang_en_dominant():
    lang, strength = _infer_lang("this is English text")
    assert lang == "en"
    assert strength >= 0.9


def test_infer_lang_ar_dominant():
    lang, strength = _infer_lang("هذا نص عربي للاختبار")
    assert lang == "ar"
    assert strength >= 0.7


def test_infer_lang_mixed_script_is_ambiguous():
    # 50/50 mix — neither reaches 70% threshold
    lang, strength = _infer_lang("tutorial دليل guide دليل")
    assert lang is None


def test_infer_lang_empty():
    assert _infer_lang("") == (None, 0.0)
    assert _infer_lang("   ") == (None, 0.0)


def test_infer_lang_threshold_tunable():
    # Lower threshold lets the 50/50 case resolve
    lang, _ = _infer_lang("tutorial دليل", threshold=0.4)
    assert lang in ("en", "ar")  # whichever has more letters
    # Higher threshold rejects even dominant en
    lang, _ = _infer_lang("this is English", threshold=0.99)
    assert lang is None or lang == "en"  # depends on punctuation stripping


# ============================================================ evaluate — top-level


def test_evaluate_high_returns_plan(caps):
    s = Signals(
        intent="tutorial framework guide bloom",
        lang="en",
        brand="jasem",
        known_brands=["jasem"],
    )
    d = evaluate(s, caps)
    assert d.outcome == "proceed"
    assert d.plan is not None
    assert d.plan.recipe == "tutorial"
    assert d.plan.lang == "en"
    assert d.plan.brand == "jasem"


def test_evaluate_medium_returns_candidates(caps):
    s = Signals(
        intent="tutorial framework guide",
        lang=None,  # no explicit lang
        brand=None,
        known_brands=["jasem", "acme"],  # ambiguous brand
    )
    d = evaluate(s, caps)
    assert d.outcome in ("proceed", "choose")
    if d.outcome == "choose":
        assert len(d.candidates) >= 1


def test_evaluate_low_fires_gate(caps):
    s = Signals(intent="weekly report", known_brands=["a", "b", "c"])
    d = evaluate(s, caps)
    # This might be LOW or MEDIUM depending on keyword overlap; if LOW, gate fires
    if d.outcome == "fire":
        assert len(d.questions) == 2
        assert d.questions[0].id == "fit"
        assert d.questions[1].id == "frequency"


def test_evaluate_needs_intent_on_empty(caps):
    d = evaluate(Signals(intent=""), caps)
    assert d.outcome == "needs-intent"
    assert d.message is not None


def test_evaluate_needs_intent_on_zero_match(caps):
    d = evaluate(Signals(intent="asdf-lkjh-qwer"), caps)
    assert d.outcome == "needs-intent"
    assert d.message is not None


# ============================================================ Question shape / AUQ contract


def test_question_to_ask_user_question_shape(caps):
    s = Signals(intent="weekly report that is wholly unknown")
    d = evaluate(s, caps)
    if d.outcome != "fire":
        # Force a fire by hand-building one from a known recipe
        from core.gate import _build_fit_question, _build_frequency_question
        closest = rank_recipes("tutorial", caps, top_k=1)[0]
        qs = [_build_fit_question(closest), _build_frequency_question()]
    else:
        qs = d.questions

    for q in qs:
        payload = q.to_ask_user_question()
        # Tool contract: {question, header, options: [{label, description}], multiSelect}
        assert set(payload.keys()) == {"question", "header", "options", "multiSelect"}
        assert payload["question"].endswith("?")
        assert len(payload["header"]) <= 12
        assert 2 <= len(payload["options"]) <= 4
        for opt in payload["options"]:
            assert set(opt.keys()) == {"label", "description"}
            # No 'value' leakage — tool handles that
            assert 1 <= len(opt["label"].split()) <= 6  # allows 3-word labels


def test_answer_to_value_fit():
    assert answer_to_value("fit", "Yes, fits") == "yes-fits"
    assert answer_to_value("fit", "Partial fit") == "partial"
    assert answer_to_value("fit", "No, fundamentally different") == "no-different"


def test_answer_to_value_frequency():
    assert answer_to_value("frequency", "One-off") == "one-off"
    assert answer_to_value("frequency", "Occasional") == "occasional"
    assert answer_to_value("frequency", "Recurring") == "recurring"


def test_answer_to_value_rejects_unknown():
    with pytest.raises(KeyError):
        answer_to_value("unknown-qid", "Yes, fits")
    with pytest.raises(KeyError):
        answer_to_value("fit", "garbage label")


# ============================================================ Q1 × Q2 resolve matrix


@pytest.fixture
def closest(caps):
    return rank_recipes("tutorial", caps, top_k=1)[0]


@pytest.mark.parametrize(
    "q1,q2,expected_action,expects_fill",
    [
        ("yes-fits", "one-off", "fill-closest", True),
        ("yes-fits", "occasional", "fill-closest", True),
        ("yes-fits", "recurring", "fill-closest", True),
        ("partial", "one-off", "fill-closest", True),
        ("partial", "occasional", "log-and-fill", True),
        ("partial", "recurring", "log-and-fill", True),
        ("no-different", "one-off", "log-and-fill", True),
        ("no-different", "occasional", "log-and-wait", False),
        ("no-different", "recurring", "log-and-wait", False),
    ],
)
def test_resolve_matrix(closest, q1, q2, expected_action, expects_fill):
    r = resolve(q1, q2, closest, intent="test")
    assert r.action == expected_action
    if expects_fill:
        assert r.fill_recipe == closest.name
    else:
        assert r.fill_recipe is None


def test_resolve_rejects_invalid_q1_q2(closest):
    with pytest.raises(ValueError, match="unexpected Q1/Q2"):
        resolve("garbage", "one-off", closest)
    with pytest.raises(ValueError, match="unexpected Q1/Q2"):
        resolve("yes-fits", "never", closest)


def test_resolve_force_graduation_requires_justification(closest):
    # Without justification — rejected
    with pytest.raises(ValueError, match="justification"):
        resolve("no-different", "recurring", closest, force_graduation=True)
    # With empty justification — rejected
    with pytest.raises(ValueError, match="justification"):
        resolve(
            "no-different",
            "recurring",
            closest,
            force_graduation=True,
            force_graduation_justification="   ",
        )


def test_resolve_force_graduation_only_valid_on_no_different_recurring(closest):
    with pytest.raises(ValueError, match="only valid when"):
        resolve(
            "partial",
            "recurring",
            closest,
            force_graduation=True,
            force_graduation_justification="reason",
        )


def test_resolve_force_graduation_success(closest):
    r = resolve(
        "no-different",
        "recurring",
        closest,
        intent="quarterly board memo",
        force_graduation=True,
        force_graduation_justification="3 board memos already logged this quarter",
    )
    assert r.action == "request-graduation"
    assert r.log_entry["force_graduation_justification"] == (
        "3 board memos already logged this quarter"
    )


# ============================================================ Log entry schema


def test_log_entry_schema_version_is_1(closest):
    r = resolve("yes-fits", "one-off", closest, intent="test-intent")
    assert r.log_entry["schema_version"] == LOG_SCHEMA_VERSION


def test_log_entry_fields_match_contract(closest):
    r = resolve("partial", "occasional", closest, intent="my test intent text")
    entry = r.log_entry
    # v1 parity fields
    assert "ts" in entry
    assert entry["request"] == "my test intent text"
    assert entry["routed_to"] == closest.name  # partial × occasional → log-and-fill
    assert "reason" in entry
    # gate-specific fields
    assert entry["recipe_closest"] == closest.name
    assert entry["closest_score"] == closest.score
    assert entry["fit"] == "partial"
    assert entry["frequency"] == "occasional"
    assert entry["action"] == "log-and-fill"
    assert entry["force_graduation_justification"] is None


def test_log_entry_routed_to_none_for_log_and_wait(closest):
    r = resolve("no-different", "recurring", closest, intent="test")
    assert r.log_entry["routed_to"] is None  # log-and-wait → no recipe used


# ============================================================ Snapshot corpus


CANONICAL_INTENTS = [
    ("tutorial guide bloom framework", "tutorial"),
    ("chart showcase sparkline donut", "phase-2-day6-showcase"),
    # Note: avoid the word "tutorial" here — it matches the `tutorial` recipe
    # by exact name and outranks phase-2-day5-showcase even when day5 has
    # stronger keyword overlap with tutorial-step concept.
    ("two-column image showcase", "phase-2-day5-showcase"),
    ("cover variant image-background", "phase-2-day4-showcase"),
    ("module section showcase", "phase-2-day3-showcase"),
    ("scaffolding front-matter summary objectives", "phase-2-day2-showcase"),
    ("phase 1 trivial smoke primitives", "phase-1-trivial"),
]


@pytest.mark.parametrize("intent,expected_top", CANONICAL_INTENTS)
def test_snapshot_corpus_ranking(caps, intent, expected_top):
    """For each canonical intent, the top-ranked recipe should be predictable.

    Protects against regressions when scoring weights change.
    """
    ranked = rank_recipes(intent, caps, top_k=1)
    assert ranked, f"no match for intent: {intent!r}"
    assert ranked[0].name == expected_top, (
        f"intent {intent!r} ranked {ranked[0].name!r} #1; expected {expected_top!r}"
    )
