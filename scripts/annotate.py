#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0",
# ]
# ///
"""Katib screenshot annotator — arrows, numbered callouts, blur rects.

Reads an annotation spec (JSON) and a source PNG, writes an annotated PNG
to `<source>.annot.png`. DPI-aware — scales strokes & fonts based on the
actual pixel dimensions of the source image.

Spec format (image.annot.json):
{
  "callouts": [
    {"n": 1, "at": [1200, 400]},
    {"n": 2, "at": [1600, 800]}
  ],
  "arrows": [
    {"from": [100, 200], "to": [400, 500]}
  ],
  "blurs": [
    {"box": [100, 100, 300, 200]}
  ]
}

Coordinates are in the source image's pixel space. For a retina (2x)
screenshot at 2880x1800, use coordinates up to (2880, 1800).

RTL: pass --lang ar. Currently only affects label-side heuristics; callout
numbers stay numeric (1, 2, 3) regardless of language.

Usage:
    uv run scripts/annotate.py shot.png              # auto-loads shot.annot.json
    uv run scripts/annotate.py shot.png --spec other.json
    uv run scripts/annotate.py shot.png --lang ar
    uv run scripts/annotate.py shot.png --dry-run
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CALLOUT_FILL = (200, 90, 62)       # terracotta (matches workbook accent)
CALLOUT_TEXT = (255, 255, 255)
ARROW_COLOR = (200, 90, 62)
BLUR_RADIUS_PX = 18                # at 1x — scaled up for retina


def load_spec(spec_path: Path) -> dict[str, Any]:
    try:
        data = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ annotation spec is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, dict):
        print(f"✗ annotation spec must be a JSON object, got {type(data).__name__}", file=sys.stderr)
        sys.exit(2)
    return data


def resolve_font(size_px: int):
    """Best available sans-serif font at requested pixel size. Falls back to PIL default."""
    from PIL import ImageFont
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # linux
    ):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size_px)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_callout(draw, *, n: int, at: tuple[int, int], radius: int, font, outline_px: int) -> None:
    cx, cy = at
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=CALLOUT_FILL,
        outline=(255, 255, 255),
        width=outline_px,
    )
    text = str(n)
    # Pillow 10+ uses textbbox for accurate centering
    try:
        bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, fill=CALLOUT_TEXT, font=font)
    except Exception:
        # Older Pillow
        draw.text((cx - radius / 3, cy - radius / 2), text, fill=CALLOUT_TEXT, font=font)


def draw_arrow(draw, *, start: tuple[int, int], end: tuple[int, int], stroke_px: int) -> None:
    sx, sy = start
    ex, ey = end
    # Shaft
    draw.line((sx, sy, ex, ey), fill=ARROW_COLOR, width=stroke_px)
    # Arrowhead — triangle at the tip, sized proportionally to stroke
    angle = math.atan2(ey - sy, ex - sx)
    head_len = max(stroke_px * 5, 18)
    head_half_w = max(stroke_px * 2.5, 9)
    # Two base points of the triangle
    p1 = (
        ex - head_len * math.cos(angle) + head_half_w * math.sin(angle),
        ey - head_len * math.sin(angle) - head_half_w * math.cos(angle),
    )
    p2 = (
        ex - head_len * math.cos(angle) - head_half_w * math.sin(angle),
        ey - head_len * math.sin(angle) + head_half_w * math.cos(angle),
    )
    draw.polygon([end, p1, p2], fill=ARROW_COLOR)


def apply_blur(img, *, box: tuple[int, int, int, int], radius: int):
    from PIL import ImageFilter
    # Clamp box to image bounds
    x0, y0, x1, y1 = box
    W, H = img.size
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    region = img.crop((x0, y0, x1, y1))
    blurred = region.filter(ImageFilter.GaussianBlur(radius=radius))
    img.paste(blurred, (x0, y0))


def main() -> int:
    parser = argparse.ArgumentParser(description="Katib screenshot annotator")
    parser.add_argument("image", help="Source PNG path")
    parser.add_argument("--spec", help="Annotation spec JSON (default: <image>.annot.json alongside source)")
    parser.add_argument("--out", help="Output PNG path (default: <image>.annot.png alongside source)")
    parser.add_argument("--lang", default="en", choices=["en", "ar"], help="Content language (affects label-side heuristics)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output")
    parser.add_argument("--dry-run", action="store_true", help="Validate spec, don't write")
    args = parser.parse_args()

    src = Path(args.image).expanduser().resolve()
    if not src.exists():
        print(f"✗ source image not found: {src}", file=sys.stderr)
        return 1

    # Default spec path — change `.png` → `.annot.json`
    spec_path = Path(args.spec).expanduser().resolve() if args.spec else src.with_suffix(".annot.json")
    if not spec_path.exists():
        print(f"✗ annotation spec not found: {spec_path}", file=sys.stderr)
        print(f"  Expected alongside source or specify with --spec", file=sys.stderr)
        return 1

    spec = load_spec(spec_path)

    callouts = spec.get("callouts", []) or []
    arrows = spec.get("arrows", []) or []
    blurs = spec.get("blurs", []) or []

    if not (callouts or arrows or blurs):
        print(f"⚠ annotation spec is empty: {spec_path}", file=sys.stderr)

    # Default output
    if args.out:
        out = Path(args.out).expanduser().resolve()
    else:
        out = src.with_suffix(".annot.png") if src.suffix == ".png" else src.with_name(src.stem + ".annot.png")

    if args.dry_run:
        print("DRY RUN — not writing annotated image")
        print(f"  source:   {src}")
        print(f"  spec:     {spec_path}")
        print(f"  out:      {out}")
        print(f"  callouts: {len(callouts)}")
        print(f"  arrows:   {len(arrows)}")
        print(f"  blurs:    {len(blurs)}")
        print(f"  lang:     {args.lang}")
        return 0

    if out.exists() and not args.force:
        print(f"✓ annotated image exists (use --force): {out}")
        return 0

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("✗ pillow not installed. Run via `uv run` or `pip install pillow`", file=sys.stderr)
        return 1

    img = Image.open(src).convert("RGBA")
    W, H = img.size

    # DPI scale — base at 1440px wide (laptop preset). Retina 2x = ~2880px.
    scale = max(1.0, W / 1440.0)
    stroke_px = int(round(4 * scale))
    callout_radius = int(round(18 * scale))
    callout_font_px = int(round(20 * scale))
    blur_radius = int(round(BLUR_RADIUS_PX * scale / 2))  # modest blur, still unreadable
    outline_px = max(1, int(round(2 * scale)))

    # Blurs first (under other annotations)
    for b in blurs:
        box = b.get("box")
        if not (isinstance(box, list) and len(box) == 4):
            print(f"⚠ skip blur — invalid box {box!r}", file=sys.stderr)
            continue
        apply_blur(img, box=tuple(box), radius=blur_radius)

    # Convert to RGBA draw surface for anti-aliased shapes
    draw = ImageDraw.Draw(img)
    font = resolve_font(callout_font_px)

    for a in arrows:
        src_pt = a.get("from")
        dst_pt = a.get("to")
        if not (isinstance(src_pt, list) and len(src_pt) == 2 and isinstance(dst_pt, list) and len(dst_pt) == 2):
            print(f"⚠ skip arrow — invalid endpoints {src_pt!r} → {dst_pt!r}", file=sys.stderr)
            continue
        draw_arrow(draw, start=tuple(src_pt), end=tuple(dst_pt), stroke_px=stroke_px)

    for c in callouts:
        n = c.get("n")
        at = c.get("at")
        if not isinstance(n, (int, str)) or not (isinstance(at, list) and len(at) == 2):
            print(f"⚠ skip callout — invalid spec {c!r}", file=sys.stderr)
            continue
        draw_callout(draw, n=n, at=tuple(at), radius=callout_radius, font=font, outline_px=outline_px)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, format="PNG", optimize=True)

    # Sidecar — merge onto existing meta if present
    meta_path = out.with_suffix(".meta.json")
    raw_meta_path = src.with_suffix(".meta.json")
    existing: dict[str, Any] = {}
    if raw_meta_path.exists():
        try:
            existing = json.loads(raw_meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    existing.update({
        "annotated_from": src.name,
        "annotations": {
            "callouts": len(callouts),
            "arrows": len(arrows),
            "blurs": len(blurs),
        },
        "lang": args.lang,
        "annotated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    meta_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")

    size = out.stat().st_size
    print(f"✓ annotated · {len(callouts)} callouts, {len(arrows)} arrows, {len(blurs)} blurs · {size/1024:.0f} KB")
    print(f"  → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
