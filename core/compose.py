"""Recipe composition: recipe YAML -> single HTML document.

Phase 1 responsibilities:
    1. Load recipe YAML, validate against recipe schema
    2. For each section, resolve component directory (core only in Phase 1)
    3. Load component.yaml, validate against component schema
    4. Check recipe language is supported by each referenced component
    5. Render the lang-appropriate Jinja template with tokens + inputs context
    6. Concatenate section HTML; wrap in a minimal page shell with token CSS

Phase 2+ will extend compose.py with:
    - Brand/user/core component resolution order
    - Image provider resolution (components declaring `type: image` inputs)
    - Audit-log presence check at startup
    - Capability-index usage
"""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from jsonschema import Draft202012Validator

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
    return Environment(
        loader=FileSystemLoader(str(COMPONENTS_DIR)),
        undefined=StrictUndefined,
        autoescape=select_autoescape(enabled_extensions=("html", "htm"), default=True),
        keep_trailing_newline=True,
    )


def compose(
    recipe_name: str,
    lang: str,
    brand: str | None = None,
    overrides: dict[str, Any] | None = None,
) -> tuple[str, dict]:
    recipe = load_recipe(recipe_name)
    _check_lang_supported(recipe, lang)

    base = load_base_tokens()
    brand_data = load_brand(brand) if brand else None
    merged = merge_tokens(base, brand_data, overrides)
    ctx = render_context(merged, lang)

    env = _jinja_env()
    body_parts: list[str] = []
    style_parts: list[str] = []
    seen_components: set[str] = set()

    for idx, section in enumerate(recipe["sections"]):
        comp_name = section["component"]
        comp = load_component(comp_name)
        _check_component_supports_lang(comp, lang)

        tier = comp["tier"]
        template_rel = f"{TIER_DIRS[tier]}/{comp_name}/{lang}.html"
        template = env.get_template(template_rel)

        inputs = section.get("inputs", {}) or {}
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

        if comp_name not in seen_components:
            seen_components.add(comp_name)
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
.katib-section {{ margin-bottom: 1.2em; }}
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
