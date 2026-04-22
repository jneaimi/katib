#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "weasyprint>=60.0",
#     "pypdf>=4.0",
#     "pyyaml>=6.0",
#     "jinja2>=3.1",
# ]
# ///
"""Katib build — HTML template → PDF with token injection + vault integration.

Usage:
    uv run scripts/build.py one-pager --lang en --domain business-proposal
    uv run scripts/build.py one-pager --lang en --domain business-proposal --title "Custom Title"
    uv run scripts/build.py --check                 # CSS + template lint, no render
    uv run scripts/build.py --verify <folder>       # verify an existing generation folder

Environment:
    KATIB_DEBUG=1           Print extra info
    KATIB_OUTPUT_ROOT=...   Override vault output root (for testing)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from config import (  # noqa: E402
    load_config,
    resolve_output_root,
    resolve_project_outputs_root,
    resolve_vault_root,
)
from manifest import (  # noqa: E402
    append_index_entry,
    folder_name,
    write_manifest,
    write_run_json,
    write_tokens_snapshot,
)
from memory import log_run  # noqa: E402

DEBUG = os.environ.get("KATIB_DEBUG") == "1"


# ===================== SCREENSHOT DISCOVERY =====================

# Stem suffix order — later = more-processed. When multiple variants exist
# for the same base stem, prefer the most-processed one as the template src.
_SCREENSHOT_SUFFIX_RANK = {"": 0, ".annot": 1, ".framed": 2, ".annot.framed": 3}


def _strip_variant_suffix(stem: str) -> tuple[str, str]:
    """Split 'step-1.annot.framed' → ('step-1', '.annot.framed')."""
    for suffix in (".annot.framed", ".framed", ".annot"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)], suffix
    return stem, ""


def _resolve_text_for_lang(value: Any, lang: str) -> tuple[str, bool]:
    """Pick a caption/alt value for a given lang.

    Returns (text, fell_back_to_en). `value` can be:
      - str: legacy single-string sidecar — no fallback concept, returns as-is
      - dict: bundle like {"en": "...", "ar": "..."} — lang → en → "" with a
        boolean signaling that we dropped to EN because `lang` was missing.
    """
    if isinstance(value, dict):
        if lang in value and value[lang]:
            return value[lang], False
        if "en" in value and value["en"]:
            return value["en"], lang != "en"
        return "", False
    if isinstance(value, str):
        return value, False
    return "", False


def discover_screenshots(slug_dir: Path, lang: str = "en") -> dict[str, dict[str, Any]]:
    """Scan assets/screenshots/ and return a dict keyed by underscore-stem.

    For each base stem, pick the most-processed variant (framed > annot > raw).
    Resolve alt/caption for the target `lang` — dict sidecars pick `lang`, fall
    back to `en`, then to "". Fallbacks emit a stderr warning.
    Template context sees `screenshots.step_1 = {src, alt, caption, width, height}`.
    """
    shots_dir = slug_dir / "assets" / "screenshots"
    if not shots_dir.exists():
        return {}

    groups: dict[str, tuple[int, Path]] = {}
    for png in shots_dir.glob("*.png"):
        base, variant = _strip_variant_suffix(png.stem)
        rank = _SCREENSHOT_SUFFIX_RANK.get(variant, 0)
        best = groups.get(base)
        if best is None or rank > best[0]:
            groups[base] = (rank, png)

    result: dict[str, dict[str, Any]] = {}
    for base, (_rank, png) in groups.items():
        key = base.replace("-", "_")
        meta_path = png.with_suffix(".meta.json")
        raw_meta = shots_dir / f"{base}.meta.json"
        sidecar: dict[str, Any] = {}
        for candidate in (meta_path, raw_meta):
            if candidate.exists():
                try:
                    sidecar = json.loads(candidate.read_text(encoding="utf-8"))
                    break
                except json.JSONDecodeError:
                    continue
        alt, alt_fb = _resolve_text_for_lang(sidecar.get("alt", ""), lang)
        caption, cap_fb = _resolve_text_for_lang(sidecar.get("caption", ""), lang)
        if alt_fb:
            print(f"  ⚠ screenshot '{base}': alt missing for lang='{lang}', falling back to en",
                  file=sys.stderr)
        if cap_fb:
            print(f"  ⚠ screenshot '{base}': caption missing for lang='{lang}', falling back to en",
                  file=sys.stderr)
        result[key] = {
            "src": f"../assets/screenshots/{png.name}",
            "alt": alt,
            "caption": caption,
            "width": sidecar.get("viewport", {}).get("width"),
            "height": sidecar.get("viewport", {}).get("height"),
        }
    return result


# ===================== COVER GENERATION HOOK =====================

def maybe_generate_cover(slug_dir: Path, cover_style: str, *, force: bool = False) -> dict:
    """Invoke scripts/cover.py as a subprocess. Returns render-meta for run.json.

    Skipped if cover.png already exists (unless force=True). On any failure we log
    but continue — a missing cover does not block the PDF render.
    """
    import subprocess

    cover_path = slug_dir / "assets" / "cover.png"
    if cover_path.exists() and not force:
        return {"engine": "cached", "file": "assets/cover.png", "skipped": True}

    script = SKILL_ROOT / "scripts" / "cover.py"
    cmd = ["uv", "run", str(script), "--folder", str(slug_dir), "--style", cover_style]
    if force:
        cmd.append("--force")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  ⚠ cover.py skipped: {e}", file=sys.stderr)
        return {"engine": "failed", "error": str(e)}

    if result.returncode != 0:
        # Don't fail the whole build — surface the error and continue.
        print(f"  ⚠ cover.py exited {result.returncode}: {result.stderr.strip()[:240]}", file=sys.stderr)
        return {"engine": "failed", "returncode": result.returncode, "stderr": result.stderr.strip()}

    # CSS-only covers (e.g., minimalist-typographic) produce no cover.png —
    # the template renders the cover inline in HTML.
    if not cover_path.exists():
        return {"engine": "css", "file": None}

    # Image-engine covers: read the meta.json cover.py wrote alongside the PNG
    meta_path = cover_path.with_suffix(".meta.json")
    meta: dict = {"engine": "gemini", "file": "assets/cover.png"}
    if meta_path.exists():
        try:
            meta.update(json.loads(meta_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            pass
    return meta


# ===================== TOKEN LOADING =====================

def load_domain_tokens(domain: str) -> dict[str, Any]:
    path = SKILL_ROOT / "domains" / domain / "tokens.json"
    if not path.exists():
        raise FileNotFoundError(f"Domain tokens missing: {path}")
    with path.open() as f:
        return json.load(f)


def load_domain_styles(domain: str) -> dict[str, Any]:
    path = SKILL_ROOT / "domains" / domain / "styles.json"
    if not path.exists():
        raise FileNotFoundError(f"Domain styles missing: {path}")
    with path.open() as f:
        return json.load(f)


def tokens_to_css_vars(tokens: dict[str, Any]) -> str:
    """Convert semantic_colors + fonts from tokens.json into :root CSS custom properties."""
    lines = [":root {"]
    for var, val in tokens.get("semantic_colors", {}).items():
        lines.append(f"  {var}: {val};")
    # Font stacks
    en = tokens.get("fonts", {}).get("en", {})
    ar = tokens.get("fonts", {}).get("ar", {})
    if en:
        lines.append(f"  --font-primary: {en.get('primary', 'sans-serif')}, {en.get('fallback', 'sans-serif')};")
        lines.append(f"  --font-display: {en.get('display', en.get('primary', 'sans-serif'))}, {en.get('fallback', 'sans-serif')};")
    lines.append("}")
    if ar:
        lines.append('html[lang="ar"] {')
        lines.append(f"  --font-primary: {ar.get('primary', 'sans-serif')}, {ar.get('fallback', 'sans-serif')};")
        lines.append(f"  --font-display: {ar.get('display', ar.get('primary', 'sans-serif'))}, {ar.get('fallback', 'sans-serif')};")
        lines.append("}")
    return "\n".join(lines)


# ===================== CHECK MODE (fast lint) =====================

def check_css_violations(template_dir: Path) -> tuple[bool, list[str]]:
    """Scan CSS + HTML for forbidden patterns. Returns (ok, violations)."""
    violations = []
    simple_patterns = [
        (r"\brgba\s*\(", "rgba() — use flat hex from design.*.md conversion table"),
        (r"height\s*:\s*100vh", "height: 100vh in CSS — use explicit mm in @page"),
    ]

    search_dirs = [
        SKILL_ROOT / "styles",
        SKILL_ROOT / "domains",
    ]
    if template_dir != SKILL_ROOT:
        search_dirs.append(template_dir)

    def check_arabic_letter_spacing(text: str, path: Path) -> None:
        """Flag letter-spacing on Arabic selectors ONLY when value is non-zero/non-normal."""
        for rule_match in re.finditer(r'\[lang=[\'"]ar[\'"][^{]*\{([^}]*)\}', text):
            block = rule_match.group(1)
            for ls in re.finditer(r'letter-spacing\s*:\s*([^;}\n]+)', block):
                val = ls.group(1).strip()
                if val not in ("normal", "0", "0em", "0pt", "0px", "0rem"):
                    violations.append(
                        f"{path.relative_to(SKILL_ROOT)}: letter-spacing:{val} on Arabic selector (forbidden — breaks cursive ligatures)"
                    )

    for d in search_dirs:
        if not d.exists():
            continue
        for path in d.rglob("*.css"):
            text = path.read_text(encoding="utf-8")
            for pat, msg in simple_patterns:
                if re.search(pat, text):
                    violations.append(f"{path.relative_to(SKILL_ROOT)}: {msg}")
            check_arabic_letter_spacing(text, path)
        for path in d.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for pat, msg in simple_patterns:
                if re.search(pat, text):
                    violations.append(f"{path.relative_to(SKILL_ROOT)}: {msg}")
            check_arabic_letter_spacing(text, path)
            # <pre>/<code> need dir="ltr" in Arabic templates
            if ".ar." in path.name or 'lang="ar"' in text:
                if re.search(r"<(pre|code)(?![^>]*dir\s*=)", text):
                    violations.append(
                        f"{path.relative_to(SKILL_ROOT)}: <pre> or <code> missing dir=\"ltr\" in AR template"
                    )
                # WeasyPrint's SVG renderer doesn't run Arabic shaping — letters
                # disconnect into isolated forms. Use the .diagram-stage / .diagram-label
                # HTML-overlay pattern instead (see references/diagrams.md).
                check_arabic_in_svg(text, path, violations)

    return len(violations) == 0, violations


_AR_CHAR = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def check_arabic_in_svg(text: str, path: Path, violations: list[str]) -> None:
    """Flag any <text>/<tspan> element inside an <svg> block that contains Arabic
    characters. WeasyPrint does not shape Arabic in SVG text — migrate to the
    .diagram-stage overlay pattern documented in references/diagrams.md."""
    for svg_match in re.finditer(r"<svg\b[^>]*>(.*?)</svg>", text, re.DOTALL | re.IGNORECASE):
        svg_body = svg_match.group(1)
        for el_match in re.finditer(
            r"<(text|tspan)\b[^>]*>(.*?)</\1>", svg_body, re.DOTALL | re.IGNORECASE
        ):
            content = el_match.group(2)
            if _AR_CHAR.search(content):
                snippet = content.strip()[:40].replace("\n", " ")
                violations.append(
                    f"{path.relative_to(SKILL_ROOT)}: Arabic text in SVG <{el_match.group(1)}> "
                    f"(\"{snippet}\") — WeasyPrint can't shape Arabic in SVG. "
                    f"Use .diagram-stage HTML overlay pattern (see references/diagrams.md)."
                )


# ===================== RENDER MODE =====================

def render_template(
    domain: str,
    doc_type: str,
    lang: str,
    title: str,
    cfg: dict,
    cover_style: str | None = None,
    layout: str = "classic",
    project: str = "katib",
    reference_code: str | None = None,
    purpose: str | None = None,
    with_cover: bool = False,
    force_cover: bool = False,
    brand: dict | None = None,
    agent: str | None = None,
    source_context: str | None = None,
) -> Path:
    """Render HTML template → PDF in a new vault folder. Returns the folder path."""
    try:
        from weasyprint import HTML
        from pypdf import PdfReader
        import jinja2
    except ImportError as e:
        print(f"✗ missing dep: {e.name}. Run via: uv run scripts/build.py ...", file=sys.stderr)
        sys.exit(2)

    # Load domain config
    tokens = load_domain_tokens(domain)
    if brand:
        from brand import apply_brand_to_tokens
        tokens = apply_brand_to_tokens(tokens, brand)
    styles = load_domain_styles(domain)

    if doc_type not in styles["doc_types"]:
        raise ValueError(f"doc_type {doc_type!r} not in domain {domain!r}. Available: {list(styles['doc_types'])}")

    doc_meta = styles["doc_types"][doc_type]
    if cover_style is None:
        cover_style = styles["defaults"].get("cover")
    # Cover-less domains (e.g. `formal`): covers_allowed may be [] and defaults.cover may be null.
    # In that case we skip cover validation and render without a cover page.
    if styles.get("covers_allowed"):
        if cover_style not in styles["covers_allowed"]:
            raise ValueError(f"cover_style {cover_style!r} not allowed for domain {domain!r}")
    else:
        cover_style = None  # ensure downstream knows there's no cover

    # Layout resolution: per-doc-type default > domain default > global fallback
    if layout is None or layout == "":
        layout = doc_meta.get("default_layout") or styles.get("defaults", {}).get("layout") or "classic"
    if "layouts_allowed" in styles and layout not in styles["layouts_allowed"]:
        raise ValueError(
            f"layout {layout!r} not allowed for domain {domain!r}. "
            f"Allowed: {styles['layouts_allowed']}"
        )

    # Template path
    template_path = SKILL_ROOT / "domains" / domain / "templates" / f"{doc_type}.{lang}.html"
    if not template_path.exists():
        raise FileNotFoundError(f"Template missing: {template_path}")

    # Build output folder — include doc_type to avoid collisions across doc types for the same title
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Routing (Phase 2 of vault-integration migration):
    #   project=katib  → legacy <vault>/content/katib/<domain>/<slug>/ (governed by content/katib/CLAUDE.md)
    #   project=<slug> → <vault>/projects/<slug>/outputs/<domain>/<slug>/ (governed by projects/CLAUDE.md)
    # KATIB_OUTPUT_ROOT env var overrides both paths — used by tests to isolate writes.
    if env_root := os.environ.get("KATIB_OUTPUT_ROOT"):
        out_root = Path(env_root)
    else:
        out_root = resolve_project_outputs_root(cfg, project)

    # Folder name format: YYYY-MM-DD-<doc_type>-<slug>
    # User can override entire slug via --slug (for EN+AR co-location)
    if slug_override := os.environ.get("KATIB_SLUG_OVERRIDE"):
        slug_dir = out_root / domain / f"{today}-{slug_override}"
    else:
        slug_dir = out_root / domain / folder_name(today, f"{doc_type}-{title}")
    slug_dir.mkdir(parents=True, exist_ok=True)
    (slug_dir / "source").mkdir(exist_ok=True)
    (slug_dir / "assets").mkdir(exist_ok=True)

    # Cover generation (opt-in) — happens before HTML render so templates can reference assets/cover.png
    cover_render_meta: dict[str, Any]
    if with_cover:
        cover_render_meta = maybe_generate_cover(slug_dir, cover_style, force=force_cover)
    else:
        cover_render_meta = {"engine": "none-in-v0", "style": cover_style}

    # Load layout CSS + inject tokens
    layout_css = (SKILL_ROOT / "styles" / "layouts" / layout / "body.css").read_text(encoding="utf-8")
    tokens_css = tokens_to_css_vars(tokens)

    # Read + render template
    template_text = template_path.read_text(encoding="utf-8")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_path.parent)),
        autoescape=jinja2.select_autoescape(["html"]),
    )
    template = env.from_string(template_text)

    # Cover image — relative to rendered HTML (source/<doc>.<lang>.html)
    cover_png = slug_dir / "assets" / "cover.png"
    cover_image_src = "../assets/cover.png" if cover_png.exists() else None

    # Placeholders available to template
    # Brand context — falls back to cfg.identity when no --brand passed so
    # existing templates that read author_name/company stay unchanged.
    from brand import brand_context_vars
    brand_ctx = brand_context_vars(brand, lang)
    author_name = brand_ctx["identity"].get("author_name") or cfg.get("identity", {}).get("author_name", "")
    company = brand_ctx["name"] or cfg.get("identity", {}).get("company", "")

    # Resolved color tokens for inline use (e.g. SVG fill/stroke attributes,
    # which WeasyPrint does NOT resolve via CSS `var()`). Keys mirror
    # `semantic_colors` but strip `--` and replace `-` with `_` for Jinja
    # ergonomics: `--accent-on` → `colors.accent_on`.
    colors = {
        k.lstrip("-").replace("-", "_"): v
        for k, v in (tokens.get("semantic_colors") or {}).items()
    }

    context = {
        "title": title,
        "subtitle": purpose or "",
        "reference_code": reference_code or "",
        "author_name": author_name,
        "company": company,
        "brand": brand_ctx,
        "colors": colors,
        "today": today,
        "tokens_css": tokens_css,
        "layout_css": layout_css,
        "lang": lang,
        "direction": "rtl" if lang == "ar" else "ltr",
        "screenshots": discover_screenshots(slug_dir, lang),
        "cover_style": cover_style,
        "cover_image_src": cover_image_src,
    }
    rendered_html = template.render(**context)

    # Write source HTML
    source_path = slug_dir / "source" / f"{doc_type}.{lang}.html"
    source_path.write_text(rendered_html, encoding="utf-8")

    # Snapshot tokens
    write_tokens_snapshot(slug_dir, tokens)

    # Render PDF — base_url = source dir so relative @font-face paths resolve
    pdf_path = slug_dir / f"{doc_type}.{lang}.pdf"
    HTML(string=rendered_html, base_url=str(source_path.parent)).write_pdf(str(pdf_path))

    # Count pages + enforce limit
    pages = len(PdfReader(str(pdf_path)).pages)
    page_limit = doc_meta.get("page_limit", 0)
    over_limit = page_limit and pages > page_limit
    target_range = doc_meta.get("target_pages") or []
    under_target = bool(target_range) and pages < target_range[0]

    # Source context: short run-id so manifest frontmatter can be traced back to
    # a specific Katib render. Use first 8 chars of a UUID4 — enough entropy for
    # audit-log lookups, cheap to generate, stable across EN/AR co-located runs
    # because we derive it from the slug_dir name (shared between languages).
    import hashlib
    if not source_context:
        source_context = hashlib.blake2s(slug_dir.name.encode(), digest_size=4).hexdigest()

    # Meta for manifest
    meta = {
        "title": title,
        "domain": domain,
        "doc_type": doc_type,
        "languages": [lang],
        "formats": ["pdf"],
        "cover_style": cover_style,
        "layout": layout,
        "project": project,
        "created": today,
        "purpose": purpose,
        "source_context": source_context,
    }
    if agent:
        meta["source_agent"] = agent
    if reference_code:
        meta["reference_code"] = reference_code

    # Write manifest + run.json
    # vault_root goes through to manifest.py so first-writes route via the
    # Soul Hub API (Phase 2). When KATIB_OUTPUT_ROOT redirects output to a
    # scratch path outside the vault, write_manifest detects that and does
    # a pure FS write — no API call. Updates (merge path) also stay on FS.
    vault_root_for_write: Path | None
    try:
        vault_root_for_write = resolve_vault_root(cfg)
    except Exception:
        vault_root_for_write = None
    write_manifest(slug_dir, meta, vault_root=vault_root_for_write)
    render_meta = {
        "page_counts": {pdf_path.name: pages},
        "cover": {"style": cover_style, **cover_render_meta},
        "verify": {"passed": not over_limit, "checks": ["page-limit"]},
    }
    write_run_json(slug_dir, meta, render_meta)

    # Passive capture — one line in runs.jsonl for reflect.py to analyse later
    if brand:
        meta_for_log = {**meta, "brand_name": brand.get("name") or brand.get("id")}
    else:
        meta_for_log = meta
    try:
        log_run(cfg, meta_for_log, render_meta, pdf_path)
    except Exception as e:
        if DEBUG:
            print(f"⚠ memory log skipped: {e}", file=sys.stderr)

    # Append to vault index (only if destination=vault AND slug_dir is actually under it —
    # KATIB_OUTPUT_ROOT can redirect output to a scratch path for testing)
    if cfg["output"]["destination"] == "vault":
        katib_root = Path(cfg["output"]["vault_path"])
        try:
            slug_dir.resolve().relative_to(katib_root.resolve())
            in_vault = True
        except ValueError:
            in_vault = False
        if in_vault and (katib_root / "index.md").exists():
            append_index_entry(katib_root, slug_dir, meta)

    # Report
    msg = f"✓ {domain}/{doc_type}.{lang} · {pages} page{'s' if pages != 1 else ''}"
    if over_limit:
        msg = f"✗ {domain}/{doc_type}.{lang} · {pages} pages (limit {page_limit})"
    print(msg)
    print(f"  → {pdf_path.relative_to(out_root)}")
    print(f"  folder: {slug_dir}")
    if under_target and not over_limit:
        print(f"  ⚠ under target: {pages} pp (expected ≥{target_range[0]} pp for {doc_type})", file=sys.stderr)

    if over_limit:
        sys.exit(3)

    return slug_dir


# ===================== VERIFY MODE =====================

def verify_folder(folder: Path) -> tuple[bool, list[str]]:
    """Verify a generation folder has all required files + manifest fields."""
    issues = []

    required_files = ["manifest.md", "source", ".katib/run.json"]
    for req in required_files:
        if not (folder / req).exists():
            issues.append(f"missing: {req}")

    # Parse manifest frontmatter
    manifest_path = folder / "manifest.md"
    if manifest_path.exists():
        text = manifest_path.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            issues.append("manifest.md missing frontmatter")
        else:
            fm = fm_match.group(1)
            required_fields = ["type:", "created:", "updated:", "tags:", "project:", "domain:", "doc_type:"]
            for field in required_fields:
                if field not in fm:
                    issues.append(f"manifest frontmatter missing: {field.rstrip(':')}")

    # tokens-snapshot.json parses
    snap = folder / "source" / "tokens-snapshot.json"
    if snap.exists():
        try:
            json.loads(snap.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append(f"tokens-snapshot.json invalid: {e}")

    # Unresolved placeholders in source HTML
    for html in (folder / "source").glob("*.html"):
        text = html.read_text(encoding="utf-8")
        if "{{" in text and "}}" in text:
            # Check if it's an unresolved Jinja placeholder (heuristic)
            placeholders = re.findall(r"\{\{\s*([^}]+?)\s*\}\}", text)
            if placeholders:
                issues.append(f"{html.name}: unresolved placeholders: {placeholders[:3]}")

    return len(issues) == 0, issues


# ===================== CLI =====================

def main():
    parser = argparse.ArgumentParser(description="Katib build")
    parser.add_argument("doc_type", nargs="?", help="Doc type (e.g., one-pager, proposal, letter)")
    parser.add_argument("--domain", default="business-proposal")
    parser.add_argument("--lang", default="en", choices=["en", "ar"])
    parser.add_argument("--title", default="Sample Document")
    parser.add_argument("--cover", default=None, help="Cover style (defaults to domain default)")
    parser.add_argument("--layout", default=None, help="Layout (default: from domain styles.json defaults.layout, fallback 'classic')")
    parser.add_argument("--project", default="katib")
    parser.add_argument("--ref", default=None, help="Reference code (e.g., TITS-TP-2026-001)")
    parser.add_argument("--purpose", default=None)
    parser.add_argument("--slug", default=None, help="Custom folder slug (use to co-locate EN+AR in one folder)")
    parser.add_argument("--with-cover", action="store_true", help="Generate cover.png via Gemini Nano Banana 2 before render")
    parser.add_argument("--force-cover", action="store_true", help="Regenerate cover even if assets/cover.png exists (implies --with-cover)")
    parser.add_argument("--brand", default=None, help="Brand profile name (resolves to ~/.katib/brands/<name>.yaml or <skill>/brands/<name>.yaml)")
    parser.add_argument("--brand-file", default=None, help="Direct path to a brand profile YAML (overrides --brand)")
    parser.add_argument("--agent", default=None, help="source_agent identifier for write audit log (default: $KATIB_AGENT_ID or 'katib-cli')")

    # modes
    parser.add_argument("--check", action="store_true", help="CSS/template lint only, no render")
    parser.add_argument("--verify", metavar="FOLDER", help="Verify an existing generation folder")
    parser.add_argument("--list-brands", action="store_true", help="List available brand profiles (user + skill dirs) and exit")

    args = parser.parse_args()

    if args.list_brands:
        from brand import list_brands
        profiles = list_brands(SKILL_ROOT / "brands")
        if not profiles:
            print("No brand profiles found.")
            print(f"  user:  ~/.katib/brands/")
            print(f"  skill: {SKILL_ROOT / 'brands'}/")
            sys.exit(0)
        width = max(len(p["name"]) for p in profiles)
        print(f"{'NAME'.ljust(width)}  LOCATION  DISPLAY NAME")
        for p in profiles:
            print(f"{p['name'].ljust(width)}  {p['location'].ljust(8)}  {p['display']}")
        sys.exit(0)

    if args.check:
        ok, violations = check_css_violations(SKILL_ROOT)
        if ok:
            print("✓ check passed (no violations)")
            sys.exit(0)
        for v in violations:
            print(f"✗ {v}")
        sys.exit(1)

    if args.verify:
        folder = Path(args.verify).resolve()
        ok, issues = verify_folder(folder)
        if ok:
            print(f"✓ verify passed: {folder}")
            sys.exit(0)
        for i in issues:
            print(f"✗ {i}")
        sys.exit(1)

    if not args.doc_type:
        parser.print_help()
        sys.exit(1)

    cfg = load_config()
    if args.slug:
        os.environ["KATIB_SLUG_OVERRIDE"] = args.slug

    brand = None
    if args.brand_file and args.brand:
        print(
            f"⚠ --brand-file={args.brand_file} overrides --brand={args.brand}. "
            f"Loading the file path; pass one flag, not both.",
            file=sys.stderr,
        )
    brand_selector = args.brand_file or args.brand
    if brand_selector:
        from brand import load_brand, BrandError
        try:
            brand = load_brand(brand_selector, SKILL_ROOT / "brands")
        except BrandError as e:
            print(f"✗ {e}", file=sys.stderr)
            sys.exit(1)

    render_template(
        domain=args.domain,
        doc_type=args.doc_type,
        lang=args.lang,
        title=args.title,
        cfg=cfg,
        cover_style=args.cover,
        layout=args.layout,
        project=args.project,
        agent=args.agent,
        reference_code=args.ref,
        purpose=args.purpose,
        with_cover=args.with_cover or args.force_cover,
        force_cover=args.force_cover,
        brand=brand,
    )


if __name__ == "__main__":
    main()
