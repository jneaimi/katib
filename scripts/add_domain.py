#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Katib — add_domain.py: scaffold a new domain end-to-end.

Generates `domains/<name>/tokens.json` + `styles.json` + skeleton templates
(one per doc-type × lang), and patches SKILL.md router tables.

Closes the self-improvement loop: reflect.py's `new-domain-candidate`
proposals now become one-command actions.

Usage:
    python3 scripts/add_domain.py <name>                    # interactive Q&A
    python3 scripts/add_domain.py <name> --from-json <f>    # non-interactive
    python3 scripts/add_domain.py <name> --dry-run          # preview only
    python3 scripts/add_domain.py <name> --force            # overwrite existing
    python3 scripts/add_domain.py --list-presets            # show palette + font presets
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = SKILL_ROOT / "domains"
SKILL_MD = SKILL_ROOT / "SKILL.md"

NAME_RE = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$")


# ===================== PRESETS =====================

PALETTE_PRESETS: dict[str, dict[str, str]] = {
    "warm": {
        "description": "Terracotta + slate-teal on warm ivory. Instructional, approachable.",
        "--page-bg": "#FBF8F3",
        "--accent": "#C85A3E",
        "--accent-2": "#3A7D8B",
        "--accent-on": "#FFFFFF",
        "--text": "#2A2A2A",
        "--text-secondary": "#4A4A4A",
        "--text-tertiary": "#7A7268",
        "--border": "#E5DED1",
        "--border-strong": "#CFC4AF",
        "--tag-bg": "#EFE5D6",
        "--tag-fg": "#2A2A2A",
        "--code-bg": "#F3EEE3",
        "--code-fg": "#2A2A2A",
    },
    "cool": {
        "description": "Navy + sky on white. Clean, corporate, digital-native.",
        "--page-bg": "#FFFFFF",
        "--accent": "#1E3A8A",
        "--accent-2": "#3B82F6",
        "--accent-on": "#FFFFFF",
        "--text": "#1F2937",
        "--text-secondary": "#4B5563",
        "--text-tertiary": "#6B7280",
        "--border": "#E5E7EB",
        "--border-strong": "#CBD5E1",
        "--tag-bg": "#DBEAFE",
        "--tag-fg": "#1E3A8A",
        "--code-bg": "#F1F5F9",
        "--code-fg": "#1F2937",
    },
    "emerald": {
        "description": "Emerald + slate on warm ivory. Financial, trustworthy.",
        "--page-bg": "#FBF9F3",
        "--accent": "#0F5F4E",
        "--accent-2": "#64748B",
        "--accent-on": "#FFFFFF",
        "--text": "#1F2937",
        "--text-secondary": "#475569",
        "--text-tertiary": "#64748B",
        "--border": "#E2E4DC",
        "--border-strong": "#C4C8BE",
        "--tag-bg": "#D7E8E2",
        "--tag-fg": "#0F5F4E",
        "--code-bg": "#F1F0E6",
        "--code-fg": "#1F2937",
    },
    "burgundy": {
        "description": "Burgundy + sage on cream. Academic, serious.",
        "--page-bg": "#FAF6EC",
        "--accent": "#7E1D4A",
        "--accent-2": "#5A8549",
        "--accent-on": "#FFFFFF",
        "--text": "#1F1B1C",
        "--text-secondary": "#3F3A3B",
        "--text-tertiary": "#6A635F",
        "--border": "#E4DDCA",
        "--border-strong": "#CAC0A6",
        "--tag-bg": "#ECD9E2",
        "--tag-fg": "#7E1D4A",
        "--code-bg": "#F2ECDC",
        "--code-fg": "#1F1B1C",
    },
    "navy-gold": {
        "description": "Navy + gold on off-white. Institutional, formal proposals.",
        "--page-bg": "#FAFAF8",
        "--accent": "#1B2A4A",
        "--accent-2": "#C5A44E",
        "--accent-on": "#FFFFFF",
        "--text": "#1A1A1A",
        "--text-secondary": "#404040",
        "--text-tertiary": "#6A6A6A",
        "--border": "#D9D9D3",
        "--border-strong": "#BFBEB4",
        "--tag-bg": "#D8DEED",
        "--tag-fg": "#1B2A4A",
        "--code-bg": "#ECECE4",
        "--code-fg": "#1A1A1A",
    },
    "editorial-red": {
        "description": "Magazine red + ink on warm newsprint. Op-eds, articles.",
        "--page-bg": "#FAF6F0",
        "--accent": "#B91C1C",
        "--accent-2": "#0F172A",
        "--accent-on": "#FFFFFF",
        "--text": "#171717",
        "--text-secondary": "#3F3F46",
        "--text-tertiary": "#71717A",
        "--border": "#E4DED3",
        "--border-strong": "#C8C0B1",
        "--tag-bg": "#F4DCDC",
        "--tag-fg": "#B91C1C",
        "--code-bg": "#F0EBE0",
        "--code-fg": "#171717",
    },
    "slate": {
        "description": "Slate + teal on warm paper. Reports, data-forward.",
        "--page-bg": "#FAFAF8",
        "--accent": "#2E3A4B",
        "--accent-2": "#0F766E",
        "--accent-on": "#FFFFFF",
        "--text": "#1F2937",
        "--text-secondary": "#4B5563",
        "--text-tertiary": "#6B7280",
        "--border": "#D6D3CB",
        "--border-strong": "#A8A39A",
        "--tag-bg": "#E7EEF1",
        "--tag-fg": "#2E3A4B",
        "--code-bg": "#F1EFE8",
        "--code-fg": "#1F2937",
    },
    "neutral": {
        "description": "Minimal greyscale. Brand-agnostic starting point.",
        "--page-bg": "#FFFFFF",
        "--accent": "#18181B",
        "--accent-2": "#71717A",
        "--accent-on": "#FFFFFF",
        "--text": "#18181B",
        "--text-secondary": "#3F3F46",
        "--text-tertiary": "#71717A",
        "--border": "#E4E4E7",
        "--border-strong": "#A1A1AA",
        "--tag-bg": "#F4F4F5",
        "--tag-fg": "#18181B",
        "--code-bg": "#F4F4F5",
        "--code-fg": "#18181B",
    },
}


