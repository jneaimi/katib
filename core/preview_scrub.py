"""Scrub recipe inputs to template-form for marketplace previews.

Marketplace previews advertise *layout*, not *content*. A pack browser
should see "this is a 16-page tutorial layout with cover, objectives,
8 modules, summary" — not "this specific document by Alex Acme about
Bloom's framework". The recipe inputs are the content commitment;
this module strips them to placeholders while preserving the visual
structure.

What gets scrubbed:
  - Top-level string inputs → "[Field name]" placeholder.
  - Lists of strings → "[Field name 1]", "[Field name 2]", …
  - Lists of dicts (e.g., footnotes, citations) → recurse into each.
  - HTML-bearing inputs (`raw_body`, `*_html`) → keep tag structure,
    replace prose text nodes with "[…]" markers, keep <svg>, <style>,
    and <script> subtrees verbatim (the SVG diagrams ARE structure).

What's left alone:
  - Image / SVG inputs (declared as image slots in component.yaml).
  - Section structure (which components, in what order, with what
    variant) — that's the layout we're showing off.
  - Brand / token overrides — colors and type are part of the layout.

Public entry: `scrub_recipe_for_preview(recipe_dict) -> recipe_dict`.
Returns a deep-copied recipe; never mutates the input.
"""
from __future__ import annotations

import copy
import re
from html.parser import HTMLParser
from typing import Any


# Tag classes for HTML scrubbing. Anything inside one of these stays
# verbatim — they carry structural value, not narrative content.
_VERBATIM_TAGS = {"svg", "style", "script", "defs", "symbol"}


# Lorem corpora — fixed, deterministic. Used to fill prose text nodes so
# the preview LOOKS like a populated document instead of a wireframe of
# "[…]" markers. Long enough that the proportional fill picks varied
# sentences for varied paragraph lengths.
#
# We carry a Latin and an Arabic corpus so the AR preview reads with
# proper Arabic-script placeholders inside an RTL layout — Latin lorem
# in an RTL container looks broken at a glance and undersells the
# template.
_LOREM_SENTENCES_EN = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
    "Nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit in voluptate velit esse.",
    "Cillum dolore eu fugiat nulla pariatur.",
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia.",
    "Deserunt mollit anim id est laborum.",
    "Curabitur pretium tincidunt lacus, nulla gravida orci a odio.",
    "Nullam varius turpis et commodo pharetra, est eros bibendum elit.",
    "Cras semper auctor neque vitae tempus quam pellentesque nec.",
    "Vestibulum lectus mauris ultrices eros in cursus turpis massa.",
)

# Arabic placeholder prose. Plain MSA, generic enough to read as
# placeholder text rather than a real sentence about anything specific.
# 12 sentences mirrors the Latin corpus so the rotation pattern matches.
_LOREM_SENTENCES_AR = (
    "هذا نصٌّ تجريبيٌّ يُستخدم لعرض شكل القالب وتوزيع المحتوى فيه.",
    "يهدف هذا النص إلى محاكاة الكتلة النصية الفعلية دون التزامٍ بمحتوى بعينه.",
    "يمكن استبدال هذه الفقرات لاحقًا بنصوصكم الأصلية عند تركيب القالب.",
    "تتوزّع العناوين والفقرات لإبراز الإيقاع البصري للصفحة.",
    "تخدم الصور والرسوم التوضيحية فهم الأقسام دون أن تكون جزءًا من السرد.",
    "يحرص القالب على تنظيم المعلومة وتسلسلها بصريًا قبل الالتزام بالمحتوى.",
    "تعطي الفواصل والمسافات النص مساحة للتنفّس وتحسّن قابلية القراءة.",
    "يحافظ التصميم على اتساق نوع الخط ومقاسه عبر جميع الأقسام.",
    "تظهر القوائم والجداول بصورتها التخطيطية لمعاينة بنيتها.",
    "يجمع القالب بين النص والعناصر البصرية في تركيبٍ متوازن.",
    "تكشف المعاينة عن طبيعة الإخراج النهائي قبل إدخال المحتوى الحقيقي.",
    "يُتيح هذا التنسيق تقدير عدد الصفحات وكثافة المحتوى المتوقّعة.",
)

