"""Marketplace HTML previews (Slice B).

`pack export --with-previews` calls into here to render the same HTML
the renderer produces for PDF, then stamps it into the pack under
`previews/<artifact>.<lang>.html`. The marketplace publisher uploads
each preview to R2 and the registry UI embeds them in a sandboxed
iframe so visitors can preview before installing.

Design constraints:
  - The PDF and the preview render from the *same* compose() output —
    no second template path to drift.
  - The captured HTML must be self-contained: any image referenced by
    an absolute filesystem path is inlined as a `data:` URL so the
    iframe never tries to fetch from the publisher's machine.
  - We add a small <link> to Google Fonts so headings/body text in the
    iframe look close to what WeasyPrint produces with local fonts.
    Drift is acceptable — preview is a likeness, not a re-render.
  - Pure function: given the same recipe + lang, output bytes are
    deterministic enough for the pack's content_hash to stay stable
    across re-exports. The compose() metadata block IS dropped before
    bytes are emitted (it carries a resolved-image cache path that is
    machine-specific).
"""
from __future__ import annotations

import base64
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

from core.compose import compose
from core.preview_scrub import scrub_recipe_for_preview


GOOGLE_FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@300;400;500;600;700&'
    'family=Cairo:wght@300;400;500;600;700&'
    'family=Amiri:wght@400;700&display=swap" rel="stylesheet">'
)


@dataclass(frozen=True)
class PreviewEntry:
    """One rendered preview destined for the pack tarball."""

    arcname: str           # "previews/<name>.<lang>.html"
    body: bytes            # the captured HTML bytes
    manifest_entry: dict   # what goes into marketplace.previews[]


def _supported_langs(recipe_or_component: dict) -> list[str]:
    """Return langs we'll render previews for, intersected with [en, ar]."""
    declared = recipe_or_component.get("languages") or []
    return [lang for lang in declared if lang in ("en", "ar")]


# Match `src="<absolute fs path>"` in <img> tags. We deliberately do
# not try to be perfectly defensive — components produce well-formed
# HTML, and a missed match falls through to a broken image in the
# preview rather than a publish failure.
_IMG_SRC_RE = re.compile(
    r'<img\b[^>]*?\bsrc="(?P<src>[^"]+)"',
    flags=re.IGNORECASE,
)


def _content_type_for(p: Path) -> str:
    ext = p.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }.get(ext, "application/octet-stream")


def inline_image_assets(html: str) -> str:
    """Rewrite <img src="<abs fs path>"> → data: URL for self-contained HTML.

    Leaves data:, http(s):, and relative paths untouched. Skips any path
    that doesn't resolve to a readable file (the iframe will show a
    broken image — better than failing the publish).
    """

    def repl(match: re.Match[str]) -> str:
        src = match.group("src")
        if src.startswith(("data:", "http://", "https://", "//", "./", "../")):
            return match.group(0)
        path = Path(src)
        if not path.is_absolute() or not path.is_file():
            return match.group(0)
        try:
            data = path.read_bytes()
        except OSError:
            return match.group(0)
        encoded = base64.b64encode(data).decode("ascii")
        new_src = f"data:{_content_type_for(path)};base64,{encoded}"
        # Replace just the src= value in the original tag, preserving
        # anything else inside the tag (alt, class, etc.).
        return match.group(0).replace(src, new_src, 1)

    return _IMG_SRC_RE.sub(repl, html)


def _inject_fonts_link(html: str) -> str:
    """Add Google Fonts <link> tags so the iframe gets close-to-PDF type.

    compose() emits a complete <html><head>...</head><body>...</body></html>
    document. We splice the fonts link into <head>. If <head> isn't found
    (shouldn't happen), return the HTML unchanged.
    """
    head_close = html.find("</head>")
    if head_close == -1:
        return html
    return html[:head_close] + GOOGLE_FONTS_LINK + "\n" + html[head_close:]


def render_recipe_previews(
    recipe: dict,
    *,
    brand: str | None = None,
) -> list[PreviewEntry]:
    """Render every supported lang of a recipe into preview HTML entries.

    The recipe is scrubbed to template form before compose() runs —
    real content (titles, authors, prose) is replaced with [Field]
    placeholders so a marketplace browser sees layout, not commitment.
    Section structure, variants, and image slot declarations survive
    intact.

    Returns an empty list if the recipe declares no `en`/`ar` language.
    Raises ValueError when compose() fails — caller decides whether
    that's fatal for the export or just a warning.
    """
    name = recipe["name"]

    entries: list[PreviewEntry] = []
    # compose() resolves recipes by name OR path. Writing the scrubbed
    # recipe to a temp file keeps compose unchanged. We re-scrub per
    # lang so placeholder labels and lorem text match the script of
    # the rendered template (Arabic placeholders inside RTL layout).
    with tempfile.TemporaryDirectory(prefix="katib-preview-") as tmp:
        for lang in _supported_langs(recipe):
            scrubbed = scrub_recipe_for_preview(recipe, lang=lang)
            tmp_path = Path(tmp) / f"{name}.{lang}.yaml"
            tmp_path.write_text(
                yaml.safe_dump(scrubbed, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            html, _meta = compose(str(tmp_path), lang=lang, brand=brand)
            html = inline_image_assets(html)
            html = _inject_fonts_link(html)
            body = html.encode("utf-8")
            entries.append(
                PreviewEntry(
                    arcname=f"previews/{name}.{lang}.html",
                    body=body,
                    manifest_entry={
                        "path": f"previews/{name}.{lang}.html",
                        "recipe": name,
                        "lang": lang,
                    },
                )
            )
    return entries
