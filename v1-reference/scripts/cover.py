#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=0.3",
#     "python-dotenv>=1.0",
#     "pyyaml>=6.0",
#     "pillow>=10.0",
# ]
# ///
"""Katib cover generator — Gemini Nano Banana 2 (`gemini-3-pro-image-preview`).

Reads a cover style brief from `styles/covers/<style>/brief.md`, sends the prompt
to Gemini, and writes `assets/cover.png` + `assets/cover.meta.json` alongside
the target document folder.

The same image is used for EN and AR variants of a given document — the style
brief only differs by overlay placement, handled at template/HTML level.

Usage:
    # Standard — write cover.png into an existing Katib generation folder
    uv run scripts/cover.py --folder <generation-folder> [--style neural-cartography]

    # Arbitrary output path (useful for one-off exploration)
    uv run scripts/cover.py --out /tmp/cover.png --style neural-cartography

    # Dry-run: print the prompt & model call that would be made, do not call API
    uv run scripts/cover.py --folder <folder> --dry-run

Flags:
    --folder PATH       Katib generation folder (creates assets/ if missing)
    --out PATH          Explicit output file path (bypasses folder mode)
    --style NAME        Cover style key (default: read from folder manifest, else 'neural-cartography')
    --force             Overwrite existing cover.png
    --dry-run           Resolve prompt + config, don't call API
    --model             Override model (default: from brief frontmatter)

Environment:
    GOOGLE_API_KEY      Required (or GEMINI_API_KEY)
    KATIB_DEBUG=1       Verbose trace output
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get("KATIB_DEBUG") == "1"

IMAGE_MODELS = {
    "nano-banana-2": "gemini-3-pro-image-preview",
    "nano-banana": "gemini-2.5-flash-image",
}

# Aspect ratios accepted by the Gemini image API.
VALID_ASPECTS = {"1:1", "2:3", "3:2", "16:9", "9:16", "21:9"}

# Cost estimate (USD) per image for the Gemini Nano Banana tier.
COST_USD = {
    "gemini-3-pro-image-preview": 0.12,
    "gemini-2.5-flash-image": 0.04,
}


def _log(msg: str) -> None:
    if DEBUG:
        print(f"[cover] {msg}", file=sys.stderr)


# ─── Brief parsing ──────────────────────────────────────────────────

def parse_brief(brief_path: Path) -> dict[str, Any]:
    """Parse brief.md: YAML frontmatter + a section titled `## Prompt …` (body = prompt).

    Returns {engine, model, aspect, size, temperature, prompt, negative_prompt}.
    """
    import yaml

    text = brief_path.read_text(encoding="utf-8")

    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    frontmatter: dict[str, Any] = {}
    body = text
    if fm_match:
        frontmatter = yaml.safe_load(fm_match.group(1)) or {}
        body = text[fm_match.end():]

    # Extract the prompt — the first paragraph after a heading containing "Prompt"
    prompt = _extract_section_blockquote(body, heading_contains="Prompt") or ""
    negative_prompt = _extract_section_blockquote(body, heading_contains="Negative prompt") or ""

    if not prompt.strip():
        # Fallback: any blockquote
        prompt = _extract_first_blockquote(body) or ""

    # PyYAML parses `9:16` as sexagesimal int (9*60+16 = 556). Coerce & repair.
    aspect_raw = frontmatter.get("aspect", "9:16")
    aspect = _coerce_aspect(aspect_raw)

    return {
        "engine": frontmatter.get("engine", "gemini"),
        "model": frontmatter.get("model", "nano-banana-2"),
        "aspect": aspect,
        "size": str(frontmatter.get("size", "4K")),
        "temperature": frontmatter.get("temperature", 0.7),
        "text_in_image": frontmatter.get("text_in_image", False),
        "prompt": prompt.strip(),
        "negative_prompt": negative_prompt.strip(),
    }


def _coerce_aspect(raw: Any) -> str:
    """Accept '9:16', 556 (= 9*60+16), or 9.16 and return canonical 'W:H' form."""
    if isinstance(raw, str) and ":" in raw:
        return raw
    if isinstance(raw, int):
        # Sexagesimal: seconds = h*3600 + m*60 + s. For small ratios: val = W*60 + H
        if 0 < raw < 10000:
            w, h = divmod(raw, 60)
            if w > 0 and h > 0:
                return f"{w}:{h}"
    if isinstance(raw, float):
        s = f"{raw:.2f}"
        w, _, h = s.partition(".")
        return f"{int(w)}:{int(h)}"
    return str(raw)


def _extract_section_blockquote(md: str, *, heading_contains: str) -> str | None:
    """Find a `## <heading>` that contains the given substring, return blockquote body under it."""
    pattern = re.compile(
        rf"^##\s+.*{re.escape(heading_contains)}.*?\n(.+?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(md)
    if not m:
        return None
    section = m.group(1)
    # Collect blockquote lines (markdown `> ...`)
    quote_lines = []
    for line in section.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(">"):
            quote_lines.append(stripped[1:].lstrip())
        elif quote_lines and not stripped:
            # Blank line inside blockquote — keep as paragraph break
            continue
        elif quote_lines:
            # Non-blockquote line after quote started → stop
            break
    if not quote_lines:
        # No blockquote — return the first non-empty paragraph instead
        for para in section.strip().split("\n\n"):
            if para.strip():
                return para.strip()
        return None
    return " ".join(quote_lines).strip()


def _extract_first_blockquote(md: str) -> str | None:
    quote_lines = []
    for line in md.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(">"):
            quote_lines.append(stripped[1:].lstrip())
        elif quote_lines:
            break
    return " ".join(quote_lines).strip() if quote_lines else None


# ─── Manifest inspection ─────────────────────────────────────────────

def read_cover_style_from_folder(folder: Path) -> str | None:
    """Read `cover_style:` from the folder's manifest.md frontmatter, if present."""
    manifest = folder / "manifest.md"
    if not manifest.exists():
        return None
    text = manifest.read_text(encoding="utf-8")
    m = re.search(r"^cover_style:\s*([^\s#]+)", text, re.MULTILINE)
    return m.group(1).strip() if m else None


