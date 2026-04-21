#!/usr/bin/env python3
"""Katib brand profile loader + token merge.

A brand profile lives at `~/.katib/brands/<name>.yaml` (per-user) or at
`<skill>/brands/<name>.yaml` (shipped). Per-user overrides skill. A brand
profile merges into domain tokens so a single domain (business-proposal,
tutorial) can render with any brand's colors, fonts, and identity without
forking templates.

Public API:
    load_brand(name_or_path, skill_brands_dir) -> dict
    apply_brand_to_tokens(tokens, brand) -> dict            # mutates copy
    brand_context_vars(brand, lang) -> dict                 # template vars

Precedence (most specific wins):
    domain tokens.json → brand profile → CLI flags

Validations at load time (v1.3):
- `name` must be present and non-empty (string or bilingual dict)
- colors must match a known CSS color syntax (blocks CSS injection)
- `logo.primary` must exist on disk if set
- `logo.max_height_mm` must be an integer in [1, 200]

Bilingual fallback (v1.3): `name`, `legal_name`, and every `identity.*`
field resolve per-language, with `*_ar` siblings and `{en, ar}` dicts both
supported. Falls back to EN if AR missing.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

USER_BRANDS_DIR_ENV = "KATIB_BRANDS_DIR"
DEFAULT_USER_BRANDS_DIR = Path.home() / ".katib" / "brands"

# Human-friendly brand color keys → CSS variable names used by templates.
# Templates read `--accent` etc. from tokens_css; brand authors write
# `accent`, `accent_secondary` etc. for ergonomics.
COLOR_KEY_MAP = {
    "accent": "--accent",
    "accent_secondary": "--accent-2",
    "accent_on": "--accent-on",
    "text": "--text",
    "text_secondary": "--text-secondary",
    "text_tertiary": "--text-tertiary",
    "page_bg": "--page-bg",
    "border": "--border",
    "border_strong": "--border-strong",
    "tag_bg": "--tag-bg",
    "tag_fg": "--tag-fg",
    "code_bg": "--code-bg",
    "code_fg": "--code-fg",
}

# Color value shapes we accept. Positive whitelist — anything falling outside
# these patterns (semicolons, braces, comments, newlines, url()) is rejected
# before it reaches the CSS output, which would otherwise be injection-prone
# since tokens land in a raw `:root { --accent: <val>; }` block.
_COLOR_PATTERNS = (
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),
    re.compile(r"^rgba?\(\s*[\d.,\s%/]+\s*\)$"),
    re.compile(r"^hsla?\(\s*[\d.,\s%/deg]+\s*\)$"),
    re.compile(r"^[a-zA-Z]+$"),                     # named colors (navy, gold, transparent)
)
_LOGO_HEIGHT_MIN_MM = 1
_LOGO_HEIGHT_MAX_MM = 200
_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}


class BrandError(ValueError):
    """Raised when a brand profile can't be loaded or is malformed."""


def _validate_color(raw_key: str, val: str) -> str:
    for pat in _COLOR_PATTERNS:
        if pat.match(val):
            return val
    raise BrandError(
        f"brand.colors.{raw_key} = {val!r} is not a recognized CSS color "
        f"(accepted: #hex, rgb()/rgba(), hsl()/hsla(), or a named color)"
    )


def user_brands_dir() -> Path:
    env = os.environ.get(USER_BRANDS_DIR_ENV)
    return Path(env).expanduser() if env else DEFAULT_USER_BRANDS_DIR


def _resolve_brand_path(name_or_path: str, skill_brands_dir: Path) -> Path:
    p = Path(name_or_path).expanduser()
    if p.suffix in (".yaml", ".yml") and p.exists():
        return p.resolve()
    tried: list[str] = []
    for base in (user_brands_dir(), skill_brands_dir):
        for ext in (".yaml", ".yml"):
            candidate = base / f"{name_or_path}{ext}"
            tried.append(str(candidate))
            if candidate.exists():
                return candidate.resolve()
    raise BrandError(
        f"brand profile not found: {name_or_path!r}\n"
        f"  searched:\n    " + "\n    ".join(tried)
    )