FONT_PRESETS: dict[str, dict[str, dict[str, str]]] = {
    "sans-modern": {
        "en": {"primary": "Inter", "display": "Inter", "mono": "JetBrains Mono",
               "fallback": "system-ui, -apple-system, sans-serif"},
        "ar": {"primary": "Cairo", "display": "Cairo", "mono": "JetBrains Mono",
               "fallback": "IBM Plex Arabic, Tahoma, sans-serif"},
    },
    "serif-editorial": {
        "en": {"primary": "Newsreader", "display": "Newsreader", "mono": "JetBrains Mono",
               "fallback": "Georgia, 'Times New Roman', serif"},
        "ar": {"primary": "Amiri", "display": "Amiri", "mono": "JetBrains Mono",
               "fallback": "'Traditional Arabic', Tahoma, serif"},
    },
    "serif-formal": {
        "en": {"primary": "Georgia", "display": "Georgia", "mono": "JetBrains Mono",
               "fallback": "'Times New Roman', serif"},
        "ar": {"primary": "Amiri", "display": "Amiri", "mono": "JetBrains Mono",
               "fallback": "'Traditional Arabic', Tahoma, serif"},
    },
    "corporate": {
        "en": {"primary": "Arial", "display": "Arial", "mono": "JetBrains Mono",
               "fallback": "Helvetica, system-ui, sans-serif"},
        "ar": {"primary": "Tajawal", "display": "Tajawal", "mono": "JetBrains Mono",
               "fallback": "Tahoma, sans-serif"},
    },
}

COVER_STYLES = ["minimalist-typographic", "neural-cartography", "friendly-illustration"]
LAYOUTS = ["classic", "workbook", "cheatsheet"]


# ===================== Q&A + SPEC LOADING =====================

def _input(prompt: str, default: str | None = None) -> str:
    """Read from stdin, showing default in brackets."""
    if default is not None:
        shown = f"{prompt} [{default}]: "
    else:
        shown = f"{prompt}: "
    try:
        val = input(shown).strip()
    except EOFError:
        val = ""
    return val or (default or "")


def _pick(prompt: str, choices: list[str], default: str) -> str:
    """Show numbered list, accept name or index."""
    print(f"\n{prompt}")
    for i, c in enumerate(choices, 1):
        marker = " ← default" if c == default else ""
        print(f"  {i}. {c}{marker}")
    raw = _input("  pick (name or number)", default)
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(choices):
            return choices[idx]
    if raw in choices:
        return raw
    print(f"  ⚠ '{raw}' not in choices — using default '{default}'")
    return default


