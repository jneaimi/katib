"""Marketplace PNG previews (Slice B v2).

`pack export --with-previews` calls into here to render the same compose()
output the renderer produces for PDF, push it through WeasyPrint to a
PDF, then rasterize the first few pages to PNG via pypdfium2 and stamp
them into the pack under `previews/<artifact>.<lang>.pageN.png`. The
marketplace publisher uploads each PNG to R2 and the registry UI shows
them as a vertical image strip — no iframe, no PDF embed quirks.

Why PNG instead of HTML or PDF:
  - Card thumbnails use the page-1 image directly (single `<img>` tag,
    fast).
  - Detail page renders an image strip; mobile-friendly, zero browser
    quirks.
  - One render path serves both templates and components — components
    are wrapped in a synthesized one-section recipe and run through the
    same scrub → compose → PDF → PNG pipeline. No second code path.

Privacy:
  - Recipe inputs go through `scrub_recipe_for_preview` first — every
    string becomes a `[Field]` placeholder or proportional lorem ipsum
    BEFORE compose() ever sees it.
  - SVG `<text>` content is scrubbed too (commit removes `svg` from the
    scrubber's verbatim list, with a regex pass to restore camelCase
    attributes like `viewBox`).
  - Component-preview inputs are synthesized neutral defaults — never
    pulled from author-specific examples.
"""
from __future__ import annotations

import io
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

from core.compose import compose
from core.preview_scrub import scrub_recipe_for_preview
from core.render import render_to_pdf


# Cap pages per (artifact × lang). Marketplace previews are a quick
# look, not a full read — the pack itself is the canonical source.
# Three pages covers most templates' first impression (cover + first
# content page + structure sample) without ballooning pack size.
PREVIEW_MAX_PAGES = 3

# pypdfium2 page render scale. ~1.5 ≈ 144 DPI on letter — sharp enough
# for the marketplace card AND the detail strip without blowing the
# pack tarball past a few MB.
PREVIEW_RENDER_SCALE = 1.5


# Neutral placeholder image for component previews where the component
# requires an image input. Synthesized so we never ship author-specific
# image content as part of the marketplace preview pipeline.
_PLACEHOLDER_IMAGE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet">
  <rect width="600" height="400" fill="#E5DED1"/>
  <rect x="20" y="20" width="560" height="360" fill="none" stroke="#7A7268" stroke-width="3" stroke-dasharray="12 8"/>
  <text x="300" y="210" text-anchor="middle" font-family="serif" font-size="22" fill="#7A7268" font-style="italic">[Image]</text>
</svg>"""


@dataclass(frozen=True)
class PreviewEntry:
    """One rendered preview page destined for the pack tarball."""

    arcname: str           # "previews/<name>.<lang>.pageN.png"
    body: bytes            # the captured PNG bytes
    manifest_entry: dict   # what goes into marketplace.previews[]


def _supported_langs(recipe_or_component: dict) -> list[str]:
    """Return langs we'll render previews for, intersected with [en, ar]."""
    declared = recipe_or_component.get("languages") or []
    return [lang for lang in declared if lang in ("en", "ar")]


def _render_pdf_pages_to_png(pdf_path: Path) -> list[bytes]:
    """Rasterize the first `PREVIEW_MAX_PAGES` of a PDF to PNG bytes.

    Uses pypdfium2 (PDFium bindings) — pure-Python wheel, no system
    deps. Returns one PNG payload per page, in order.
    """
    # Lazy import — pypdfium2 ships a sizable native blob; pulling it
    # only when previews are actually being rendered keeps the default
    # `pack export` (no --with-previews) cheap.
    import pypdfium2 as pdfium  # type: ignore

    pdf = pdfium.PdfDocument(str(pdf_path))
    pages: list[bytes] = []
    n = min(len(pdf), PREVIEW_MAX_PAGES)
    for i in range(n):
        page = pdf[i]
        bitmap = page.render(scale=PREVIEW_RENDER_SCALE)
        pil = bitmap.to_pil()
        buf = io.BytesIO()
        pil.save(buf, format="PNG", optimize=True)
        pages.append(buf.getvalue())
    pdf.close()
    return pages


def _render_one_lang(
    recipe_yaml_path: Path,
    *,
    lang: str,
    brand: str | None,
    pdf_dir: Path,
) -> list[bytes]:
    """Compose → write PDF → rasterize. Returns one PNG payload per page."""
    html, _meta = compose(str(recipe_yaml_path), lang=lang, brand=brand)
    pdf_path = pdf_dir / f"{recipe_yaml_path.stem}.pdf"
    render_to_pdf(html, pdf_path)
    return _render_pdf_pages_to_png(pdf_path)