def load_brand(name_or_path: str, skill_brands_dir: Path) -> dict:
    """Load and shallow-validate a brand profile."""
    path = _resolve_brand_path(name_or_path, skill_brands_dir)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise BrandError(f"brand profile is not valid YAML: {path}: {e}") from e
    if not isinstance(data, dict):
        raise BrandError(f"brand profile must be a YAML mapping: {path}")
    name_val = data.get("name")
    if not name_val or (isinstance(name_val, dict) and not any(name_val.values())):
        raise BrandError(
            f"brand profile requires a non-empty `name` field: {path}\n"
            f"  use a string (e.g. `name: Acme Corp`) or a mapping "
            f"(e.g. `name: {{en: Acme, ar: أكمي}}`)"
        )
    data["_path"] = str(path)
    data["_resolved_logo"] = _resolve_logo(data.get("logo"), path.parent)
    return data


def _resolve_logo(logo_spec: Any, brand_dir: Path) -> dict:
    """Normalize a logo spec into {primary, max_height_mm}.

    Accepts:
      logo: path/to/logo.png                # bare string
      logo: {primary: "...", max_height_mm: 20}
    Paths resolve relative to the brand file's directory. Missing files fail
    at load time rather than mid-render. Dark-background logo variants are
    a v1.2 consideration — current templates render `primary` uniformly.
    """
    if not logo_spec:
        return {"primary": "", "max_height_mm": 18}
    if isinstance(logo_spec, str):
        logo_spec = {"primary": logo_spec}
    if not isinstance(logo_spec, dict):
        raise BrandError(f"brand.logo must be a string or mapping, got {type(logo_spec).__name__}")

    raw = logo_spec.get("primary")
    primary = ""
    if raw:
        p = Path(str(raw)).expanduser()
        if not p.is_absolute():
            p = (brand_dir / p).resolve()
        if not p.exists():
            raise BrandError(
                f"brand.logo.primary points to missing file: {p}\n"
                f"  (relative paths resolve against the brand file's directory: {brand_dir})"
            )
        if p.suffix.lower() not in _LOGO_EXTENSIONS:
            raise BrandError(
                f"brand.logo.primary must be one of {sorted(_LOGO_EXTENSIONS)} "
                f"(got {p.suffix!r}: {p})"
            )
        primary = p.as_uri()

    raw_height = logo_spec.get("max_height_mm")
    if raw_height in (None, ""):
        height = 18
    else:
        try:
            height = int(raw_height)
        except (TypeError, ValueError):
            raise BrandError(
                f"brand.logo.max_height_mm must be an integer (mm), got {raw_height!r}. "
                f"Write it without units: `max_height_mm: 18` (not `18mm`)."
            )
    if not (_LOGO_HEIGHT_MIN_MM <= height <= _LOGO_HEIGHT_MAX_MM):
        raise BrandError(
            f"brand.logo.max_height_mm must be between "
            f"{_LOGO_HEIGHT_MIN_MM} and {_LOGO_HEIGHT_MAX_MM} mm (got {height})"
        )
    return {"primary": primary, "max_height_mm": height}


def list_brands(skill_brands_dir: Path) -> list[dict]:
    """Enumerate brand profiles across user + skill dirs.

    Returns dicts with {name, display, location, path}. `display` is the
    `name` field from inside the YAML (for table output); `name` is the
    stem used with `--brand`. User dir shadows skill dir (same stem wins).
    """
    seen: dict[str, dict] = {}
    for location, base in (("user", user_brands_dir()), ("skill", skill_brands_dir)):
        if not base.exists():
            continue
        candidates = sorted(list(base.glob("*.yaml")) + list(base.glob("*.yml")))
        for p in candidates:
            stem = p.stem
            if stem in seen:
                continue  # user already took precedence
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                display = data.get("name", "(missing name)") if isinstance(data, dict) else "(invalid)"
            except yaml.YAMLError:
                display = "(yaml error)"
            seen[stem] = {
                "name": stem,
                "display": display,
                "location": location,
                "path": str(p),
            }
    return list(seen.values())