# ─── Gemini call ─────────────────────────────────────────────────────

def _get_google_client():
    home_env = os.path.expanduser("~/.env")
    if os.path.exists(home_env):
        load_dotenv(home_env, override=False)

    from google import genai
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("✗ GOOGLE_API_KEY or GEMINI_API_KEY not set. Add to ~/.zshrc or ~/.env", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)


def _extract_image_bytes(part) -> bytes | None:
    """Pull PNG bytes out of a Gemini response part."""
    if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
        data = part.inline_data.data
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            import base64
            try:
                return base64.b64decode(data)
            except Exception:
                return None
    try:
        img = part.as_image()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return None


def generate_image(
    prompt: str,
    *,
    model: str,
    aspect: str,
    negative_prompt: str = "",
) -> bytes:
    """Call Gemini once and return PNG bytes."""
    from google.genai import types

    if aspect not in VALID_ASPECTS:
        raise ValueError(f"aspect {aspect!r} not valid. Choose one of {sorted(VALID_ASPECTS)}")

    client = _get_google_client()

    full_prompt = prompt
    if negative_prompt:
        full_prompt = f"{prompt}\n\nAvoid: {negative_prompt}"

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect),
    )

    _log(f"calling {model} (aspect={aspect}, prompt chars={len(full_prompt)})")
    resp = client.models.generate_content(model=model, contents=full_prompt, config=config)

    for part in resp.parts:
        bytes_ = _extract_image_bytes(part)
        if bytes_:
            return bytes_
    raise RuntimeError("Gemini returned no image bytes. Check API key + model availability.")


# ─── Main flow ───────────────────────────────────────────────────────

def resolve_brief(style: str) -> Path:
    brief = SKILL_ROOT / "styles" / "covers" / style / "brief.md"
    if not brief.exists():
        print(f"✗ style not found: {brief}", file=sys.stderr)
        print(f"  Known styles: {[p.name for p in (SKILL_ROOT / 'styles' / 'covers').iterdir() if p.is_dir()]}", file=sys.stderr)
        sys.exit(1)
    return brief