# Cap how much lorem we emit per element so a 5000-char paragraph
# doesn't blow up into 5000 chars of fake text. Visual layout signal
# stops being useful past this threshold.
_LOREM_MAX_CHARS = 480


def _corpus_for(lang: str) -> tuple[str, ...]:
    return _LOREM_SENTENCES_AR if lang == "ar" else _LOREM_SENTENCES_EN


def _lorem_for_length(
    target_chars: int, *, start_index: int = 0, lang: str = "en"
) -> str:
    """Deterministic lorem fill, length proportional to original text."""
    target = min(max(target_chars, 24), _LOREM_MAX_CHARS)
    corpus = _corpus_for(lang)
    parts: list[str] = []
    used = 0
    i = 0
    while used < target:
        s = corpus[(start_index + i) % len(corpus)]
        parts.append(s)
        used += len(s) + 1  # +1 for the joining space
        i += 1
    out = " ".join(parts)
    # Don't trim mid-word — return the whole-sentence sequence.
    return out


class _PreviewScrubber(HTMLParser):
    """Walk HTML, emit it with prose text nodes replaced by lorem ipsum.

    Each element's original prose length is summed and replaced with a
    proportional lorem fill at the close tag, so the rendered preview
    keeps the same layout density as the real document. Nested inline
    elements (<strong>, <em>) emit their own short lorem inline so
    typography emphasis still shows up.

    `_VERBATIM_TAGS` (svg, style, script, defs, symbol) pass through as-is.
    Whitespace between tags is preserved (it affects layout).
    """

    def __init__(self, *, lang: str = "en") -> None:
        super().__init__(convert_charrefs=False)
        self._out: list[str] = []
        self._verbatim_depth = 0
        self._lang = lang
        # Stack of (open_tag, char_count_of_original_text, output_index_to_inject).
        # When we hit a starttag for a prose element, we remember the
        # output position — at the matching endtag we splice a lorem
        # block back in proportional to the consumed text length.
        self._prose_stack: list[tuple[str, int, int]] = []
        # Rotating index into the lorem corpus to vary which sentences
        # land in which paragraph — keeps a wall of identical text from
        # repeating verbatim across modules.
        self._lorem_cursor = 0

    @property
    def output(self) -> str:
        return "".join(self._out)

    def _attrs_str(self, attrs: list[tuple[str, str | None]]) -> str:
        parts: list[str] = []
        for k, v in attrs:
            if v is None:
                parts.append(k)
            else:
                escaped = v.replace("&", "&amp;").replace('"', "&quot;")
                parts.append(f'{k}="{escaped}"')
        return (" " + " ".join(parts)) if parts else ""

    def handle_starttag(self, tag: str, attrs):
        self._out.append(f"<{tag}{self._attrs_str(attrs)}>")
        if tag in _VERBATIM_TAGS:
            self._verbatim_depth += 1
            return
        # Mark this element's text-injection point for the close tag.
        self._prose_stack.append((tag, 0, len(self._out)))

    def handle_startendtag(self, tag: str, attrs):
        # Self-closing in source. Emit as void tag verbatim; no children.
        self._out.append(f"<{tag}{self._attrs_str(attrs)} />")

    def handle_endtag(self, tag: str):
        if tag in _VERBATIM_TAGS:
            self._out.append(f"</{tag}>")
            if self._verbatim_depth > 0:
                self._verbatim_depth -= 1
            return
        # Pop matching prose entry; if the stack mismatches (broken HTML)
        # just emit the close tag and keep going.
        if self._prose_stack and self._prose_stack[-1][0] == tag:
            _, char_count, inject_at = self._prose_stack.pop()
            if char_count > 0:
                lorem = _lorem_for_length(
                    char_count, start_index=self._lorem_cursor, lang=self._lang
                )
                self._lorem_cursor += 1
                # Splice the lorem back in at the position the original
                # text sat — preserves any leading/trailing whitespace
                # we already emitted around it.
                self._out.insert(inject_at, lorem)
        self._out.append(f"</{tag}>")

    def handle_data(self, data: str):
        if self._verbatim_depth > 0:
            self._out.append(data)
            return
        # Pure whitespace passes through unchanged so block-level
        # whitespace doesn't collapse into solid runs of placeholders.
        if not data.strip():
            self._out.append(data)
            return
        # Accumulate the original char count on the deepest open prose
        # element. Don't emit anything yet — the close tag splices in
        # the lorem replacement in one shot.
        if self._prose_stack:
            tag, count, inject_at = self._prose_stack[-1]
            self._prose_stack[-1] = (tag, count + len(data.strip()), inject_at)
        else:
            # Top-level text outside any element — emit a small lorem
            # so we don't leak the original.
            self._out.append(
                _lorem_for_length(
                    len(data.strip()),
                    start_index=self._lorem_cursor,
                    lang=self._lang,
                )
            )
            self._lorem_cursor += 1

    def handle_entityref(self, name: str):
        # Keep entity references; some are layout-relevant (&nbsp;).
        self._out.append(f"&{name};")

    def handle_charref(self, name: str):
        self._out.append(f"&#{name};")

    def handle_comment(self, data: str):
        self._out.append(f"<!--{data}-->")

    def handle_decl(self, decl: str):
        self._out.append(f"<!{decl}>")