def apply_brand_to_tokens(tokens: dict[str, Any], brand: dict | None) -> dict[str, Any]:
    """Return a new tokens dict with brand overrides applied.

    Brand color keys accept both the human-friendly form (`accent`) and the
    raw CSS variable form (`--accent`); both land in the same place. Font
    overrides replace whichever of `fonts.en` / `fonts.ar` the brand sets,
    leaving the other language's defaults intact.
    """
    merged = {k: (dict(v) if isinstance(v, dict) else v) for k, v in tokens.items()}
    if not brand:
        return merged

    # Colors → semantic_colors
    semantic = dict(merged.get("semantic_colors") or {})
    for raw_key, val in (brand.get("colors") or {}).items():
        css_key = raw_key if raw_key.startswith("--") else COLOR_KEY_MAP.get(raw_key)
        if css_key is None:
            # Unknown key: warn to stderr so the author notices, then skip.
            # Prior behaviour was silent drop which hid typos (`acent: ...`).
            import sys
            known = ", ".join(sorted(COLOR_KEY_MAP.keys()))
            print(
                f"⚠ brand.colors.{raw_key} is not a recognized color key — ignored. "
                f"Known keys: {known}",
                file=sys.stderr,
            )
            continue
        if not isinstance(val, (str, int, float)) or isinstance(val, bool):
            raise BrandError(
                f"brand.colors.{raw_key} must be a CSS color string (got {type(val).__name__}: {val!r})"
            )
        semantic[css_key] = _validate_color(raw_key, str(val).strip())
    merged["semantic_colors"] = semantic

    # Fonts → merge per-lang
    brand_fonts = brand.get("fonts") or {}
    if brand_fonts:
        fonts = {k: dict(v) for k, v in (merged.get("fonts") or {}).items()}
        for lang in ("en", "ar"):
            if lang in brand_fonts:
                fonts[lang] = {**(fonts.get(lang) or {}), **brand_fonts[lang]}
        merged["fonts"] = fonts

    return merged


def _lang_pick(value: Any, lang: str) -> Any:
    """Pick lang-appropriate value. Supports str, dict, or absent."""
    if isinstance(value, dict):
        if lang in value and value[lang]:
            return value[lang]
        return value.get("en") or next(iter(value.values()), "")
    return value or ""


def brand_context_vars(brand: dict | None, lang: str) -> dict[str, Any]:
    """Resolve brand fields for template rendering at the given lang.

    Returns a dict assigned to the `brand` context variable. Always returns
    something (even when brand is None) so templates can unconditionally
    reference `brand.name` with `{% if brand.name %}` guards.
    """
    empty_logo = {"primary": "", "max_height_mm": 18}
    if not brand:
        return {"name": "", "legal_name": "", "identity": {}, "logo": empty_logo}

    # Bilingual name: accept `name` (string or dict), optional `name_ar` sibling.
    name_raw = brand.get("name")
    name_ar = brand.get("name_ar")
    if name_ar and lang == "ar":
        resolved_name = name_ar
    else:
        resolved_name = _lang_pick(name_raw, lang) if isinstance(name_raw, dict) else (name_raw or "")

    # Bilingual legal_name: same shape — string, or dict, or with `legal_name_ar` sibling.
    legal_raw = brand.get("legal_name")
    legal_ar = brand.get("legal_name_ar")
    if legal_ar and lang == "ar":
        resolved_legal = legal_ar
    else:
        resolved_legal = _lang_pick(legal_raw, lang) if isinstance(legal_raw, dict) else (legal_raw or "")

    # Bilingual identity: each value may be str or {en, ar} dict. `identity_ar`
    # sibling overrides whole-block for the AR render if present.
    identity_raw = brand.get("identity") or {}
    identity_ar_block = brand.get("identity_ar") or {}
    identity_resolved: dict[str, Any] = {}
    for key, val in identity_raw.items():
        if lang == "ar" and key in identity_ar_block and identity_ar_block[key]:
            identity_resolved[key] = identity_ar_block[key]
        else:
            identity_resolved[key] = _lang_pick(val, lang) if isinstance(val, dict) else (val or "")
    # Include AR-only keys (fields present in identity_ar but not identity)
    if lang == "ar":
        for key, val in identity_ar_block.items():
            if key not in identity_resolved and val:
                identity_resolved[key] = val

    return {
        "name": resolved_name,
        "legal_name": resolved_legal,
        "identity": identity_resolved,
        "logo": dict(brand.get("_resolved_logo") or empty_logo),
    }


if __name__ == "__main__":
    # Smoke
    import sys, json
    if len(sys.argv) < 3:
        print("usage: brand.py <name-or-path> <skill-brands-dir>", file=sys.stderr)
        sys.exit(1)
    b = load_brand(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps(b, indent=2, ensure_ascii=False))
