"""Session-context reader — extracts Signals from a transcript + filesystem state.

Feeds upstream into `gate.evaluate(signals, caps)`. Pure Python, deterministic,
no LLM. Callers (Day 10's /katib runner; ad-hoc tests; integrations) pass in
a plain-text transcript string; sensor returns a `ContextInference` with
signals + a human-readable summary + a log-entry draft consumed by
`core.request_log.log_context_inference` which persists it to
`memory/context-inferences.jsonl`.

Scope (Day 9):
    - intent (topic)   — last-N-chars of transcript; role-prefix stripped
    - brand            — word-boundary match against enumerated brands, with
                         indicator-verb or quoting guard to avoid false matches
    - lang (explicit)  — marker phrases: "in Arabic"/"in English"/Arabic variants
    - lang (inferred)  — falls through to gate.infer_script() script dominance
    - known_brands     — enumerated from ~/.katib/brands/ + repo brands/

Out of scope (by design, documented for future phases):
    - format hints ("one-pager", "short", "long")
    - audience signals ("for board", "for client")
    These would require extending gate.Signals, which is deferred until a
    concrete use case lands.

Privacy: the log_entry only captures a transcript SAMPLE (first 200 + last
200 chars, middle redacted) — not the full text. Full intent text stays in
the in-memory Signals object.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from core.gate import Signals, infer_script

LOG_SCHEMA_VERSION = 1
DEFAULT_MAX_CHARS = 4000
SAMPLE_EDGE = 200            # chars at each end in transcript_sample

# Brand-directory conventions — mirrors core/tokens.py
_USER_BRANDS_DIR_ENV = "KATIB_BRANDS_DIR"
_DEFAULT_USER_BRANDS_DIR = Path.home() / ".katib" / "brands"
_REPO_BRANDS_DIR = Path(__file__).resolve().parent.parent / "brands"

# Indicator words that, when appearing within ±3 words of a brand candidate,
# lift a substring match to a confident brand signal.
_BRAND_INDICATORS = frozenset(
    {
        "brand", "with", "using", "use", "apply", "for", "in",
        "as", "the",
    }
)

# Explicit-language markers — first match wins.
# Each entry: (regex pattern, lang code)
_LANG_MARKER_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bin\s+arabic\b", re.IGNORECASE), "ar"),
    (re.compile(r"\bin\s+english\b", re.IGNORECASE), "en"),
    (re.compile(r"\bar(?:abic)?\s+only\b", re.IGNORECASE), "ar"),
    (re.compile(r"\ben(?:glish)?\s+only\b", re.IGNORECASE), "en"),
    # Arabic-language markers
    (re.compile(r"باللغة\s+العربية"), "ar"),
    (re.compile(r"بالعربية"), "ar"),
    (re.compile(r"بالإنجليزية"), "en"),
    (re.compile(r"بالإنكليزية"), "en"),
]

_ROLE_PREFIX_RE = re.compile(
    r"^\s*(user|assistant|system|human|ai)\s*[:>]\s*",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class ContextInference:
    signals: Signals
    summary: str                           # ≤ 2 sentences, for runner to show user
    reasons: list[str] = field(default_factory=list)
    transcript_sample: str = ""            # first 200 + "..." + last 200 chars
    log_entry: dict = field(default_factory=dict)


# ---------------------------------------------------------------- brand dir


def _user_brands_dir() -> Path:
    env = os.environ.get(_USER_BRANDS_DIR_ENV)
    return Path(env).expanduser() if env else _DEFAULT_USER_BRANDS_DIR


def enumerate_brands(
    user_dir: Path | None = None,
    repo_dir: Path | None = None,
) -> list[str]:
    """List brand names (filename stems) from user + repo brand directories."""
    dirs = [
        user_dir if user_dir is not None else _user_brands_dir(),
        repo_dir if repo_dir is not None else _REPO_BRANDS_DIR,
    ]
    seen: set[str] = set()
    out: list[str] = []
    for d in dirs:
        if not d.exists() or not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if p.suffix.lower() not in (".yaml", ".yml"):
                continue
            name = p.stem
            if name in seen:
                continue
            seen.add(name)
            out.append(name)
    return sorted(out)


# ---------------------------------------------------------------- message join


def from_messages(messages: list[dict]) -> str:
    """Join a list of {role, content} dicts into a transcript string.

    Only the most recent 10 messages are retained — older content is
    rarely routing-relevant and risks diluting intent extraction.
    """
    recent = messages[-10:] if len(messages) > 10 else messages
    lines: list[str] = []
    for m in recent:
        role = (m.get("role") or "").strip()
        content = (m.get("content") or "").strip()
        if not content:
            continue
        if role:
            lines.append(f"{role}: {content}")
        else:
            lines.append(content)
    return "\n\n".join(lines)


# ---------------------------------------------------------------- extractors


def extract_intent(transcript: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """Return the last `max_chars` of transcript, role prefixes stripped."""
    if not transcript:
        return ""
    text = transcript[-max_chars:] if len(transcript) > max_chars else transcript
    text = _ROLE_PREFIX_RE.sub("", text)
    return text.strip()


def extract_brand(
    transcript: str, known_brands: list[str]
) -> tuple[str | None, str]:
    """Return (brand_name | None, reason). Requires word-boundary match AND
    an indicator word within ±3 tokens, OR match inside quotes/backticks.
    Returns the most-recently-mentioned brand when multiple match."""
    if not transcript or not known_brands:
        return None, "no brands registered" if not known_brands else "empty transcript"

    text = transcript
    # Tokenize for proximity analysis
    tokens = re.findall(r"\S+", text)
    lowered = [t.lower().strip(".,;:!?\"'()[]{}") for t in tokens]

    candidates: list[tuple[int, str, str]] = []   # (position, brand, reason)
    for brand in known_brands:
        brand_lower = brand.lower()
        pattern = re.compile(rf"\b{re.escape(brand_lower)}\b", re.IGNORECASE)
        for m in pattern.finditer(text):
            pos = m.start()
            # Check for quoting/backtick context
            left = text[max(0, pos - 1):pos]
            right_end = pos + len(brand)
            right = text[right_end:right_end + 1]
            quoted = (left in "\"'`") and (right in "\"'`")

            # Find token index this match lives in
            running = 0
            tok_idx = -1
            for i, t in enumerate(tokens):
                nxt = text.find(t, running)
                if nxt == -1:
                    continue
                if nxt <= pos < nxt + len(t):
                    tok_idx = i
                    break
                running = nxt + len(t)

            # Proximity check for indicator words within ±3 tokens
            near_indicator = False
            if tok_idx >= 0:
                window_start = max(0, tok_idx - 3)
                window_end = min(len(lowered), tok_idx + 4)
                for i in range(window_start, window_end):
                    if i == tok_idx:
                        continue
                    if lowered[i] in _BRAND_INDICATORS:
                        near_indicator = True
                        break

            if quoted or near_indicator:
                reason = (
                    f"brand {brand!r} at pos {pos} "
                    f"({'quoted' if quoted else 'near indicator word'})"
                )
                candidates.append((pos, brand, reason))

    if not candidates:
        return None, f"no confident brand match among {known_brands!r}"

    # Most recent mention wins
    candidates.sort(key=lambda x: x[0])
    pos, brand, reason = candidates[-1]
    if len(candidates) > 1:
        reason += (
            f" (winner over {len(candidates) - 1} earlier candidate"
            f"{'s' if len(candidates) > 2 else ''})"
        )
    return brand, reason


def extract_lang_marker(transcript: str) -> tuple[str | None, str]:
    """Detect explicit language markers (e.g., 'in Arabic', 'باللغة العربية')."""
    if not transcript:
        return None, "empty transcript"
    # Prefer the last marker found (most recent user intent)
    matches: list[tuple[int, str, str]] = []
    for pat, lang in _LANG_MARKER_PATTERNS:
        for m in pat.finditer(transcript):
            matches.append((m.start(), lang, m.group(0)))
    if not matches:
        return None, "no explicit language marker"
    matches.sort(key=lambda x: x[0])
    _, lang, match_text = matches[-1]
    return lang, f"explicit marker {match_text!r}"


# ---------------------------------------------------------------- sample + summary


def _transcript_sample(transcript: str, edge: int = SAMPLE_EDGE) -> str:
    if not transcript:
        return ""
    if len(transcript) <= edge * 2 + 5:
        return transcript
    head = transcript[:edge]
    tail = transcript[-edge:]
    return f"{head}...{tail}"


def _summarize(signals: Signals, lang_source: str | None) -> str:
    """Return a ≤2-sentence human-readable summary of inferred signals.

    Uses `;` as internal joiner (not `.`) so the result is one sentence
    — easier for the runner to compose with surrounding text and clearer
    for observability.
    """
    intent_preview = (
        signals.intent[:60] + "..."
        if len(signals.intent) > 60
        else signals.intent
    )
    topic = f"topic {intent_preview!r}" if intent_preview else "no intent extracted"

    if signals.brand:
        brand_phrase = f"brand {signals.brand}"
    elif signals.known_brands:
        brand_phrase = f"brand unspecified ({len(signals.known_brands)} registered)"
    else:
        brand_phrase = "default brand"

    if signals.lang:
        lang_phrase = f"lang {signals.lang}"
        if lang_source:
            lang_phrase += f" via {lang_source}"
    else:
        lang_phrase = "lang ambiguous"

    return f"Inferred: {topic}; {brand_phrase}; {lang_phrase}."


# ---------------------------------------------------------------- public API


def infer_signals(
    transcript: str,
    *,
    known_brands: list[str] | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> ContextInference:
    """Extract routing signals from a transcript + filesystem brand state."""
    reasons: list[str] = []

    if known_brands is None:
        known_brands = enumerate_brands()
        reasons.append(f"known_brands enumerated from disk: {known_brands!r}")
    else:
        reasons.append(f"known_brands passed in: {known_brands!r}")

    intent = extract_intent(transcript, max_chars=max_chars)
    if intent:
        reasons.append(f"intent extracted ({len(intent)} chars)")
    else:
        reasons.append("intent empty")

    brand, brand_reason = extract_brand(transcript, known_brands)
    reasons.append(f"brand extraction: {brand_reason}")

    # Language: explicit marker wins over script inference
    marker_lang, marker_reason = extract_lang_marker(transcript)
    lang_source: str | None = None
    if marker_lang:
        lang: str | None = marker_lang
        lang_source = "explicit"
        reasons.append(f"lang from marker: {marker_reason}")
        # Log conflict if script inference disagrees
        inferred, strength = infer_script(intent)
        if inferred and inferred != marker_lang:
            reasons.append(
                f"lang conflict: marker={marker_lang} but script inference="
                f"{inferred} at {strength:.0%} — marker wins"
            )
    else:
        inferred, strength = infer_script(intent)
        if inferred:
            lang = inferred
            lang_source = "inferred"
            reasons.append(f"lang inferred from script: {inferred} ({strength:.0%})")
        else:
            lang = None
            reasons.append("lang ambiguous: no marker + no script dominance")

    signals = Signals(
        intent=intent,
        lang=lang,
        brand=brand,
        known_brands=list(known_brands),
    )

    sample = _transcript_sample(transcript)
    summary = _summarize(signals, lang_source)

    log_entry = {
        "schema_version": LOG_SCHEMA_VERSION,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transcript_sample": sample,
        "transcript_length": len(transcript),
        "inferred": {
            "intent_preview": intent[:120],
            "brand": brand,
            "lang": lang,
            "lang_source": lang_source,
        },
        "known_brands": list(known_brands),
    }

    return ContextInference(
        signals=signals,
        summary=summary,
        reasons=reasons,
        transcript_sample=sample,
        log_entry=log_entry,
    )