def _entries_for(
    *,
    name: str,
    kind: str,            # "recipe" or "component"
    lang: str,
    page_pngs: list[bytes],
) -> list[PreviewEntry]:
    out: list[PreviewEntry] = []
    for page_idx, body in enumerate(page_pngs, start=1):
        arc = f"previews/{name}.{lang}.page{page_idx}.png"
        manifest: dict = {
            "path": arc,
            "lang": lang,
            "page": page_idx,
            kind: name,
        }
        out.append(PreviewEntry(arcname=arc, body=body, manifest_entry=manifest))
    return out


def render_recipe_previews(
    recipe: dict,
    *,
    brand: str | None = None,
) -> list[PreviewEntry]:
    """Render every supported lang of a recipe into preview PNG entries.

    Pipeline per lang:
      1. `scrub_recipe_for_preview` replaces all narrative content (incl.
         SVG <text> labels) with placeholders / lorem ipsum
      2. compose() builds the same HTML the renderer uses for PDF
      3. WeasyPrint renders to PDF
      4. pypdfium2 rasterizes the first `PREVIEW_MAX_PAGES` to PNG

    Returns an empty list if the recipe declares no `en`/`ar` language.
    """
    name = recipe["name"]
    entries: list[PreviewEntry] = []

    with tempfile.TemporaryDirectory(prefix="katib-preview-") as tmp:
        tmp_dir = Path(tmp)
        for lang in _supported_langs(recipe):
            scrubbed = scrub_recipe_for_preview(recipe, lang=lang)
            yaml_path = tmp_dir / f"{name}.{lang}.yaml"
            yaml_path.write_text(
                yaml.safe_dump(scrubbed, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            page_pngs = _render_one_lang(
                yaml_path, lang=lang, brand=brand, pdf_dir=tmp_dir
            )
            entries.extend(
                _entries_for(name=name, kind="recipe", lang=lang, page_pngs=page_pngs)
            )

    return entries


# Rich HTML default for slot-style string inputs (fields named *_html or
# whose description signals "trusted HTML"). The scrubber's HTML path
# preserves tag structure and replaces narrative text with lorem-style
# fill, so passing a structured block in produces a structured block out
# rather than a flat `[Field]` label sitting on an empty page.
_HTML_SLOT_DEFAULT_EN = (
    "<h3>Lorem ipsum dolor sit amet</h3>"
    "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.</p>"
    "<p>Duis aute irure dolor in reprehenderit in voluptate velit esse "
    "cillum dolore eu fugiat nulla pariatur.</p>"
    "<ul>"
    "<li>Lorem ipsum dolor sit amet</li>"
    "<li>Consectetur adipiscing elit</li>"
    "<li>Sed do eiusmod tempor incididunt</li>"
    "</ul>"
)
_HTML_SLOT_DEFAULT_AR = (
    "<h3>لوريم إيبسوم دولور سيت أميت</h3>"
    "<p>لوريم إيبسوم دولور سيت أميت، كونسيكتيتور أديبيسسينج إليت. "
    "سيد دو إيوسمود تيمبور إنكيديدونت أوت لابوري إت دولوري ماجنا "
    "أليكوا. أوت إنيم أد مينيم فينيام، كويس نوسترود إكسيرسيتيشن.</p>"
    "<p>دويس أوتي إيروري دولور إن ريبريهيندريت إن فولوبتاتي فيليت "
    "إسسي كيلوم دولوري إيو فوجيات نولا باريتور.</p>"
    "<ul>"
    "<li>لوريم إيبسوم دولور سيت أميت</li>"
    "<li>كونسيكتيتور أديبيسسينج إليت</li>"
    "<li>سيد دو إيوسمود تيمبور إنكيديدونت</li>"
    "</ul>"
)


def _is_html_slot(field: str, spec: dict) -> bool:
    if field.endswith("_html") or field == "html":
        return True
    desc = (spec.get("description") or "").lower()
    return "trusted html" in desc or "html content" in desc


def _image_stub_for(spec: dict, *, image_path: Path, component_name: str) -> dict:
    """Pick an image-input stub that satisfies the spec's `sources_accepted`.

    Most components accept `user-file` (the synthesized neutral SVG path
    is then resolved through the standard image pipeline). Chart
    components only accept `inline-svg` — those need a minimal chart
    spec instead. Component name picks the chart shape (chart-bar →
    bar, chart-donut → donut, chart-sparkline → sparkline) so the spec
    matches what the inline-svg provider expects.
    """
    sources = spec.get("sources_accepted") or ["user-file"]
    if "user-file" in sources:
        return {"source": "user-file", "path": str(image_path)}
    if "inline-svg" in sources:
        if "sparkline" in component_name:
            return {
                "source": "inline-svg",
                "type": "sparkline",
                "data": [10, 12, 8, 14, 11, 16, 13],
            }
        chart_type = "bar" if "bar" in component_name else "donut"
        return {
            "source": "inline-svg",
            "type": chart_type,
            "data": [
                {"label": "A", "value": 3},
                {"label": "B", "value": 2},
                {"label": "C", "value": 1},
            ],
        }
    # url / gemini / screenshot — fall back to user-file. compose() may
    # still fail validation, but that's strictly better than silently
    # dropping a required image input.
    return {"source": "user-file", "path": str(image_path)}


def _synthesize_wrapper_recipe(component_meta: dict, *, image_path: Path) -> dict:
    """Build a one-section recipe that wraps a component for previewing.

    Inputs are minimal placeholders that the scrubber will replace with
    `[Field]` labels. Image inputs receive a stub picked from the
    component's `sources_accepted` (file path for user-file, minimal
    chart spec for inline-svg-only components like chart-bar). Slot-
    style string inputs (fields ending `_html` or whose description
    signals trusted HTML) get a structured lorem block so the
    scrubber's HTML path produces a populated page rather than a flat
    `[Field]` label on whitespace.
    """
    name = component_meta["name"]
    declared_langs = component_meta.get("languages") or ["en"]
    accepts = component_meta.get("accepts", {}).get("inputs") or []

    inputs_en: dict = {}
    inputs_ar: dict = {}
    for entry in accepts:
        # Each `accepts.inputs[]` element is a single-key dict like
        #   {"title": {"type": "string", "required": true, ...}}
        if not isinstance(entry, dict):
            continue
        for field, spec in entry.items():
            spec = spec or {}
            t = (spec.get("type") or "string").lower()
            if t == "image":
                stub = _image_stub_for(
                    spec, image_path=image_path, component_name=name
                )
                inputs_en[field] = dict(stub)
                inputs_ar[field] = dict(stub)
            elif t in ("number", "integer", "int", "float"):
                inputs_en[field] = 1
                inputs_ar[field] = 1
            elif t in ("list", "array"):
                inputs_en[field] = ["Sample item"] * 3
                inputs_ar[field] = ["عنصر"] * 3
            elif t in ("dict", "object"):
                inputs_en[field] = {"sample": "value"}
                inputs_ar[field] = {"sample": "قيمة"}
            elif t == "bool" or t == "boolean":
                # Booleans aren't scrubbed — pass through as-is.
                inputs_en[field] = spec.get("default", True)
                inputs_ar[field] = spec.get("default", True)
            elif _is_html_slot(field, spec):
                inputs_en[field] = _HTML_SLOT_DEFAULT_EN
                inputs_ar[field] = _HTML_SLOT_DEFAULT_AR
            else:  # "string" and any unknown type
                inputs_en[field] = "Sample text content goes here"
                inputs_ar[field] = "نص نموذجي يظهر هنا"

    return {
        "name": f"{name}-preview",
        "version": "0.0.0",
        "namespace": "katib",
        "languages": declared_langs,
        "description": f"Preview wrapper for component {name}",
        "sections": [
            {
                "component": name,
                "inputs_by_lang": {"en": inputs_en, "ar": inputs_ar},
            }
        ],
    }


def render_component_previews(
    component: dict,
    *,
    brand: str | None = None,
) -> list[PreviewEntry]:
    """Render every supported lang of a component into preview PNG entries.

    Wraps the component in a synthesized one-section recipe with placeholder
    inputs (text fields → `[Field]` placeholders, image fields → neutral SVG
    stub), then runs through the same scrub → compose → PDF → PNG pipeline
    as recipe previews. The marketplace shows the result as if the
    component had been used in a real document.
    """
    name = component["name"]
    entries: list[PreviewEntry] = []

    with tempfile.TemporaryDirectory(prefix="katib-cpreview-") as tmp:
        tmp_dir = Path(tmp)

        # Write the placeholder SVG to a file so resolved_path resolves
        # for components that prefer file-backed image inputs.
        image_path = tmp_dir / "placeholder.svg"
        image_path.write_text(_PLACEHOLDER_IMAGE_SVG, encoding="utf-8")

        wrapper = _synthesize_wrapper_recipe(component, image_path=image_path)

        for lang in _supported_langs(component):
            scrubbed = scrub_recipe_for_preview(wrapper, lang=lang)
            yaml_path = tmp_dir / f"{name}-wrap.{lang}.yaml"
            yaml_path.write_text(
                yaml.safe_dump(scrubbed, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            page_pngs = _render_one_lang(
                yaml_path, lang=lang, brand=brand, pdf_dir=tmp_dir
            )
            entries.extend(
                _entries_for(name=name, kind="component", lang=lang, page_pngs=page_pngs)
            )

    return entries