_HTML_HINT = re.compile(r"<[a-zA-Z]")


def _looks_like_html(s: str) -> bool:
    return bool(_HTML_HINT.search(s))


# Map Katib-component vocabulary onto labels a non-Katib user would
# expect to see in a template. "eyebrow" is internal jargon for the
# small line above a heading; users call that a tag/category.
# Anything not in here falls back to the humanized key so we still
# get something readable for arbitrary user-authored components.
_LABEL_OVERRIDES_EN = {
    "eyebrow": "Tag",
    "kicker": "Tag",
    "title": "Title",
    "subtitle": "Subtitle",
    "heading": "Heading",
    "subheading": "Subheading",
    "author": "Author",
    "authors": "Author",
    "byline": "Author",
    "date": "Date",
    "published_at": "Date",
    "reference_code": "Reference",
    "ref": "Reference",
    "label": "Label",
    "tag": "Tag",
    "category": "Category",
    "intro": "Intro",
    "lede": "Intro",
    "summary": "Summary",
    "abstract": "Summary",
    "raw_body": "Body",
    "raw_html": "Body",
    "body": "Body",
    "content": "Content",
    "items": "Item",
    "list_items": "Item",
    "footer": "Footer",
    "caption": "Caption",
    "alt": "Caption",
    "quote": "Quote",
    "attribution": "Attribution",
    "name": "Name",
    "role": "Role",
    "description": "Description",
    "note": "Note",
    "callout": "Note",
}

_LABEL_OVERRIDES_AR = {
    "eyebrow": "تصنيف",
    "kicker": "تصنيف",
    "title": "العنوان",
    "subtitle": "العنوان الفرعي",
    "heading": "عنوان",
    "subheading": "عنوان فرعي",
    "author": "الكاتب",
    "authors": "الكاتب",
    "byline": "الكاتب",
    "date": "التاريخ",
    "published_at": "التاريخ",
    "reference_code": "المرجع",
    "ref": "المرجع",
    "label": "تسمية",
    "tag": "تصنيف",
    "category": "الفئة",
    "intro": "تمهيد",
    "lede": "تمهيد",
    "summary": "الملخّص",
    "abstract": "الملخّص",
    "raw_body": "النص",
    "raw_html": "النص",
    "body": "النص",
    "content": "المحتوى",
    "items": "عنصر",
    "list_items": "عنصر",
    "footer": "تذييل",
    "caption": "وصف",
    "alt": "وصف",
    "quote": "اقتباس",
    "attribution": "النسبة",
    "name": "الاسم",
    "role": "الدور",
    "description": "الوصف",
    "note": "ملاحظة",
    "callout": "ملاحظة",
}

_DESCRIPTION_PLACEHOLDER = {"en": "[Description]", "ar": "[الوصف]"}