def interactive_spec(name: str) -> dict[str, Any]:
    """Run the Q&A flow and return a normalized spec dict."""
    print(f"\n▶ Scaffolding new domain: {name}\n")

    description_en = _input("Description (EN, one line)",
                            f"Documents for the {name} domain.")
    description_ar = _input("Description (AR, one line — optional)", "")

    palette_name = _pick("Palette preset:", list(PALETTE_PRESETS), "neutral")
    fonts_name = _pick("Font preset:", list(FONT_PRESETS), "sans-modern")
    default_cover = _pick("Default cover:", COVER_STYLES, "minimalist-typographic")
    default_layout = _pick("Default layout:", LAYOUTS, "classic")

    print()
    doc_types_raw = _input("Doc types (comma-separated)", name)
    doc_type_names = [d.strip() for d in doc_types_raw.split(",") if d.strip()]
    if not doc_type_names:
        doc_type_names = [name]

    doc_types = []
    for dt in doc_type_names:
        print(f"\n  — doc type: {dt} —")
        page_limit = int(_input(f"    page_limit", "8"))
        target_lo = int(_input(f"    target_pages min", "2"))
        target_hi = int(_input(f"    target_pages max", "6"))
        rc_prefix = _input(f"    reference-code prefix", f"{dt.upper()[:4]}-")
        doc_types.append({
            "name": dt,
            "page_limit": page_limit,
            "target_pages": [target_lo, target_hi],
            "rc_prefix": rc_prefix,
            "sections_required": ["body"],
        })

    print()
    router_signals = _input("Router signals for SKILL.md (EN / AR, e.g. 'memo / tech-memo / مذكرة')",
                            f"{name} / {description_en.lower()[:30]}")

    return {
        "name": name,
        "description_en": description_en,
        "description_ar": description_ar,
        "palette": palette_name,
        "fonts": fonts_name,
        "default_cover": default_cover,
        "default_layout": default_layout,
        "covers_allowed": [default_cover],
        "layouts_allowed": [default_layout],
        "doc_types": doc_types,
        "router_signals": router_signals,
    }


def load_spec_from_json(path: Path, name: str) -> dict[str, Any]:
    """Load a spec from JSON and normalize defaults. `name` wins over any `name` in JSON."""
    spec = json.loads(path.read_text(encoding="utf-8"))
    spec["name"] = name
    spec.setdefault("description_en", f"Documents for the {name} domain.")
    spec.setdefault("description_ar", "")
    spec.setdefault("palette", "neutral")
    spec.setdefault("fonts", "sans-modern")
    spec.setdefault("default_cover", "minimalist-typographic")
    spec.setdefault("default_layout", "classic")
    spec.setdefault("covers_allowed", [spec["default_cover"]])
    spec.setdefault("layouts_allowed", [spec["default_layout"]])
    spec.setdefault("doc_types", [{"name": name, "page_limit": 8,
                                   "target_pages": [2, 6],
                                   "rc_prefix": f"{name.upper()[:4]}-",
                                   "sections_required": ["body"]}])
    spec.setdefault("router_signals", f"{name}")
    for dt in spec["doc_types"]:
        dt.setdefault("page_limit", 8)
        dt.setdefault("target_pages", [2, 6])
        dt.setdefault("rc_prefix", f"{dt['name'].upper()[:4]}-")
        dt.setdefault("sections_required", ["body"])
    return spec


# ===================== TOKENS + STYLES BUILDERS =====================

def build_tokens_json(spec: dict) -> dict:
    """Produce the tokens.json body for the new domain."""
    palette = PALETTE_PRESETS[spec["palette"]]
    fonts = FONT_PRESETS[spec["fonts"]]

    semantic_colors = {k: v for k, v in palette.items() if k.startswith("--")}

    brand_block = {
        "accent": semantic_colors["--accent"],
        "accent_2": semantic_colors["--accent-2"],
        "page_bg": semantic_colors["--page-bg"],
        "text": semantic_colors["--text"],
    }

    margins = {dt["name"]: {"top": 20, "right": 22, "bottom": 22, "left": 22}
               for dt in spec["doc_types"]}

    return {
        "domain": spec["name"],
        "description": spec["description_en"],
        "brand": brand_block,
        "semantic_colors": semantic_colors,
        "fonts": fonts,
        "page": {
            "size": "A4",
            "portrait": True,
            "margins_mm": margins,
            "cover_margins_mm": {"top": 0, "right": 0, "bottom": 0, "left": 0},
        },
        "sections": ["cover", "body"],
        "page_numbering": {"cover": "hidden", "body_start_at": 2},
        "numerals": {"en": "western", "ar": "western"},
    }


