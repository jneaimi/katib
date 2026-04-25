"""Content lint — static catch for mechanical anti-slop violations (ported from v1).

Library-first: rules + `lint_arabic` + `lint_english` + `_extract_text` +
`guess_language` are all importable. The thin CLI lives at `scripts/lint.py`.

Not a replacement for the 5-dimension anti-slop score in `writing.{lang}.md`
(that requires human judgement). This catches the mechanical ones: banned
openers, emphasis crutches, jargon inflation, untranslated English
abbreviations, unqualified ambiguous tech terms, and واو-chain runaways.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


# ===================== Arabic rules =====================

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

AR_JARGON = [
    "تحقيق التحول الرقمي الشامل",
    "تعزيز منظومة الابتكار",
    "الاستفادة من البيانات الضخمة",
    "بناء قدرات مستدامة",
    "إطلاق العنان لـ",
    "تسخير قوة",
    "تحقيق قفزة نوعية",
]

AR_VAGUE_DECLARATIVES = [
    "النتائج مذهلة",
    "الفرص لا حصر لها",
    "المستقبل واعد",
    "الإمكانيات هائلة",
    "العالم يتغير بسرعة",
    "هذا يغير كل شيء",
]

AR_META_COMMENTARY = [
    "في هذا المقال سنتناول",
    "كما سنرى لاحقاً",
    "دعونا نلخّص",
    "كما ذكرنا سابقاً",
    "دعونا نستعرض",
    "من المهم أن نفهم أن",
    "يجب أن نتذكر أن",
]

AR_AMBIGUOUS_TECH_TERMS = {
    "الوكيل": "qualify with الذكي or pair with 'الذكاء الاصطناعي' for clarity",
    "وكيل": "qualify with الذكي",
    "الوكلاء": "qualify with الأذكياء",
    "وكلاء": "qualify with الأذكياء",
}

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


# ===================== HTML / markup rules =====================

# Arabic Unicode ranges: base block, presentation forms A and B.
_RE_ARABIC_CHARS = re.compile(r"[؀-ۿﭐ-﷿ﹰ-﻿]")
_RE_SVG_BLOCK = re.compile(r"<svg\b[^>]*>(.*?)</svg>", re.DOTALL | re.IGNORECASE)
_RE_TEXT_TAG = re.compile(r"<text\b[^>]*>(.*?)</text>", re.DOTALL | re.IGNORECASE)

_ARABIC_IN_SVG_TEXT_MESSAGE = (
    "Arabic text inside SVG <text> element. WeasyPrint cannot shape Arabic in "
    "SVG. Use the HTML-overlay pattern: SVG geometry + position:absolute HTML "
    "labels. See COMPONENT-BUILDER.md §Arabic in SVG diagrams or "
    "recipes/bilingual-svg-diagram.yaml for a working example."
)


# ===================== Core linter =====================


@dataclass
class Violation:
    rule: str
    severity: str   # "error" | "warn"
    pattern: str
    line: int
    snippet: str

    def as_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "pattern": self.pattern,
            "line": self.line,
            "snippet": self.snippet,
        }


def extract_text(raw: str) -> str:
    """Strip HTML tags and Jinja templates so we lint prose, not markup."""
    text = re.sub(r"\{\{.*?\}\}", " ", raw, flags=re.DOTALL)
    text = re.sub(r"\{%.*?%\}", " ", text, flags=re.DOTALL)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&mdash;", "—")
    return text


def _find_literal(text: str, needle: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(text.split("\n"), 1):
        if needle in line:
            hits.append((i, line.strip()[:120]))
    return hits


def _find_regex(text: str, pattern: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    regex = re.compile(pattern, re.IGNORECASE)
    for i, line in enumerate(text.split("\n"), 1):
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

    for abbrev in EN_ABBREVIATIONS_REQUIRING_TRANSLATION:
        escaped = re.escape(abbrev)
        token_re = re.compile(rf"(?:(?<=^)|(?<=[^\w/]))({escaped})(?=[^\w/]|$)")
        if not token_re.search(text):
            continue
        intro_re = re.compile(rf"[؀-ۿ][^()]*?\(\s*{escaped}\s*\)")
        if intro_re.search(text):
            continue
        first_line = 0
        snippet = ""
        for i, ln in enumerate(text.split("\n"), 1):
            if token_re.search(ln):
                first_line = i
                snippet = ln.strip()[:120]
                break
        v.append(Violation("untranslated-abbreviation", "error", abbrev, first_line, snippet))

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
                break   # one hit per term

    # واو chains — 3+ "و " in a sentence
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


def lint_html_arabic_in_svg_text(raw: str) -> list[Violation]:
    """Scan raw markup for Arabic characters inside SVG <text> elements.

    WeasyPrint's SVG renderer cannot shape Arabic — letters appear in
    isolated forms with no bidi reorder. The fix is the HTML-overlay
    pattern (geometry-only SVG + position:absolute HTML labels).

    Runs unconditionally — Arabic strings can leak into charts even when
    the document language is English (e.g., user-supplied data, mixed
    labels). Emits one HARD ERROR per offending <text> element.
    """
    violations: list[Violation] = []
    for svg_match in _RE_SVG_BLOCK.finditer(raw):
        svg_body = svg_match.group(1)
        svg_start_offset = svg_match.start()
        for text_match in _RE_TEXT_TAG.finditer(svg_body):
            content = text_match.group(1)
            if not content.strip():
                continue
            if _RE_ARABIC_CHARS.search(content):
                # Find the line number in the original raw string.
                abs_offset = svg_start_offset + text_match.start()
                line_no = raw.count("\n", 0, abs_offset) + 1
                excerpt = re.sub(r"\s+", " ", content).strip()[:80]
                violations.append(Violation(
                    rule="ARABIC_IN_SVG_TEXT",
                    severity="error",
                    pattern=_ARABIC_IN_SVG_TEXT_MESSAGE,
                    line=line_no,
                    snippet=excerpt,
                ))
    return violations


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
    """Guess language from filename suffix first, then character ratio."""
    if path is not None:
        name = path.name.lower()
        if ".ar." in name or name.endswith(".ar.html") or name.endswith(".ar.md"):
            return "ar"
        if ".en." in name or name.endswith(".en.html") or name.endswith(".en.md"):
            return "en"
    ar_chars = sum(1 for c in text if "؀" <= c <= "ۿ")
    total = max(len(text), 1)
    return "ar" if ar_chars / total > 0.3 else "en"


def lint(text: str, lang: str) -> list[Violation]:
    """Dispatch to the right language linter."""
    if lang == "ar":
        return lint_arabic(text)
    if lang == "en":
        return lint_english(text)
    raise ValueError(f"unsupported lang {lang!r}; expected 'ar' or 'en'")


def lint_file(path: Path, lang: str | None = None) -> tuple[list[Violation], str]:
    """Lint a file on disk. Returns (violations, resolved_lang)."""
    raw = path.read_text(encoding="utf-8")
    text = extract_text(raw)
    resolved = lang or guess_language(path, text)
    violations = lint(text, resolved)
    # HTML-level rules run on raw markup (always, regardless of language) —
    # Arabic can leak into SVG <text> in any document.
    violations.extend(lint_html_arabic_in_svg_text(raw))
    return violations, resolved
