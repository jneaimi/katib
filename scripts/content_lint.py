#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Content lint — static catch for mechanical anti-slop violations.

Not a replacement for the 5-dimension anti-slop score in writing.{lang}.md
(that requires human judgement). This script catches the mechanical ones:
banned openers, emphasis crutches, jargon inflation, untranslated English
abbreviations, unqualified ambiguous tech terms, and واو-chain runaways.

Usage:
    python3 scripts/content_lint.py <file>              # lint a file (HTML or MD)
    python3 scripts/content_lint.py <file> --lang ar    # force Arabic ruleset
    python3 scripts/content_lint.py <file> --lang en    # force English ruleset
    python3 scripts/content_lint.py <file> --json       # machine-readable
    python3 scripts/content_lint.py --stdin --lang ar   # read from stdin

Exit:
  0 — clean
  1 — violations found
  2 — bad input (file missing, unknown language, etc.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ===================== Arabic rules =====================

# §1 Throat-clearing openers — match at start of sentence or paragraph
AR_BANNED_OPENERS = [
    "في عالمنا اليوم",
    "في ظل التطورات المتسارعة",
    "في ظل التحولات المتسارعة",
    "لا يخفى على أحد أن",
    "مما لا شك فيه أن",
    "من الجدير بالذكر أن",
    "تجدر الإشارة إلى أن",
    "كما هو معروف",
    "من المعلوم أن",
    "لا بد من الإشارة إلى",
    "بطبيعة الحال",
    "في واقع الأمر",
    "دعونا نتفق أن",
    "ليس من المبالغة القول",
    "نعيش في زمن",
]

# §2 Emphasis crutches
AR_EMPHASIS_CRUTCHES = [
    "وهذا ما يجعل الأمر بالغ الأهمية",
    "وهنا تكمن المفارقة",
    "وهذا ليس مبالغة",
    "النقطة الجوهرية هنا",
    "الأمر الأكثر إثارة هو",
    "وهذا بالضبط ما نحتاجه",
    "الحقيقة المُرّة هي",
    "وهذا يعني شيئاً واحداً",
]

# §3 Jargon inflation (compact set — full catalog in writing.ar.md)
AR_JARGON = [
    "تحقيق التحول الرقمي الشامل",
    "تعزيز منظومة الابتكار",
    "الاستفادة من البيانات الضخمة",
    "بناء قدرات مستدامة",
    "إطلاق العنان لـ",
    "تسخير قوة",
    "تحقيق قفزة نوعية",
]

# §7 Vague declaratives
AR_VAGUE_DECLARATIVES = [
    "النتائج مذهلة",
    "الفرص لا حصر لها",
    "المستقبل واعد",
    "الإمكانيات هائلة",
    "العالم يتغير بسرعة",
    "هذا يغير كل شيء",
]

# §6 Hand-holding + meta
AR_META_COMMENTARY = [
    "في هذا المقال سنتناول",
    "كما سنرى لاحقاً",
    "دعونا نلخّص",
    "كما ذكرنا سابقاً",
    "دعونا نستعرض",
    "من المهم أن نفهم أن",
    "يجب أن نتذكر أن",
]

# Ambiguous tech terms that must be qualified (§2 in core rules).
# The regex looks for the bare form surrounded by word boundaries.
# Qualified forms (e.g. "الوكيل الذكي") don't match because they have extra words after.
# This is the MVP pass — it flags for human review, not auto-rejection.
AR_AMBIGUOUS_TECH_TERMS = {
    "الوكيل": "qualify with الذكي or pair with 'الذكاء الاصطناعي' for clarity",
    "وكيل": "qualify with الذكي",
    "الوكلاء": "qualify with الأذكياء",
    "وكلاء": "qualify with الأذكياء",
}

# Common English abbreviations that must be translated on first mention.
# The check: find the abbreviation; require that within the SAME sentence
# a preceding Arabic gloss exists (heuristic: look for "(abbrev)" pattern
# after an Arabic word run).
EN_ABBREVIATIONS_REQUIRING_TRANSLATION = [
    "MCP", "API", "SDK", "B2B", "B2C", "CEO", "CTO", "CFO", "CIO",
    "DevSecOps", "DevOps", "CI/CD", "MFA", "2FA", "SSO", "OAuth",
    "PDPL", "GDPR", "HIPAA", "SOC 2", "TCO", "MAU", "DAU",
    "KPI", "NOC", "SLA", "RFP", "ROI", "AI", "ML", "LLM",
]


# ===================== English rules =====================

EN_BANNED_OPENERS = [
    r"In today'?s world",
    r"In today'?s rapidly[- ]evolving",
    r"In an era of",
    r"It'?s no secret that",
    r"There'?s no doubt that",
    r"It'?s worth mentioning that",
    r"It should be noted that",
    r"In this context",
    r"It goes without saying",
    r"Needless to say",
]

EN_EMPHASIS_CRUTCHES = [
    r"And here lies the paradox",
    r"Let me be clear",
    r"The key point here is",
    r"What'?s most exciting is",
    r"And this is exactly what we need",
    r"The harsh truth is",
]

EN_VAGUE_DECLARATIVES = [
    r"The results are amazing",
    r"The possibilities are endless",
    r"The future is bright",
    r"The impact is huge",
    r"This changes everything",
]

EN_META_COMMENTARY = [
    r"In this article we will",
    r"As we will see later",
    r"Let'?s summarize",
    r"As mentioned earlier",
    r"It is important to understand that",
    r"We must remember that",
]


# ===================== Core linter =====================

@dataclass
class Violation:
    rule: str
    severity: str  # "error" | "warn"
    pattern: str
    line: int
    snippet: str


def _extract_text(raw: str) -> str:
    """Strip HTML tags and Jinja templates so we lint prose, not markup.

    - Removes <tag>...</tag> and <tag/> forms
    - Removes {{ ... }} and {% ... %}
    - Collapses multiple whitespace to single spaces (but preserves newlines
      for line-number reporting)
    """
    # Remove Jinja constructs
    text = re.sub(r"\{\{.*?\}\}", " ", raw, flags=re.DOTALL)
    text = re.sub(r"\{%.*?%\}", " ", text, flags=re.DOTALL)
    # Remove <style>...</style> and <script>...</script> blocks wholesale
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining HTML tags (keep inner content)
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode common HTML entities
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&mdash;", "—")
    return text


def _find_literal(text: str, needle: str) -> list[tuple[int, str]]:
    """Return (line_number, snippet) tuples for every occurrence of `needle`."""
    hits = []
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if needle in line:
            hits.append((i, line.strip()[:120]))
    return hits


def _find_regex(text: str, pattern: str) -> list[tuple[int, str]]:
    """Return (line_number, snippet) for every regex match."""
    hits = []
    regex = re.compile(pattern, re.IGNORECASE)
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if regex.search(line):
            hits.append((i, line.strip()[:120]))
    return hits


def lint_arabic(text: str) -> list[Violation]:
    v: list[Violation] = []

    for opener in AR_BANNED_OPENERS:
        for line, snip in _find_literal(text, opener):
            v.append(Violation("banned-opener", "error", opener, line, snip))

    for crutch in AR_EMPHASIS_CRUTCHES:
        for line, snip in _find_literal(text, crutch):
            v.append(Violation("emphasis-crutch", "error", crutch, line, snip))

    for jargon in AR_JARGON:
        for line, snip in _find_literal(text, jargon):
            v.append(Violation("jargon-inflation", "warn", jargon, line, snip))

    for vague in AR_VAGUE_DECLARATIVES:
        for line, snip in _find_literal(text, vague):
            v.append(Violation("vague-declarative", "error", vague, line, snip))

    for meta in AR_META_COMMENTARY:
        for line, snip in _find_literal(text, meta):
            v.append(Violation("meta-commentary", "error", meta, line, snip))

    # Untranslated abbreviations — heuristic: abbrev appears as a standalone
    # token but no Arabic word immediately precedes its "(abbrev)" introducer
    # form anywhere in the file. Uses word boundaries so "API" won't match
    # inside "GEMINI_API_KEY" and "ML" won't match inside "HTML".
    for abbrev in EN_ABBREVIATIONS_REQUIRING_TRANSLATION:
        # Build a tight match pattern: the abbreviation as its own token.
        # Handles "CI/CD" (contains /) and "SOC 2" (contains space).
        escaped = re.escape(abbrev)
        token_re = re.compile(rf"(?:(?<=^)|(?<=[^\w/]))({escaped})(?=[^\w/]|$)")
        if not token_re.search(text):
            continue
        # Intro pattern: Arabic word(s), optional whitespace, then (abbrev)
        intro_re = re.compile(rf"[\u0600-\u06FF][^()]*?\(\s*{escaped}\s*\)")
        if intro_re.search(text):
            continue
        # Get first occurrence for line reporting
        first_line = 0
        snippet = ""
        for i, ln in enumerate(text.split("\n"), 1):
            if token_re.search(ln):
                first_line = i
                snippet = ln.strip()[:120]
                break
        v.append(Violation(
            "untranslated-abbreviation",
            "error",
            abbrev,
            first_line,
            snippet,
        ))

    # Ambiguous tech terms — this is more nuanced (we can only flag for
    # human review). We flag if the bare form appears at all and leave the
    # caller to confirm each is qualified.
    for term, note in AR_AMBIGUOUS_TECH_TERMS.items():
        pattern = re.compile(rf"(^|\W){re.escape(term)}(\W|$)")
        for i, line in enumerate(text.split("\n"), 1):
            if pattern.search(line):
                v.append(Violation(
                    "ambiguous-tech-term",
                    "warn",
                    f"{term} — {note}",
                    i,
                    line.strip()[:120],
                ))
                break  # one hit per term is enough to surface the issue

    # واو chains — three+ "و " in one sentence (rough heuristic: three or
    # more " و" segments between punctuation)
    sentence_re = re.compile(r"[^.!؟،]+[.!؟،]?")
    for i, line in enumerate(text.split("\n"), 1):
        for sentence in sentence_re.findall(line):
            waw_count = len(re.findall(r"\sو", sentence))
            if waw_count >= 3:
                v.append(Violation(
                    "waw-chain",
                    "warn",
                    f"{waw_count} واو conjunctions in one sentence",
                    i,
                    sentence.strip()[:120],
                ))

    return v


def lint_english(text: str) -> list[Violation]:
    v: list[Violation] = []

    for opener in EN_BANNED_OPENERS:
        for line, snip in _find_regex(text, opener):
            v.append(Violation("banned-opener", "error", opener, line, snip))

    for crutch in EN_EMPHASIS_CRUTCHES:
        for line, snip in _find_regex(text, crutch):
            v.append(Violation("emphasis-crutch", "error", crutch, line, snip))

    for vague in EN_VAGUE_DECLARATIVES:
        for line, snip in _find_regex(text, vague):
            v.append(Violation("vague-declarative", "error", vague, line, snip))

    for meta in EN_META_COMMENTARY:
        for line, snip in _find_regex(text, meta):
            v.append(Violation("meta-commentary", "error", meta, line, snip))

    return v


def guess_language(path: Path | None, text: str) -> str:
    """Guess language from filename suffix first, then by character content."""
    if path is not None:
        name = path.name.lower()
        if ".ar." in name or name.endswith(".ar.html") or name.endswith(".ar.md"):
            return "ar"
        if ".en." in name or name.endswith(".en.html") or name.endswith(".en.md"):
            return "en"
    # Character ratio — Arabic codepoints
    ar_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    total = max(len(text), 1)
    return "ar" if ar_chars / total > 0.3 else "en"


def format_text(violations: list[Violation], file_label: str) -> str:
    if not violations:
        return f"✓ {file_label}: clean (0 violations)"

    errs = [v for v in violations if v.severity == "error"]
    warns = [v for v in violations if v.severity == "warn"]

    lines = [f"✗ {file_label}: {len(errs)} error(s), {len(warns)} warning(s)"]
    for v in violations:
        sev = "ERROR" if v.severity == "error" else "warn "
        lines.append(f"  [{sev}] L{v.line:4d} · {v.rule}: {v.pattern}")
        if v.snippet:
            lines.append(f"         → {v.snippet}")
    return "\n".join(lines)


def to_json(violations: list[Violation], file_label: str) -> str:
    return json.dumps({
        "file": file_label,
        "clean": not violations,
        "error_count": sum(1 for v in violations if v.severity == "error"),
        "warning_count": sum(1 for v in violations if v.severity == "warn"),
        "violations": [
            {
                "rule": v.rule,
                "severity": v.severity,
                "pattern": v.pattern,
                "line": v.line,
                "snippet": v.snippet,
            }
            for v in violations
        ],
    }, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib content lint — mechanical anti-slop")
    parser.add_argument("file", nargs="?", help="File to lint (HTML or MD)")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--lang", choices=["ar", "en"], help="Force language (default: auto-detect)")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    if args.stdin:
        raw = sys.stdin.read()
        file_label = "<stdin>"
        path = None
    else:
        if not args.file:
            print("✗ provide a file or --stdin", file=sys.stderr)
            return 2
        path = Path(args.file).expanduser()
        if not path.exists():
            print(f"✗ file not found: {path}", file=sys.stderr)
            return 2
        raw = path.read_text(encoding="utf-8")
        file_label = str(path)

    text = _extract_text(raw)
    lang = args.lang or guess_language(path, text)

    if lang == "ar":
        violations = lint_arabic(text)
    elif lang == "en":
        violations = lint_english(text)
    else:
        print(f"✗ unknown language: {lang}", file=sys.stderr)
        return 2

    if args.json:
        print(to_json(violations, file_label))
    else:
        print(format_text(violations, file_label))

    errors = sum(1 for v in violations if v.severity == "error")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
