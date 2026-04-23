"""Recipe composition: recipe YAML -> single HTML document.

Responsibilities:
    1. Load recipe YAML, validate against recipe schema
    2. For each section, resolve component directory (core only in Phase 1-2)
    3. Load component.yaml, validate against component schema
    4. Check recipe language is supported by each referenced component
    5. Resolve any `type: image` inputs through the provider layer
    6. Render the lang-appropriate Jinja template with tokens + inputs context
    7. Concatenate section HTML; wrap in a minimal page shell with token CSS

Phase 3+ will add:
    - Brand/user/core component resolution order
    - Audit-log presence check at startup
    - Capability-index usage
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, Undefined, select_autoescape
from jsonschema import Draft202012Validator

from core.image.base import Provider, default_providers, resolve_image
from core.output import resolve_cache_dir
from core.tokens import (
    load_base_tokens,
    load_brand,
    merge_tokens,
    render_context,
    tokens_css,
)

CORE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CORE_DIR.parent
COMPONENTS_DIR = REPO_ROOT / "components"
RECIPES_DIR = REPO_ROOT / "recipes"
SCHEMAS_DIR = REPO_ROOT / "schemas"

TIER_DIRS = {"primitive": "primitives", "section": "sections", "cover": "covers"}


class ComposeError(ValueError):
    pass


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def load_recipe(name_or_path: str) -> dict:
    p = Path(name_or_path).expanduser()
    if p.suffix in (".yaml", ".yml") and p.exists():
        path = p
    else:
        path = RECIPES_DIR / f"{name_or_path}.yaml"
        if not path.exists():
            raise FileNotFoundError(
                f"recipe {name_or_path!r} not found (looked at {path})"
            )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    validator = Draft202012Validator(_load_schema("recipe.yaml.schema.json"))
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        msg = "\n  ".join(f"{list(e.path)}: {e.message}" for e in errors)
        raise ComposeError(f"recipe {path.name} failed schema validation:\n  {msg}")
    data["__path__"] = str(path)
    return data


def _resolve_component_dir(name: str) -> Path:
    for tier_dirname in TIER_DIRS.values():
        candidate = COMPONENTS_DIR / tier_dirname / name
        if (candidate / "component.yaml").exists():
            return candidate
    raise FileNotFoundError(
        f"component {name!r} not found under {COMPONENTS_DIR}. "
        f"Expected one of: "
        + ", ".join(
            f"{COMPONENTS_DIR / t / name}/component.yaml" for t in TIER_DIRS.values()
        )
    )


def load_component(name: str) -> dict:
    cdir = _resolve_component_dir(name)
    data = yaml.safe_load((cdir / "component.yaml").read_text(encoding="utf-8")) or {}
    validator = Draft202012Validator(_load_schema("component.yaml.schema.json"))
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        msg = "\n  ".join(f"{list(e.path)}: {e.message}" for e in errors)
        raise ComposeError(f"component {name} failed schema validation:\n  {msg}")
    data["__dir__"] = str(cdir)
    return data


def _check_lang_supported(recipe: dict, lang: str) -> None:
    langs = recipe.get("languages", [])
    if lang not in langs:
        raise ComposeError(
            f"recipe {recipe['name']!r} declares languages {langs}; "
            f"requested render lang {lang!r} is not supported"
        )


def _check_component_supports_lang(comp: dict, lang: str) -> None:
    langs = comp.get("languages", [])
    if lang not in langs:
        raise ComposeError(
            f"component {comp['name']!r} declares languages {langs}; "
            f"requested render lang {lang!r} is not supported"
        )


def _jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(COMPONENTS_DIR)),
        undefined=Undefined,
        autoescape=select_autoescape(enabled_extensions=("html", "htm"), default=True),
        keep_trailing_newline=True,
    )
    # `{{ input.items }}` must resolve to the 'items' KEY of the inputs dict,
    # not dict.items() method. Jinja's default getattr tries attribute first;
    # override to prefer item-lookup for mapping access. When a dict key is
    # missing, return env.undefined (not the dict's bound method) so template
    # `{%- if input.missing %}` checks evaluate falsy instead of truthy-on-method.
    original_getattr = env.getattr

    def _getattr_item_first(obj: Any, attribute: Any) -> Any:
        if isinstance(obj, dict):
            try:
                return obj[attribute]
            except KeyError:
                return env.undefined(name=attribute)
        try:
            return obj[attribute]
        except (TypeError, LookupError):
            return original_getattr(obj, attribute)

    env.getattr = _getattr_item_first
    return env


def _load_primitive_styles() -> list[str]:
    primitives_dir = COMPONENTS_DIR / "primitives"
    if not primitives_dir.exists():
        return []
    out: list[str] = []
    for pdir in sorted(primitives_dir.iterdir()):
        styles_file = pdir / "styles.css"
        if styles_file.exists():
            out.append(
                f"/* primitive: {pdir.name} */\n"
                f"{styles_file.read_text(encoding='utf-8')}"
            )
    return out


def _image_input_specs(comp: dict) -> dict[str, dict]:
    """Extract {input_name: decl} for inputs declared as `type: image`.

    Accepts both YAML shapes the schema permits:
        - {image: {type: image, required: true, sources_accepted: [...]}}
        - {name: image, type: image, required: true, sources_accepted: [...]}
    """
    out: dict[str, dict] = {}
    for entry in comp.get("accepts", {}).get("inputs", []) or []:
        if not isinstance(entry, dict):
            continue
        if "type" in entry and "name" in entry:
            if entry["type"] == "image":
                out[entry["name"]] = entry
            continue
        if len(entry) == 1:
            name, decl = next(iter(entry.items()))
            if isinstance(decl, dict) and decl.get("type") == "image":
                out[name] = decl
    return out


def _resolve_image_slots(
    inputs: dict,
    image_decls: dict[str, dict],
    cache_dir: Path,
    providers: dict[str, Provider],
    comp_name: str,
    tokens: dict | None = None,
    lang: str | None = None,
) -> dict:
    if not image_decls:
        return inputs
    resolved = dict(inputs)
    charts_cfg = (tokens or {}).get("charts", {}) or {}
    palette = charts_cfg.get("palette") or []
    axis_color = charts_cfg.get("axis_color")
    for slot_name, decl in image_decls.items():
        if slot_name not in inputs:
            if decl.get("required"):
                raise ComposeError(
                    f"component {comp_name!r}: required image input "
                    f"{slot_name!r} not supplied by recipe"
                )
            continue
        value = inputs[slot_name]
        if not isinstance(value, dict):
            raise ComposeError(
                f"component {comp_name!r}: input {slot_name!r} is type:image; "
                f"expected dict {{'source': '...', ...}}, got {type(value).__name__}"
            )
        if value.get("source") == "inline-svg":
            value = dict(value)
            if "colors" not in value and palette:
                value["colors"] = list(palette)
            if "lang" not in value and lang:
                value["lang"] = lang
            if "axis_color" not in value and axis_color:
                value["axis_color"] = axis_color
        img = resolve_image(
            value,
            cache_dir,
            providers,
            sources_accepted=decl.get("sources_accepted"),
        )
        resolved[slot_name] = {
            "resolved_path": str(img.path) if img.path else None,
            "resolved_svg": img.inline_svg,
            "content_hash": img.content_hash,
            "alt": img.alt_hint or value.get("alt_text") or "",
            "source": value.get("source"),
            "spec": value,
        }
    return resolved


def compose(
    recipe_name: str,
    lang: str,
    brand: str | None = None,
    overrides: dict[str, Any] | None = None,
    providers: dict[str, Provider] | None = None,
    image_cache_dir: Path | None = None,
) -> tuple[str, dict]:
    recipe = load_recipe(recipe_name)
    _check_lang_supported(recipe, lang)

    base = load_base_tokens()
    brand_data = load_brand(brand) if brand else None
    merged = merge_tokens(base, brand_data, overrides)
    ctx = render_context(merged, lang)

    providers = providers if providers is not None else default_providers()
    cache_dir = image_cache_dir or resolve_cache_dir("images")

    env = _jinja_env()
    body_parts: list[str] = []
    style_parts: list[str] = _load_primitive_styles()
    seen_non_primitive: set[str] = set()

    for idx, section in enumerate(recipe["sections"]):
        comp_name = section["component"]
        comp = load_component(comp_name)
        _check_component_supports_lang(comp, lang)

        tier = comp["tier"]
        template_rel = f"{TIER_DIRS[tier]}/{comp_name}/{lang}.html"
        template = env.get_template(template_rel)

        inputs = section.get("inputs", {}) or {}
        image_decls = _image_input_specs(comp)
        inputs = _resolve_image_slots(
            inputs, image_decls, cache_dir, providers, comp_name,
            tokens=merged, lang=lang,
        )

        rendered = template.render(
            **ctx,
            input=inputs,
            inputs=inputs,
            variant=section.get("variant"),
            component={"name": comp_name, "tier": tier, "version": comp["version"]},
        )
        body_parts.append(
            f"<!-- section[{idx}]: {comp_name} -->\n{rendered.rstrip()}\n"
        )

        if tier != "primitive" and comp_name not in seen_non_primitive:
            seen_non_primitive.add(comp_name)
            styles_file = Path(comp["__dir__"]) / "styles.css"
            if styles_file.exists():
                style_parts.append(
                    f"/* {comp_name} */\n{styles_file.read_text(encoding='utf-8')}"
                )

    page_html = _wrap_page(
        body="\n".join(body_parts),
        token_css=tokens_css(merged),
        component_css="\n\n".join(style_parts),
        lang=lang,
        direction=ctx["dir"],
        fonts=ctx["fonts"],
        title=recipe.get("description") or recipe["name"],
    )

    return page_html, {"recipe": recipe, "tokens": merged, "ctx": ctx}


def _wrap_page(
    *,
    body: str,
    token_css: str,
    component_css: str,
    lang: str,
    direction: str,
    fonts: dict,
    title: str,
) -> str:
    primary = fonts.get("primary") or "system-ui"
    display = fonts.get("display") or primary
    fallback = fonts.get("fallback") or "sans-serif"
    safe_title = html.escape(title, quote=True)

    font_vars = (
        f'    --font-primary: "{primary}", {fallback};\n'
        f'    --font-display: "{display}", {fallback};\n'
    )
    token_css_with_fonts = token_css.replace(
        "}", font_vars + "}", 1
    ) if token_css.endswith("}") else token_css

    base_css = f"""
