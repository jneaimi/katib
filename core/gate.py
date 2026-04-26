"""Decision gate — self-contained 3-question flow for LOW-confidence routing.

Fires only when the capability match is low-confidence (ADR §Built-in
decision gate). Produces structured Question payloads matching Claude
Code's `AskUserQuestion` tool contract; consumes answers and computes a
sanctioned action via the Q1 × Q2 matrix.

No Claude-Code coupling beyond the Question shape: the gate is pure
Python, testable with dict inputs. Runner (Day 10 slash command) calls
`question.to_ask_user_question()` to produce the exact payload.

-----------------------------------------------------------------------
Public API

    score_confidence(signals, caps, *, weights=None, thresholds=None,
                     inference_threshold=0.7) -> Confidence
    evaluate(signals, caps) -> GateDecision
    resolve(q1, q2, closest, *, intent="", force_graduation=False,
            force_graduation_justification=None) -> GateResolution
    answer_to_value(question_id, answer_label) -> str

-----------------------------------------------------------------------
Q1 × Q2 action matrix (ADR-sanctioned paths; no path bypasses the log)

                  one-off      occasional   recurring
    yes-fits      fill-closest fill-closest fill-closest
    partial       fill-closest log-and-fill log-and-fill
    no-different  log-and-fill log-and-wait log-and-wait*

    (*) With force_graduation=True + justification, `no-different ×
        recurring` escalates to `request-graduation`.

-----------------------------------------------------------------------
Log-entry schema (schema_version: 1) — written by
`core.request_log.log_gate_decision` and `log_recipe_request`. Matches v1's
minimal `{ts, request, routed_to, reason}` shape for continuity, extended
with gate-specific fields.

    {
        schema_version: 1,
        ts: ISO8601,
        request: str,          # full intent text (reflect uses for clustering)
        routed_to: str | None, # fill_recipe if any
        reason: str,           # human-readable summary
        recipe_closest: str | None,
        closest_score: float | None,
        fit: "yes-fits" | "partial" | "no-different",
        frequency: "one-off" | "occasional" | "recurring",
        action: "fill-closest" | "log-and-fill" | "log-and-wait" | "request-graduation",
        force_graduation_justification: str | None,
    }
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from core.capabilities import RecipeMatch, rank_recipes

ConfidenceLevel = Literal["HIGH", "MEDIUM", "LOW"]
Outcome = Literal["proceed", "choose", "fire", "needs-intent"]
Action = Literal["fill-closest", "log-and-fill", "log-and-wait", "request-graduation"]

# ----- default thresholds + weights (all overridable per call)
DEFAULT_THRESHOLDS = {"high": 90, "medium": 50}
DEFAULT_WEIGHTS = {"topic": 50, "brand": 25, "lang": 25}
DEFAULT_TOPIC_STRONG = 0.7       # top-recipe score above which topic is "strong"
DEFAULT_TOPIC_MODERATE = 0.4     # above this, "moderate"
DEFAULT_HIGH_MARGIN = 1.3        # top score must beat second by ≥ this × to allow HIGH
LOG_SCHEMA_VERSION = 1

_AR_CHAR_RE = re.compile(r"[؀-ۿ]")


@dataclass
class Signals:
    intent: str
    lang: str | None = None
    brand: str | None = None
    known_brands: list[str] = field(default_factory=list)


@dataclass
class Confidence:
    level: ConfidenceLevel
    score: int
    reasons: list[str] = field(default_factory=list)


@dataclass
class QuestionOption:
    """Matches Claude Code AskUserQuestion option shape (label + description).

    The internal routing `value` is derived from the label via
    `answer_to_value()` — AskUserQuestion itself returns the selected
    label, so we don't embed value here.
    """

    label: str
    description: str


@dataclass
class Question:
    """Matches AskUserQuestion question shape. `id` is internal-only
    (for answer→value mapping); the tool uses `question` as the key."""

    id: str
    header: str              # ≤12 chars (tool constraint)
    question: str            # full prompt, ends with ?
    options: list[QuestionOption]
    multiSelect: bool = False

    def to_ask_user_question(self) -> dict:
        """Emit the exact dict shape `AskUserQuestion` expects."""
        return {
            "question": self.question,
            "header": self.header,
            "options": [
                {"label": o.label, "description": o.description} for o in self.options
            ],
            "multiSelect": self.multiSelect,
        }


@dataclass
class ResolvedPlan:
    recipe: str
    lang: str
    brand: str | None
    slug: str | None = None


@dataclass
class GateDecision:
    outcome: Outcome
    confidence: Confidence
    closest: RecipeMatch | None = None
    candidates: list[RecipeMatch] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    plan: ResolvedPlan | None = None
    message: str | None = None   # only set when outcome="needs-intent"


@dataclass
class GateResolution:
    action: Action
    fill_recipe: str | None
    log_entry: dict
    reasons: list[str] = field(default_factory=list)


# -------------------- answer-label → internal-value mapping --------------------

_FIT_LABEL_TO_VALUE = {
    "Yes, fits": "yes-fits",
    "Partial fit": "partial",
    "No, fundamentally different": "no-different",
}
_FREQUENCY_LABEL_TO_VALUE = {
    "One-off": "one-off",
    "Occasional": "occasional",
    "Recurring": "recurring",
}

_LABEL_MAPS = {"fit": _FIT_LABEL_TO_VALUE, "frequency": _FREQUENCY_LABEL_TO_VALUE}


def answer_to_value(question_id: str, answer_label: str) -> str:
    """Map an AskUserQuestion answer-label back to the internal routing value."""
    if question_id not in _LABEL_MAPS:
        raise KeyError(f"unknown question id {question_id!r}")
    mapping = _LABEL_MAPS[question_id]
    if answer_label not in mapping:
        raise KeyError(
            f"answer {answer_label!r} not recognized for question {question_id!r}; "
            f"expected one of {list(mapping)}"
        )
    return mapping[answer_label]


# ---------------------------------------------------------------- scoring


def infer_script(text: str, threshold: float = 0.7) -> tuple[str | None, float]:
    """Return (lang, strength 0-1). Strength = fraction of script-dominant letters.

    Public helper — context_sensor imports this directly. `_infer_lang` kept
    as a private alias for backward-compat within gate.py.
    """
    if not text:
        return None, 0.0
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return None, 0.0
    ar_count = sum(1 for c in letters if _AR_CHAR_RE.match(c))
    ar_ratio = ar_count / len(letters)
    en_ratio = 1.0 - ar_ratio
    if ar_ratio >= threshold:
        return "ar", ar_ratio
    if en_ratio >= threshold:
        return "en", en_ratio
    return None, max(ar_ratio, en_ratio)


# Private alias for callers inside this module (kept to avoid churn).
_infer_lang = infer_script


def score_confidence(
    signals: Signals,
    caps: dict,
    *,
    weights: dict | None = None,
    thresholds: dict | None = None,
    inference_threshold: float = 0.7,
    topic_strong: float = DEFAULT_TOPIC_STRONG,
    topic_moderate: float = DEFAULT_TOPIC_MODERATE,
    high_margin: float = DEFAULT_HIGH_MARGIN,
) -> Confidence:
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    reasons: list[str] = []
    score = 0

    # ---- topic (up to w["topic"])
    top = rank_recipes(signals.intent, caps, top_k=2)
    topic_score_earned = 0
    if top:
        best = top[0]
        second_score = top[1].score if len(top) > 1 else 0.0
        margin_ok = (second_score == 0) or (best.score >= second_score * high_margin)
        if best.score >= topic_strong:
            topic_score_earned = w["topic"]
            reasons.append(f"topic: strong match to {best.name!r} ({best.score:.2f})")
        elif best.score >= topic_moderate:
            topic_score_earned = w["topic"] // 2
            reasons.append(f"topic: moderate match to {best.name!r} ({best.score:.2f})")
        else:
            topic_score_earned = max(1, int(w["topic"] * best.score))
            reasons.append(f"topic: weak match to {best.name!r} ({best.score:.2f})")
        # Margin guard: if #1 doesn't beat #2 by the margin, cap topic credit
        # at moderate — this prevents tied-rank cases from triggering HIGH.
        if not margin_ok:
            capped = w["topic"] // 2
            if topic_score_earned > capped:
                reasons.append(
                    f"topic: margin guard — #1 ({best.score:.2f}) vs "
                    f"#2 ({second_score:.2f}) < {high_margin}× — capped at moderate"
                )
                topic_score_earned = capped
    else:
        reasons.append("topic: no recipe match")
    score += topic_score_earned

    # ---- brand (up to w["brand"])
    if signals.brand:
        score += w["brand"]
        reasons.append(f"brand: explicit ({signals.brand!r})")
    elif len(signals.known_brands) == 1:
        score += w["brand"]
        reasons.append(
            f"brand: inferred ({signals.known_brands[0]!r}, only one registered)"
        )
    elif not signals.known_brands:
        score += w["brand"]
        reasons.append("brand: default (no brands registered)")
    else:
        reasons.append(
            f"brand: ambiguous ({len(signals.known_brands)} registered, none chosen)"
        )

    # ---- language (up to w["lang"]) — strong inference only (no partial credit)
    if signals.lang:
        score += w["lang"]
        reasons.append(f"lang: explicit ({signals.lang!r})")
    else:
        inferred, strength = _infer_lang(signals.intent, threshold=inference_threshold)
        if inferred:
            score += w["lang"]
            reasons.append(f"lang: inferred {inferred!r} ({strength:.0%} script match)")
        else:
            reasons.append(
                f"lang: ambiguous (no script reaches {inference_threshold:.0%})"
            )

    score = max(0, min(100, score))

    # Belt-and-suspenders: HIGH also requires that topic earned strong credit,
    # not just that the arithmetic crossed 90. Protects against future weight
    # tweaks accidentally letting HIGH fire on weak topic + strong brand+lang.
    if score >= t["high"] and topic_score_earned >= w["topic"]:
        level: ConfidenceLevel = "HIGH"
    elif score >= t["medium"]:
        level = "MEDIUM"
        if score >= t["high"]:
            reasons.append("downgrade: score≥HIGH but topic credit insufficient")
    else:
        level = "LOW"

    return Confidence(level=level, score=score, reasons=reasons)


# ---------------------------------------------------------------- evaluate


def _build_fit_question(closest: RecipeMatch) -> Question:
    data = closest.data or {}
    target_pages = data.get("target_pages")
    pages_str = (
        f"{target_pages[0]}–{target_pages[1]}pp"
        if isinstance(target_pages, list) and len(target_pages) == 2
        else "variable length"
    )
    sections_shape = data.get("sections_shape") or []
    shape_str = (
        ", ".join(sections_shape[:3]) + ("..." if len(sections_shape) > 3 else "")
        if sections_shape
        else "flexible"
    )
    return Question(
        id="fit",
        header="Recipe fit",
        question=(
            f"The closest existing recipe is `{closest.name}` "
            f"({shape_str}, {pages_str}). Does your document fit that shape?"
        ),
        options=[
            QuestionOption(
                label="Yes, fits",
                description=f"Use `{closest.name}` as-is with my content.",
            ),
            QuestionOption(
                label="Partial fit",
                description="Close, but some sections don't match what I need.",
            ),
            QuestionOption(
                label="No, fundamentally different",
                description="This is a different kind of document.",
            ),
        ],
    )


def _build_frequency_question() -> Question:
    return Question(
        id="frequency",
        header="Frequency",
        question="Do you expect to produce documents like this again?",
        options=[
            QuestionOption(
                label="One-off",
                description="Just this one; no expected repeat.",
            ),
            QuestionOption(
                label="Occasional",
                description="Maybe one or two more like this.",
            ),
            QuestionOption(
                label="Recurring",
                description="Three or more expected — worth graduating a pattern.",
            ),
        ],
    )


def evaluate(signals: Signals, caps: dict) -> GateDecision:
    confidence = score_confidence(signals, caps)
    candidates = rank_recipes(signals.intent, caps, top_k=3)
    closest = candidates[0] if candidates else None

    # Degenerate case: no intent → can't help even with a gate
    if not signals.intent.strip():
        return GateDecision(
            outcome="needs-intent",
            confidence=confidence,
            message=(
                "No intent provided. Supply a document description "
                "(e.g., \"tutorial about onboarding\") before calling the gate."
            ),
        )

    # No recipe match at all — the 3-question gate can't ask about closest
    if closest is None:
        return GateDecision(
            outcome="needs-intent",
            confidence=confidence,
            message=(
                "No recipes matched the intent. Either (a) refine the intent "
                "with terms closer to existing recipes, or (b) log a new "
                "recipe request via log_recipe_request."
            ),
        )

    if confidence.level == "HIGH":
        plan = ResolvedPlan(
            recipe=closest.name,
            lang=signals.lang or _infer_lang(signals.intent)[0] or "en",
            brand=signals.brand
            or (signals.known_brands[0] if len(signals.known_brands) == 1 else None),
        )
        return GateDecision(
            outcome="proceed",
            confidence=confidence,
            closest=closest,
            candidates=candidates,
            plan=plan,
        )

    if confidence.level == "MEDIUM":
        return GateDecision(
            outcome="choose",
            confidence=confidence,
            closest=closest,
            candidates=candidates,
        )

    # LOW — fire the gate
    return GateDecision(
        outcome="fire",
        confidence=confidence,
        closest=closest,
        candidates=candidates,
        questions=[_build_fit_question(closest), _build_frequency_question()],
    )


# ---------------------------------------------------------------- resolve


_ACTION_MATRIX: dict[tuple[str, str], Action] = {
    ("yes-fits", "one-off"): "fill-closest",
    ("yes-fits", "occasional"): "fill-closest",
    ("yes-fits", "recurring"): "fill-closest",
    ("partial", "one-off"): "fill-closest",
    ("partial", "occasional"): "log-and-fill",
    ("partial", "recurring"): "log-and-fill",
    ("no-different", "one-off"): "log-and-fill",
    ("no-different", "occasional"): "log-and-wait",
    ("no-different", "recurring"): "log-and-wait",
}


def resolve(
    q1: str,
    q2: str,
    closest: RecipeMatch | None,
    *,
    intent: str = "",
    force_graduation: bool = False,
    force_graduation_justification: str | None = None,
) -> GateResolution:
    key = (q1, q2)
    if key not in _ACTION_MATRIX:
        raise ValueError(
            f"gate.resolve: unexpected Q1/Q2 combination {key!r}. "
            f"Valid Q1: yes-fits, partial, no-different. "
            f"Valid Q2: one-off, occasional, recurring."
        )
    action: Action = _ACTION_MATRIX[key]
    reasons: list[str] = [f"Q1={q1} × Q2={q2} → {action}"]

    if force_graduation:
        if key != ("no-different", "recurring"):
            raise ValueError(
                "force_graduation=True is only valid when Q1=no-different and "
                "Q2=recurring. Otherwise the matrix already routes to a "
                "sanctioned path."
            )
        if not force_graduation_justification or not force_graduation_justification.strip():
            raise ValueError(
                "force_graduation=True requires a non-empty "
                "force_graduation_justification string (ADR: 'requires justification')."
            )
        action = "request-graduation"
        reasons.append(
            f"force_graduation=True: {force_graduation_justification.strip()!r}"
        )

    fill_recipe = (
        closest.name
        if closest and action in ("fill-closest", "log-and-fill")
        else None
    )

    log_entry: dict = {
        "schema_version": LOG_SCHEMA_VERSION,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stage": "resolve",
        "request": intent,
        "routed_to": fill_recipe,
        "reason": reasons[0] + (f" + {reasons[1]}" if len(reasons) > 1 else ""),
        "recipe_closest": closest.name if closest else None,
        "closest_score": closest.score if closest else None,
        "fit": q1,
        "frequency": q2,
        "action": action,
        "force_graduation_justification": (
            force_graduation_justification.strip()
            if force_graduation and force_graduation_justification
            else None
        ),
    }

    return GateResolution(
        action=action,
        fill_recipe=fill_recipe,
        log_entry=log_entry,
        reasons=reasons,
    )


# ---------------------------------------------------------------- evaluation log

def build_evaluation_log_entry(
    *,
    intent: str,
    action: str,
    decision: GateDecision | None = None,
    recipe: str | None = None,
    lang: str | None = None,
    brand: str | None = None,
    reasons: list[str] | None = None,
) -> dict:
    """Build a gate-decisions log entry for the infer stage.

    Mirrors the resolve-stage entry shape so both stages live in the same
    `gate-decisions.jsonl` distinguished by the `stage` field. `action`
    matches the JSON action emitted by route.py infer:
    'render' | 'present_candidates' | 'ask_questions' | 'ask_intent' |
    'explicit-recipe' | 'error'.

    `decision` is optional — the explicit-recipe path short-circuits the
    gate so no GateDecision exists; we still log the routing outcome.
    """
    confidence_level: str | None = None
    confidence_score: int | None = None
    closest: str | None = None
    candidates: list[str] = []
    if decision is not None:
        confidence_level = decision.confidence.level
        confidence_score = decision.confidence.score
        if decision.closest is not None:
            closest = decision.closest.name
        if decision.candidates:
            candidates = [c.name for c in decision.candidates]

    return {
        "schema_version": LOG_SCHEMA_VERSION,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stage": "evaluate",
        "request": intent,
        "action": action,
        "recipe": recipe,
        "lang": lang,
        "brand": brand,
        "confidence_level": confidence_level,
        "confidence_score": confidence_score,
        "closest": closest,
        "candidates": candidates,
        "reasons": list(reasons or []),
    }