def _humanize_key(key: str, *, lang: str = "en") -> str:
    """Return a user-facing label for a recipe input key.

    Looks up the override map first (where Katib-internal vocab gets
    standard user-facing names), then falls back to a simple
    humanization for unknown keys so user-authored components still
    get something readable.
    """
    overrides = _LABEL_OVERRIDES_AR if lang == "ar" else _LABEL_OVERRIDES_EN
    if key in overrides:
        return overrides[key]
    # Generic fallback. We don't try to translate unknown keys to AR;
    # showing a humanized English token is better than emitting the
    # raw key in either language.
    return key.replace("_", " ").replace("-", " ").strip().capitalize() or "Field"


def _scrub_string(key: str, value: str, *, lang: str) -> str:
    if _looks_like_html(value):
        parser = _PreviewScrubber(lang=lang)
        parser.feed(value)
        parser.close()
        return parser.output
    # Plain string. Empty strings pass through (they're often layout sentinels).
    if not value.strip():
        return value
    return f"[{_humanize_key(key, lang=lang)}]"


def _singularize(label: str) -> str:
    """Best-effort singularization for numbered list placeholders."""
    if label.endswith("ies") and len(label) > 3:
        return label[:-3] + "y"
    if label.endswith("ses") and len(label) > 3:
        return label[:-2]
    if label.endswith("s") and not label.endswith("ss"):
        return label[:-1]
    return label


def _scrub_list(key: str, items: list[Any], *, lang: str) -> list[Any]:
    item_label = _singularize(_humanize_key(key, lang=lang))
    out: list[Any] = []
    for i, item in enumerate(items, start=1):
        if isinstance(item, str):
            if _looks_like_html(item):
                parser = _PreviewScrubber(lang=lang)
                parser.feed(item)
                parser.close()
                out.append(parser.output)
            elif item.strip():
                out.append(f"[{item_label} {i}]")
            else:
                out.append(item)
        elif isinstance(item, dict):
            out.append(_scrub_dict(item, lang=lang))
        elif isinstance(item, list):
            out.append(_scrub_list(key, item, lang=lang))
        else:
            out.append(item)
    return out


def _scrub_dict(d: dict[str, Any], *, lang: str) -> dict[str, Any]:
    """In-place scrub of a single inputs dict. Image slots are kept
    intact — they're declared shapes, not narrative content. We
    detect them by the presence of a `source` or `path` key."""
    if "source" in d or "path" in d or "resolved_path" in d:
        return d
    for key, val in list(d.items()):
        if val is None:
            continue
        if isinstance(val, str):
            d[key] = _scrub_string(key, val, lang=lang)
        elif isinstance(val, list):
            d[key] = _scrub_list(key, val, lang=lang)
        elif isinstance(val, dict):
            d[key] = _scrub_dict(val, lang=lang)
        # numbers, bools — leave alone (page counts, flags, etc.)
    return d


def scrub_recipe_for_preview(
    recipe: dict[str, Any], *, lang: str = "en"
) -> dict[str, Any]:
    """Return a deep-copied recipe whose inputs are template placeholders.

    Section structure (component, variant, order) is preserved.
    Image slot declarations are preserved. Only narrative text is
    rewritten — to "[Title]", "[Body content]", lorem-style fill, etc.

    Pass `lang="ar"` to render placeholders and lorem text in Arabic
    so the AR preview reads naturally inside an RTL layout.

    Recipe-level metadata that surfaces in rendered output (notably
    `description`, which compose() uses as the HTML <title>) is also
    cleared so the original example's content doesn't leak through
    the page title.
    """
    out = copy.deepcopy(recipe)

    # The renderer reads `description` for the HTML <title> tag,
    # falling back to `name`. Replace it with a neutral marker so
    # the example pack's pitch ("Bloom's framework — production
    # tutorial recipe…") doesn't leak through the preview's <title>.
    if isinstance(out.get("description"), str):
        out["description"] = _DESCRIPTION_PLACEHOLDER.get(lang, "[Description]")

    for section in out.get("sections", []) or []:
        if isinstance(section.get("inputs"), dict):
            _scrub_dict(section["inputs"], lang=lang)
        ibl = section.get("inputs_by_lang")
        if isinstance(ibl, dict):
            for lang_inputs in ibl.values():
                if isinstance(lang_inputs, dict):
                    _scrub_dict(lang_inputs, lang=lang)
    return out