def build_styles_json(spec: dict) -> dict:
    """Produce the styles.json body for the new domain."""
    doc_types = {}
    for dt in spec["doc_types"]:
        doc_types[dt["name"]] = {
            "formats": ["pdf"],
            "default_format": "pdf",
            "default_layout": spec["default_layout"],
            "page_limit": dt["page_limit"],
            "target_pages": dt["target_pages"],
            "sections_required": dt["sections_required"],
        }

    return {
        "domain": spec["name"],
        "covers_allowed": spec["covers_allowed"],
        "layouts_allowed": spec["layouts_allowed"],
        "defaults": {"cover": spec["default_cover"], "layout": spec["default_layout"]},
        "doc_types": doc_types,
    }


# ===================== SKELETON TEMPLATE =====================

SKELETON_HTML = """<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ direction }}">
<head>
  <meta charset="UTF-8">
  <title>{{ title }}</title>
  <style>
  {{ tokens_css | safe }}
  {{ layout_css | safe }}

  @page {
    size: A4;
    margin: 22mm;
    @bottom-center {
      content: "{{ title }}  ·  Page " counter(page) " of " counter(pages);
      font-size: 8pt;
      color: var(--text-tertiary);
    }
  }
  @page :first { @bottom-center { content: none; } }

  .cover-page {
    height: 253mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    page-break-after: always;
    text-align: center;
  }
  .cover-page .cover-title {
    font-size: 40pt;
    font-weight: 600;
    color: var(--text);
    margin: 0;
    line-height: 1.1;
    max-width: 150mm;
  }
  .cover-page .cover-subtitle {
    font-size: 13pt;
    color: var(--accent);
    margin-top: 16pt;
    max-width: 140mm;
  }
  .cover-page .cover-rule {
    width: 40mm;
    height: 0.5pt;
    background: var(--border-strong);
    margin: 28pt 0;
  }
  .cover-page .cover-meta {
    font-family: var(--font-mono, monospace);
    font-size: 9pt;
    color: var(--text-tertiary);
  }

  .skeleton-note {
    background: var(--tag-bg);
    color: var(--tag-fg);
    padding: 10pt 14pt;
    border-{BORDER_SIDE}: 3pt solid var(--accent);
    margin: 20pt 0;
    font-size: 10pt;
  }
  </style>
</head>
<body>

  <section class="cover-page">
    <h1 class="cover-title">{{ title }}</h1>
    {% if subtitle %}<p class="cover-subtitle">{{ subtitle }}</p>{% endif %}
    <div class="cover-rule"></div>
    <div class="cover-meta">{{ reference_code or "{RC_PREFIX}" }}  ·  {{ today }}</div>
  </section>

  <h1>{{ title }}</h1>

  <div class="skeleton-note">
    <strong>{SKELETON_LABEL}</strong>
    {SKELETON_MSG}
  </div>

  <h2>{SECTION_1_TITLE}</h2>
  <p>{SECTION_1_BODY}</p>

  <h2>{SECTION_2_TITLE}</h2>
  <p>{SECTION_2_BODY}</p>

</body>
</html>
"""

EN_STRINGS = {
    "BORDER_SIDE": "left",
    "SKELETON_LABEL": "Skeleton template",
    "SKELETON_MSG": "This was generated by <code dir=\"ltr\">add_domain.py</code>. Replace with your document structure — body copy, tables, callouts, code blocks, or screenshots as needed.",
    "SECTION_1_TITLE": "First section",
    "SECTION_1_BODY": "Edit this paragraph. Use <code dir=\"ltr\">references/design.en.md</code> for typography rules and <code dir=\"ltr\">references/writing.en.md</code> for voice.",
    "SECTION_2_TITLE": "Second section",
    "SECTION_2_BODY": "Follow the domain's spec — tokens live in <code dir=\"ltr\">tokens.json</code>, layout rhythm comes from <code dir=\"ltr\">styles/layouts/classic/body.css</code>. Build with <code dir=\"ltr\">python3 scripts/build.py &lt;doc-type&gt; --domain &lt;this-domain&gt;</code>.",
}

