#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0",
# ]
# ///
"""Katib screenshot framer — wraps a PNG in browser-chrome.

Adds a title bar + url bar above the screenshot so it reads as a real browser
shot in print, not a naked rectangle. DPI-aware: chrome scales with the
source's pixel width.

Usage:
    uv run scripts/frame.py shot.png                     # Mac-style, light
    uv run scripts/frame.py shot.png --chrome generic
    uv run scripts/frame.py shot.png --chrome none       # no-op pass-through
    uv run scripts/frame.py shot.png --url https://...
    uv run scripts/frame.py shot.png --theme dark

Input resolution rules:
    - Source PNG must exist.
    - URL is read from --url, or from <shot>.meta.json, else left blank.

Output:
    <shot>.framed.png   (or --out PATH)
    <shot>.framed.meta.json — merged from source meta + framing info
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRAFFIC_COLORS = [(255, 95, 87), (254, 188, 46), (40, 200, 64)]  # red, yellow, green

THEMES = {
    "light": {
        "chrome_bg": (240, 240, 240),
        "chrome_border": (210, 210, 210),
        "url_bg": (255, 255, 255),
        "url_border": (220, 220, 220),
        "url_fg": (80, 80, 80),
        "shadow": (0, 0, 0, 40),
    },
    "dark": {
        "chrome_bg": (42, 42, 42),
        "chrome_border": (70, 70, 70),
        "url_bg": (30, 30, 30),
        "url_border": (60, 60, 60),
        "url_fg": (200, 200, 200),
        "shadow": (0, 0, 0, 80),
    },
}


def read_meta(src: Path) -> dict[str, Any]:
    meta_path = src.with_suffix(".meta.json")
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def resolve_font(size_px: int):
    from PIL import ImageFont
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size_px)
            except Exception:
                continue
    return ImageFont.load_default()


def render_mac_chrome(img, *, url: str, theme: str, scale: float):
    """Overlay a Mac-style title bar with traffic lights + url bar onto a new canvas."""
    from PIL import Image, ImageDraw

    theme_cfg = THEMES[theme]
    W, H = img.size
    chrome_h = int(round(72 * scale))  # 36px at 1x
    traffic_r = int(round(7 * scale))
    traffic_gap = int(round(9 * scale))
    traffic_margin = int(round(18 * scale))
    url_font_px = int(round(13 * scale))
    url_h = int(round(30 * scale))
    url_margin_x = int(round(110 * scale))
    url_padding_x = int(round(14 * scale))
    border_px = max(1, int(round(1 * scale)))

    canvas = Image.new("RGBA", (W, H + chrome_h), theme_cfg["chrome_bg"])
    draw = ImageDraw.Draw(canvas)

    # Bottom border of chrome (separation line)
    draw.rectangle(
        (0, chrome_h - border_px, W, chrome_h),
        fill=theme_cfg["chrome_border"],
    )

    # Traffic lights
    cy = chrome_h // 2
    cx = traffic_margin + traffic_r
    for color in TRAFFIC_COLORS:
        draw.ellipse((cx - traffic_r, cy - traffic_r, cx + traffic_r, cy + traffic_r), fill=color)
        cx += traffic_r * 2 + traffic_gap

    # URL bar (rounded rect)
    url_left = url_margin_x
    url_right = W - url_margin_x
    url_top = cy - url_h // 2
    url_bot = url_top + url_h
    radius = url_h // 2
    draw.rounded_rectangle(
        (url_left, url_top, url_right, url_bot),
        radius=radius,
        fill=theme_cfg["url_bg"],
        outline=theme_cfg["url_border"],
        width=border_px,
    )

    if url:
        font = resolve_font(url_font_px)
        # Truncate URL if needed
        max_px = (url_right - url_left) - 2 * url_padding_x
        text = url
        for _ in range(4):
            try:
                bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
                tw = bbox[2] - bbox[0]
            except Exception:
                tw = len(text) * url_font_px * 0.55
            if tw <= max_px or len(text) < 12:
                break
            text = text[: int(len(text) * 0.75)] + "…"
        try:
            bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
            th = bbox[3] - bbox[1]
            tx = url_left + url_padding_x - bbox[0]
            ty = cy - th / 2 - bbox[1]
        except Exception:
            tx = url_left + url_padding_x
            ty = cy - url_font_px / 2
        draw.text((tx, ty), text, fill=theme_cfg["url_fg"], font=font)

    # Paste the screenshot underneath the chrome
    canvas.paste(img, (0, chrome_h), img if img.mode == "RGBA" else None)
    return canvas


def render_generic_chrome(img, *, url: str, theme: str, scale: float):
    """Minimal flat chrome — url bar only, no traffic lights. Platform-neutral."""
    from PIL import Image, ImageDraw

    theme_cfg = THEMES[theme]
    W, H = img.size
    chrome_h = int(round(48 * scale))
    url_font_px = int(round(13 * scale))
    url_h = int(round(28 * scale))
    url_margin_x = int(round(24 * scale))
    url_padding_x = int(round(12 * scale))
    border_px = max(1, int(round(1 * scale)))

    canvas = Image.new("RGBA", (W, H + chrome_h), theme_cfg["chrome_bg"])
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, chrome_h - border_px, W, chrome_h), fill=theme_cfg["chrome_border"])

    cy = chrome_h // 2
    url_left = url_margin_x
    url_right = W - url_margin_x
    url_top = cy - url_h // 2
    url_bot = url_top + url_h
    draw.rounded_rectangle(
        (url_left, url_top, url_right, url_bot),
        radius=int(round(4 * scale)),
        fill=theme_cfg["url_bg"],
        outline=theme_cfg["url_border"],
        width=border_px,
    )

    if url:
        font = resolve_font(url_font_px)
        try:
            bbox = draw.textbbox((0, 0), url, font=font, anchor="lt")
            th = bbox[3] - bbox[1]
            tx = url_left + url_padding_x - bbox[0]
            ty = cy - th / 2 - bbox[1]
        except Exception:
            tx = url_left + url_padding_x
            ty = cy - url_font_px / 2
        draw.text((tx, ty), url, fill=theme_cfg["url_fg"], font=font)

    canvas.paste(img, (0, chrome_h), img if img.mode == "RGBA" else None)
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib screenshot framer — browser chrome wrapper")
    parser.add_argument("image", help="Source PNG path")
    parser.add_argument("--out", help="Output PNG path (default: <image>.framed.png)")
    parser.add_argument("--chrome", default="mac", choices=["mac", "generic", "none"], help="Chrome style (default: mac)")
    parser.add_argument("--theme", default="light", choices=["light", "dark"], help="Chrome theme (default: light)")
    parser.add_argument("--url", help="URL displayed in the url bar (default: from <image>.meta.json)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved config, don't render")
    args = parser.parse_args()

    src = Path(args.image).expanduser().resolve()
    if not src.exists():
        print(f"✗ source image not found: {src}", file=sys.stderr)
        return 1

    source_meta = read_meta(src)
    url = args.url if args.url is not None else source_meta.get("url", "")

    if args.out:
        out = Path(args.out).expanduser().resolve()
    else:
        # shot.png → shot.framed.png ; shot.annot.png → shot.annot.framed.png
        out = src.with_suffix(".framed.png") if src.suffix == ".png" else src.with_name(src.stem + ".framed.png")

    if args.dry_run:
        print("DRY RUN — not writing framed image")
        print(f"  source: {src}")
        print(f"  out:    {out}")
        print(f"  chrome: {args.chrome}")
        print(f"  theme:  {args.theme}")
        print(f"  url:    {url or '(blank)'}")
        return 0

    if out.exists() and not args.force:
        print(f"✓ framed image exists (use --force): {out}")
        return 0

    try:
        from PIL import Image
    except ImportError:
        print("✗ pillow not installed. Run via `uv run` or `pip install pillow`", file=sys.stderr)
        return 1

    img = Image.open(src).convert("RGBA")
    W = img.size[0]
    scale = max(1.0, W / 1440.0)

    if args.chrome == "none":
        img.convert("RGB").save(out, format="PNG", optimize=True)
    elif args.chrome == "mac":
        framed = render_mac_chrome(img, url=url, theme=args.theme, scale=scale)
        framed.convert("RGB").save(out, format="PNG", optimize=True)
    elif args.chrome == "generic":
        framed = render_generic_chrome(img, url=url, theme=args.theme, scale=scale)
        framed.convert("RGB").save(out, format="PNG", optimize=True)

    # Sidecar — merge framing info into source meta
    meta_path = out.with_suffix(".meta.json")
    existing = dict(source_meta)
    existing.update({
        "framed_from": src.name,
        "chrome": args.chrome,
        "theme": args.theme,
        "url_shown": url,
        "framed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    meta_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")

    size = out.stat().st_size
    print(f"✓ framed · {args.chrome} chrome, {args.theme} theme · {size/1024:.0f} KB")
    print(f"  → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