@page {{
    size: A4;
    margin: 20mm;
    background: var(--page-bg);
}}
html, body {{
    background: var(--page-bg);
    color: var(--text);
    margin: 0;
    padding: 0;
}}
body {{
    font-family: var(--font-primary);
    direction: {direction};
    font-size: 11pt;
    line-height: 1.6;
}}

h1, h2, h3, h4 {{
    font-family: var(--font-display);
    line-height: 1.25;
    margin: 1em 0 0.4em 0;
    color: var(--text);
}}
h1 {{ font-size: 22pt; font-weight: 700; }}
h2 {{ font-size: 15pt; font-weight: 700; }}
h3 {{ font-size: 12pt; font-weight: 700; }}
h4 {{ font-size: 11pt; font-weight: 700; }}

p {{ margin: 0.5em 0; }}

ul, ol {{
    margin: 0.6em 0;
    padding-left: 1.4em;
}}
[dir="rtl"] ul,
[dir="rtl"] ol {{
    padding-left: 0;
    padding-right: 1.4em;
}}
li {{ margin: 0.3em 0; }}

code {{
    font-family: var(--font-mono, "JetBrains Mono", monospace);
    background: var(--code-bg);
    color: var(--code-fg);
    padding: 1pt 4pt;
    border-radius: 2pt;
    font-size: 9.5pt;
}}

a {{ color: var(--accent); text-decoration: none; }}

.katib-section {{
    margin-bottom: 1.4em;
    page-break-inside: avoid;
}}
""".strip()

    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="utf-8">
<title>{safe_title}</title>
<style>
{token_css_with_fonts}

{base_css}

{component_css}
</style>
</head>
<body>
{body}
</body>
</html>
"""