AR_STRINGS = {
    "BORDER_SIDE": "right",
    "SKELETON_LABEL": "قالب هيكلي",
    "SKELETON_MSG": "تم إنشاء هذا القالب بواسطة <code dir=\"ltr\">add_domain.py</code>. استبدل محتواه ببنية مستندك — فقرات، جداول، تنبيهات، أكواد، أو لقطات شاشة حسب الحاجة.",
    "SECTION_1_TITLE": "القسم الأول",
    "SECTION_1_BODY": "حرّر هذه الفقرة. راجع <code dir=\"ltr\">references/design.ar.md</code> لقواعد الطباعة و <code dir=\"ltr\">references/writing.ar.md</code> للأسلوب.",
    "SECTION_2_TITLE": "القسم الثاني",
    "SECTION_2_BODY": "اتّبع مواصفات النطاق — الرموز في <code dir=\"ltr\">tokens.json</code> وإيقاع التخطيط من <code dir=\"ltr\">styles/layouts/classic/body.css</code>. ابنِ عبر <code dir=\"ltr\">python3 scripts/build.py &lt;doc-type&gt; --domain &lt;this-domain&gt; --lang ar</code>.",
}


def build_skeleton_template(doc_type: dict, lang: str) -> str:
    """Return the full HTML skeleton for one doc-type × lang."""
    strings = EN_STRINGS if lang == "en" else AR_STRINGS
    out = SKELETON_HTML
    out = out.replace("{BORDER_SIDE}", strings["BORDER_SIDE"])
    out = out.replace("{SKELETON_LABEL}", strings["SKELETON_LABEL"])
    out = out.replace("{SKELETON_MSG}", strings["SKELETON_MSG"])
    out = out.replace("{SECTION_1_TITLE}", strings["SECTION_1_TITLE"])
    out = out.replace("{SECTION_1_BODY}", strings["SECTION_1_BODY"])
    out = out.replace("{SECTION_2_TITLE}", strings["SECTION_2_TITLE"])
    out = out.replace("{SECTION_2_BODY}", strings["SECTION_2_BODY"])
    out = out.replace("{RC_PREFIX}", doc_type["rc_prefix"].rstrip("-"))
    return out


# ===================== SKILL.md PATCHING =====================

ROUTER_ANCHOR = "All planned domains are live."
# Doc-type table "legal" row is distinct from the router "legal" row because
# it includes `service-agreement`. Match the full pattern to avoid colliding
# with the router table (which also contains `| `legal` |`).
DOC_TABLE_ROW_RE = re.compile(
    r"(\|\s*`legal`\s*\|\s*`service-agreement`[^\n]*\n)"
)


def patch_skill_md(spec: dict, skill_md_path: Path = SKILL_MD) -> str:
    """Return the new SKILL.md text with router + doc-type table rows appended.

    Idempotent: if the domain row already exists, return unchanged text.
    """
    text = skill_md_path.read_text(encoding="utf-8")

    new_router_row = (
        f"| \"{spec['router_signals']}\" "
        f"| `{spec['name']}` "
        f"| {PALETTE_PRESETS[spec['palette']]['description']} |"
    )
    if f"`{spec['name']}`" in text and new_router_row.strip() in text:
        return text  # already patched

    # Router table — insert before the "All planned domains are live." line
    if new_router_row not in text:
        text = text.replace(
            f"\n{ROUTER_ANCHOR}",
            f"\n{new_router_row}\n\n{ROUTER_ANCHOR}",
            1,
        )

    # Doc-type table — insert after the legal row (second "legal" row, distinct
    # from the router row because it starts with `service-agreement`).
    doc_names = ", ".join(f"`{dt['name']}`" for dt in spec["doc_types"])
    new_doc_row = f"| `{spec['name']}` | {doc_names} |"
    if new_doc_row not in text:
        text = DOC_TABLE_ROW_RE.sub(
            lambda m: m.group(1) + new_doc_row + "\n",
            text,
            count=1,
        )

    return text


# ===================== WRITE ORCHESTRATOR =====================

def write_domain(spec: dict, *, dry_run: bool = False, force: bool = False) -> list[Path]:
    """Materialize the domain. Returns list of paths written (or that would be written)."""
    name = spec["name"]
    domain_dir = DOMAINS_DIR / name
    templates_dir = domain_dir / "templates"
    written: list[Path] = []

    if domain_dir.exists() and not force:
        raise FileExistsError(
            f"Domain '{name}' already exists at {domain_dir}. Use --force to overwrite."
        )

    tokens = build_tokens_json(spec)
    styles = build_styles_json(spec)
    new_skill_md = patch_skill_md(spec)

    plan: list[tuple[Path, str]] = []
    plan.append((domain_dir / "tokens.json", json.dumps(tokens, indent=2, ensure_ascii=False) + "\n"))
    plan.append((domain_dir / "styles.json", json.dumps(styles, indent=2, ensure_ascii=False) + "\n"))
    for dt in spec["doc_types"]:
        for lang in ("en", "ar"):
            plan.append((templates_dir / f"{dt['name']}.{lang}.html",
                         build_skeleton_template(dt, lang)))
    plan.append((SKILL_MD, new_skill_md))

    if dry_run:
        print("\n▶ Dry run — these files would be written:")
        for path, _body in plan:
            marker = "·" if path.exists() else "+"
            print(f"  {marker} {path.relative_to(SKILL_ROOT)}")
        return [p for p, _ in plan]

    # Create dirs
    templates_dir.mkdir(parents=True, exist_ok=True)

    for path, body in plan:
        path.write_text(body, encoding="utf-8")
        written.append(path)
        rel = path.relative_to(SKILL_ROOT) if path.is_relative_to(SKILL_ROOT) else path
        print(f"  ✓ wrote {rel}")

    return written


