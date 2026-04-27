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

# Tags whose direct text content reads as prose. Inside the body of
# one of these we replace text nodes with a single placeholder marker.
_PROSE_TAGS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "td", "th", "dt", "dd",
    "figcaption", "caption", "blockquote", "summary",
    "strong", "em", "b", "i", "u", "a", "span",
    "code", "pre", "small",
}


class _PreviewScrubber(HTMLParser):
    """Walk HTML, emit it with prose text nodes replaced by placeholders.

    Everything inside `_VERBATIM_TAGS` is passed through as-is so SVG
    diagrams and inline styles survive. Whitespace between tags is
    preserved (it affects layout). Self-closing tags are emitted with
    a leading slash to keep XHTML/HTML5 friendliness.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._out: list[str] = []
        self._verbatim_depth = 0
        # Track whether the current parent has already received a
        # placeholder, so nested <strong>X</strong> inside <p>foo<strong>X</strong> bar</p>
        # doesn't double up.
        self._placeholder_emitted_at_depth: list[bool] = [False]

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
        self._placeholder_emitted_at_depth.append(False)

    def handle_startendtag(self, tag: str, attrs):
        # Self-closing in source. Emit as void tag verbatim; no children.
        self._out.append(f"<{tag}{self._attrs_str(attrs)} />")

    def handle_endtag(self, tag: str):
        self._out.append(f"</{tag}>")
        if tag in _VERBATIM_TAGS and self._verbatim_depth > 0:
            self._verbatim_depth -= 1
        if len(self._placeholder_emitted_at_depth) > 1:
            self._placeholder_emitted_at_depth.pop()

    def handle_data(self, data: str):
        if self._verbatim_depth > 0:
            self._out.append(data)
            return
        # Pure whitespace passes through unchanged so block-level
        # whitespace doesn't collapse into solid runs of placeholders.
        if not data.strip():
            self._out.append(data)
            return
        # Collapse all narrative text inside this element to a single
        # placeholder. Subsequent text nodes at the same depth get
        # nothing — keeps things readable.
        if not self._placeholder_emitted_at_depth[-1]:
            self._out.append("[…]")
            self._placeholder_emitted_at_depth[-1] = True

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
_LABEL_OVERRIDES = {
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


def _humanize_key(key: str) -> str:
    """Return a user-facing label for a recipe input key.

    Looks up the override map first (where Katib-internal vocab gets
    standard user-facing names), then falls back to a simple
    humanization for unknown keys so user-authored components still
    get something readable.
    """
    if key in _LABEL_OVERRIDES:
        return _LABEL_OVERRIDES[key]
    return key.replace("_", " ").replace("-", " ").strip().capitalize() or "Field"


def _scrub_string(key: str, value: str) -> str:
    if _looks_like_html(value):
        parser = _PreviewScrubber()
        parser.feed(value)
        parser.close()
        return parser.output
    # Plain string. Empty strings pass through (they're often layout sentinels).
    if not value.strip():
        return value
    return f"[{_humanize_key(key)}]"


def _singularize(label: str) -> str:
    """Best-effort singularization for numbered list placeholders."""
    if label.endswith("ies") and len(label) > 3:
        return label[:-3] + "y"
    if label.endswith("ses") and len(label) > 3:
        return label[:-2]
    if label.endswith("s") and not label.endswith("ss"):
        return label[:-1]
    return label


def _scrub_list(key: str, items: list[Any]) -> list[Any]:
    item_label = _singularize(_humanize_key(key))
    out: list[Any] = []
    for i, item in enumerate(items, start=1):
        if isinstance(item, str):
            if _looks_like_html(item):
                parser = _PreviewScrubber()
                parser.feed(item)
                parser.close()
                out.append(parser.output)
            elif item.strip():
                out.append(f"[{item_label} {i}]")
            else:
                out.append(item)
        elif isinstance(item, dict):
            out.append(_scrub_dict(item))
        elif isinstance(item, list):
            out.append(_scrub_list(key, item))
        else:
            out.append(item)
    return out


def _scrub_dict(d: dict[str, Any]) -> dict[str, Any]:
    """In-place scrub of a single inputs dict. Image slots are kept
    intact — they're declared shapes, not narrative content. We
    detect them by the presence of a `source` or `path` key."""
    if "source" in d or "path" in d or "resolved_path" in d:
        return d
    for key, val in list(d.items()):
        if val is None:
            continue
        if isinstance(val, str):
            d[key] = _scrub_string(key, val)
        elif isinstance(val, list):
            d[key] = _scrub_list(key, val)
        elif isinstance(val, dict):
            d[key] = _scrub_dict(val)
        # numbers, bools — leave alone (page counts, flags, etc.)
    return d


def scrub_recipe_for_preview(recipe: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied recipe whose inputs are template placeholders.

    Section structure (component, variant, order) is preserved.
    Image slot declarations are preserved. Only narrative text is
    rewritten — to "[Title]", "[Body content]", "[…]" markers, etc.

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
        out["description"] = "[Description]"

    for section in out.get("sections", []) or []:
        if isinstance(section.get("inputs"), dict):
            _scrub_dict(section["inputs"])
        ibl = section.get("inputs_by_lang")
        if isinstance(ibl, dict):
            for lang_inputs in ibl.values():
                if isinstance(lang_inputs, dict):
                    _scrub_dict(lang_inputs)
    return out