def resolve_output_path(args) -> Path:
    if args.out:
        return Path(args.out).expanduser().resolve()
    if args.folder:
        folder = Path(args.folder).expanduser().resolve()
        if not folder.exists():
            print(f"✗ folder not found: {folder}", file=sys.stderr)
            sys.exit(1)
        assets = folder / "assets"
        assets.mkdir(exist_ok=True)
        return assets / "cover.png"
    print("✗ either --folder or --out is required", file=sys.stderr)
    sys.exit(1)


def resolve_style(args) -> str:
    if args.style:
        return args.style
    if args.folder:
        found = read_cover_style_from_folder(Path(args.folder).expanduser().resolve())
        if found:
            _log(f"style from manifest: {found}")
            return found
    return "neural-cartography"


def write_meta(target: Path, meta: dict[str, Any]) -> Path:
    meta_path = target.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib cover generator (Gemini Nano Banana 2)")
    parser.add_argument("--folder", help="Katib generation folder (writes to <folder>/assets/cover.png)")
    parser.add_argument("--out", help="Explicit output path (bypasses folder mode)")
    parser.add_argument("--style", help="Cover style key (default: manifest cover_style or 'neural-cartography')")
    parser.add_argument("--force", action="store_true", help="Overwrite existing cover.png")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved prompt/config, do not call API")
    parser.add_argument("--model", help="Override model (e.g., 'nano-banana-2' or full model id)")
    parser.add_argument("--aspect", help="Override aspect ratio (e.g., '9:16')")
    args = parser.parse_args()

    style = resolve_style(args)
    brief_path = resolve_brief(style)
    brief = parse_brief(brief_path)

    engine = brief.get("engine", "gemini")
    model_key = args.model or brief["model"]
    model_id = IMAGE_MODELS.get(model_key, model_key)
    aspect = args.aspect or brief["aspect"]
    prompt = brief["prompt"]
    negative = brief["negative_prompt"]

    # CSS-only covers (e.g., minimalist-typographic) have no image — the
    # template renders the cover inline. Skip Gemini entirely.
    if engine == "css":
        print(f"✓ style '{style}' uses engine=css — no image generated (rendered inline by template)")
        return 0

    if engine != "gemini":
        print(f"✗ unknown cover engine {engine!r} in {brief_path}. Expected 'gemini' or 'css'.", file=sys.stderr)
        return 1

    if not prompt:
        print(f"✗ no prompt found in {brief_path}", file=sys.stderr)
        return 1

    target = resolve_output_path(args)

    if args.dry_run:
        print("DRY RUN — not calling API")
        print(f"  style:  {style}")
        print(f"  model:  {model_id}")
        print(f"  aspect: {aspect}")
        print(f"  target: {target}")
        print(f"  prompt ({len(prompt)} chars):")
        print(f"    {prompt[:240]}{'…' if len(prompt) > 240 else ''}")
        if negative:
            print(f"  negative:")
            print(f"    {negative[:160]}{'…' if len(negative) > 160 else ''}")
        return 0

    if target.exists() and not args.force:
        print(f"✓ cover exists (use --force to regenerate): {target}")
        return 0

    print(f"Generating cover · {style} · {model_id} · {aspect}", file=sys.stderr)
    try:
        png_bytes = generate_image(prompt, model=model_id, aspect=aspect, negative_prompt=negative)
    except Exception as e:
        print(f"✗ Gemini call failed: {e}", file=sys.stderr)
        return 2

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(png_bytes)

    # Sidecar metadata — what we sent, what we got
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(png_bytes))
        width, height = img.size
    except Exception:
        width = height = None

    meta = {
        "type": "cover",
        "style": style,
        "model": model_id,
        "aspect": aspect,
        "prompt": prompt,
        "negative_prompt": negative,
        "width": width,
        "height": height,
        "bytes": len(png_bytes),
        "cost_usd_est": COST_USD.get(model_id, 0.0),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "brief": str(brief_path.relative_to(SKILL_ROOT)),
    }
    meta_path = write_meta(target, meta)

    size_kb = len(png_bytes) / 1024
    dim = f"{width}×{height}" if width else "?"
    print(f"✓ cover saved · {dim} · {size_kb:.0f} KB · ~${meta['cost_usd_est']:.2f}")
    print(f"  → {target}")
    print(f"  meta: {meta_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