# ===================== SUMMARY =====================

def print_summary(spec: dict) -> None:
    print("\n▶ Summary")
    print(f"  name:            {spec['name']}")
    print(f"  description:     {spec['description_en']}")
    if spec.get("description_ar"):
        print(f"  description ar:  {spec['description_ar']}")
    print(f"  palette:         {spec['palette']}  ({PALETTE_PRESETS[spec['palette']]['description']})")
    print(f"  fonts:           {spec['fonts']}")
    print(f"  default cover:   {spec['default_cover']}")
    print(f"  default layout:  {spec['default_layout']}")
    print(f"  doc types ({len(spec['doc_types'])}):")
    for dt in spec["doc_types"]:
        pages = f"{dt['target_pages'][0]}–{dt['target_pages'][1]} pp (max {dt['page_limit']})"
        print(f"    - {dt['name']:<20} {pages}  rc: {dt['rc_prefix']}")
    print()


def list_presets() -> None:
    print("Palette presets:")
    for name, block in PALETTE_PRESETS.items():
        print(f"  {name:<16} {block['description']}")
    print("\nFont presets:")
    for name, block in FONT_PRESETS.items():
        en = block["en"]["primary"]
        ar = block["ar"]["primary"]
        print(f"  {name:<16} EN: {en:<12} AR: {ar}")


# ===================== MAIN =====================

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("name", nargs="?", help="Domain name (lowercase, hyphens allowed)")
    parser.add_argument("--from-json", metavar="FILE", help="Load spec from JSON (non-interactive)")
    parser.add_argument("--dry-run", action="store_true", help="Print plan, don't write")
    parser.add_argument("--force", action="store_true", help="Overwrite existing domain")
    parser.add_argument("--list-presets", action="store_true", help="List palette + font presets")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    if args.list_presets:
        list_presets()
        return 0

    if not args.name:
        parser.error("name is required (or use --list-presets)")
    name = args.name

    if not NAME_RE.match(name):
        print(f"✗ invalid name '{name}' — must match {NAME_RE.pattern}", file=sys.stderr)
        return 2

    # Build spec
    if args.from_json:
        spec = load_spec_from_json(Path(args.from_json), name)
    else:
        spec = interactive_spec(name)

    # Validate preset references
    if spec["palette"] not in PALETTE_PRESETS:
        print(f"✗ unknown palette '{spec['palette']}'. Run --list-presets.", file=sys.stderr)
        return 2
    if spec["fonts"] not in FONT_PRESETS:
        print(f"✗ unknown fonts '{spec['fonts']}'. Run --list-presets.", file=sys.stderr)
        return 2

    print_summary(spec)

    # Confirm unless -y / --dry-run / --from-json
    if not (args.yes or args.dry_run or args.from_json):
        ans = _input("Write these files?", "y").lower()
        if ans not in ("y", "yes"):
            print("aborted.")
            return 1

    try:
        write_domain(spec, dry_run=args.dry_run, force=args.force)
    except FileExistsError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        return 0

    # Verify by running --check
    print("\n▶ Verifying with build.py --check...")
    import subprocess
    result = subprocess.run(
        ["python3", str(SKILL_ROOT / "scripts" / "build.py"), "--check"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print("  ✓ --check passed")
    else:
        print(f"  ✗ --check reported violations (exit {result.returncode}):")
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return 3

    print(f"\n✓ Domain '{name}' scaffolded. Next:")
    print(f"  1. Edit domains/{name}/templates/*.html to flesh out structure")
    print(f"  2. Build a test render: python3 scripts/build.py {spec['doc_types'][0]['name']} --domain {name}")
    print(f"  3. Commit when happy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
