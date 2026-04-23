"""Token resolution for Katib v2.

Layered merge (lowest to highest priority):
    1. core/tokens.base.yaml        shipped defaults
    2. brands/<brand>.yaml           brand profile (repo or ~/.katib/brands/)
    3. render-time overrides         CLI flags / recipe overrides

Public API:
    load_base_tokens() -> dict
    load_brand(name_or_path) -> dict | None
    merge_tokens(base, brand, overrides=None) -> dict
    render_context(tokens, lang) -> dict      template context vars
    tokens_css(tokens) -> str                  `:root { --accent: ...; }` block

Validations at load time (ported from v1 brand.py):
    - color values match CSS whitelist (#hex, rgb/hsl, named) -> blocks injection
    - logo.primary must exist on disk if set
    - logo.max_height_mm in [1, 200]
    - identity fields resolve per-language (en / ar) with fallback
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

CORE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CORE_DIR.parent
BASE_TOKENS_FILE = CORE_DIR / "tokens.base.yaml"
REPO_BRANDS_DIR = REPO_ROOT / "brands"

USER_BRANDS_DIR_ENV = "KATIB_BRANDS_DIR"
DEFAULT_USER_BRANDS_DIR = Path.home() / ".katib" / "brands"

_COLOR_PATTERNS = (
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),
    re.compile(r"^rgba?\(\s*[\d.,\s%/]+\s*\)$"),
    re.compile(r"^hsla?\(\s*[\d.,\s%/deg]+\s*\)$"),
    re.compile(r"^[a-zA-Z][a-zA-Z0-9-]*$"),
)
_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
_LOGO_HEIGHT_RANGE = (1, 200)


class TokenError(ValueError):
    """Raised when a base token file, brand profile, or merged token set is invalid."""


def _validate_color(key: str, val: Any) -> str:
    if not isinstance(val, str):
        raise TokenError(f"colors.{key} must be a string, got {type(val).__name__}")
    for pat in _COLOR_PATTERNS:
        if pat.match(val):
            return val
    raise TokenError(
        f"colors.{key} = {val!r} is not a recognized CSS color "
        f"(accepted: #hex, rgb()/rgba(), hsl()/hsla(), or a named color)"
    )


def _user_brands_dir() -> Path:
    env = os.environ.get(USER_BRANDS_DIR_ENV)
    return Path(env).expanduser() if env else DEFAULT_USER_BRANDS_DIR


def load_base_tokens() -> dict[str, Any]:
    with BASE_TOKENS_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    colors = data.get("colors", {})
    for key, val in list(colors.items()):
        colors[key] = _validate_color(key, val)
    return data


def _resolve_brand_path(name_or_path: str) -> Path:
    p = Path(name_or_path).expanduser()
    if p.suffix in (".yaml", ".yml") and p.exists():
        return p.resolve()
    tried: list[str] = []
    for base in (_user_brands_dir(), REPO_BRANDS_DIR):
        for ext in (".yaml", ".yml"):
            candidate = base / f"{name_or_path}{ext}"
            tried.append(str(candidate))
            if candidate.exists():
                return candidate.resolve()
    raise TokenError(
        f"Brand profile {name_or_path!r} not found. Tried:\n  "
        + "\n  ".join(tried)
    )


def load_brand(name_or_path: str | None) -> dict[str, Any] | None:
    if not name_or_path:
        return None
    path = _resolve_brand_path(name_or_path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data["__source_path__"] = str(path)

    name = data.get("name")
    if not name or (isinstance(name, str) and not name.strip()):
        raise TokenError(f"{path}: `name` is required (string or {{en, ar}} dict)")

    colors = data.get("colors", {})
    if colors and not isinstance(colors, dict):
        raise TokenError(f"{path}: `colors` must be a mapping")
    for key, val in list(colors.items()):
        colors[key] = _validate_color(key, val)

    logo = data.get("logo")
    if isinstance(logo, str):
        logo = {"primary": logo}
        data["logo"] = logo
    if isinstance(logo, dict):
        primary = logo.get("primary")
        if primary:
            logo_path = Path(primary).expanduser()
            if not logo_path.is_absolute():
                logo_path = path.parent / logo_path
            if not logo_path.exists():
                raise TokenError(f"{path}: logo.primary not found at {logo_path}")
            if logo_path.suffix.lower() not in _LOGO_EXTENSIONS:
                raise TokenError(
                    f"{path}: logo.primary {logo_path.suffix!r} not in "
                    f"{sorted(_LOGO_EXTENSIONS)}"
                )
            logo["primary"] = str(logo_path.resolve())
        max_h = logo.get("max_height_mm", 18)
        if not isinstance(max_h, int) or not (
            _LOGO_HEIGHT_RANGE[0] <= max_h <= _LOGO_HEIGHT_RANGE[1]
        ):
            raise TokenError(
                f"{path}: logo.max_height_mm must be int in "
                f"[{_LOGO_HEIGHT_RANGE[0]}, {_LOGO_HEIGHT_RANGE[1]}]"
            )

    return data


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for k, v in override.items():
        if k.startswith("__"):
            continue
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = _deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def merge_tokens(
    base: dict[str, Any],
    brand: dict[str, Any] | None = None,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged = dict(base)
    if brand:
        merged = _deep_merge(merged, brand)
    if overrides:
        merged = _deep_merge(merged, overrides)
    return merged


def _lang_field(value: Any, lang: str, fallback_lang: str = "en") -> str:
    if isinstance(value, dict):
        if lang in value and value[lang]:
            return value[lang]
        if fallback_lang in value and value[fallback_lang]:
            return value[fallback_lang]
        return ""
    return value if isinstance(value, str) else ""


def render_context(tokens: dict[str, Any], lang: str) -> dict[str, Any]:
    identity_raw = tokens.get("identity", {}) or {}
    identity: dict[str, str] = {}
    seen_bases: set[str] = set()
    for key, val in identity_raw.items():
        if key.endswith("_ar"):
            continue
        seen_bases.add(key)
        if lang == "ar":
            ar_sibling = identity_raw.get(f"{key}_ar")
            if ar_sibling:
                identity[key] = ar_sibling
                continue
        identity[key] = _lang_field(val, lang)

    fonts_block = tokens.get("fonts", {}) or {}
    fonts = fonts_block.get(lang, fonts_block.get("en", {})) or {}

    name_val = tokens.get("name", "")
    name = _lang_field(
        {"en": tokens.get("name", ""), "ar": tokens.get("name_ar", "")},
        lang,
    ) if isinstance(name_val, str) else _lang_field(name_val, lang)

    return {
        "colors": tokens.get("colors", {}),
        "fonts": fonts,
        "identity": identity,
        "logo": tokens.get("logo", {}) or {},
        "name": name,
        "legal_name": _lang_field(
            {
                "en": tokens.get("legal_name", ""),
                "ar": tokens.get("legal_name_ar", ""),
            },
            lang,
        ),
        "lang": lang,
        "dir": "rtl" if lang == "ar" else "ltr",
    }


_COLOR_KEY_TO_VAR = {
    "page_bg": "--page-bg",
    "text": "--text",
    "text_secondary": "--text-secondary",
    "text_tertiary": "--text-tertiary",
    "accent": "--accent",
    "accent_2": "--accent-2",
    "accent_on": "--accent-on",
    "border": "--border",
    "border_strong": "--border-strong",
    "tag_bg": "--tag-bg",
    "tag_fg": "--tag-fg",
    "code_bg": "--code-bg",
    "code_fg": "--code-fg",
    "callout_info_bg": "--callout-info-bg",
    "callout_info_accent": "--callout-info-accent",
    "callout_warn_bg": "--callout-warn-bg",
    "callout_warn_accent": "--callout-warn-accent",
    "callout_danger_bg": "--callout-danger-bg",
    "callout_danger_accent": "--callout-danger-accent",
    "callout_tip_bg": "--callout-tip-bg",
    "callout_tip_accent": "--callout-tip-accent",
    "step_circle_bg": "--step-circle-bg",
    "step_circle_fg": "--step-circle-fg",
}


def tokens_css(tokens: dict[str, Any]) -> str:
    colors = tokens.get("colors", {}) or {}
    lines = [":root {"]
    for key, val in colors.items():
        var = _COLOR_KEY_TO_VAR.get(key, f"--{key.replace('_', '-')}")
        lines.append(f"    {var}: {val};")
    lines.append("}")
    return "\n".join(lines)
