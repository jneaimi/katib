"""Inline-SVG provider — chart SVG generation.

Renders simple charts from data as SVG strings that embed directly in
component HTML (no file on disk). Phase 1 ships one chart type: `donut`.
Additional types (`bar`, `sparkline`, `process-flow`) land in later
phases when components actually consume them.

SVG is generated deterministically (same spec -> identical string) and
is small enough that inline embedding is simpler than caching on disk.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from core.image.base import ProviderError, ResolvedImage

DEFAULT_PALETTE = [
    "#1F3A68", "#D4A437", "#3A7D8B", "#C85A3E",
    "#5A8549", "#B8842A", "#7A7268", "#B53E3E",
]


class InlineSvgProvider:
    name = "inline-svg"

    def is_available(self) -> tuple[bool, str]:
        return True, ""

    def cache_key(self, spec: dict) -> str:
        blob = json.dumps(spec, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]

    def resolve(self, spec: dict, cache_dir: Path) -> ResolvedImage:
        chart_type = spec.get("type") or spec.get("chart_type") or "donut"
        if chart_type == "donut":
            svg = render_donut(spec)
        else:
            raise ProviderError(
                f"inline-svg: unknown chart type {chart_type!r}. "
                f"Phase 1 supports: donut"
            )
        return ResolvedImage(
            inline_svg=svg,
            content_hash=self.cache_key(spec),
            alt_hint=spec.get("alt_text") or spec.get("title"),
        )


def render_donut(spec: dict) -> str:
    data = spec.get("data")
    if not data:
        raise ProviderError("donut: `data` is required (list of {label, value})")

    total = sum(d.get("value", 0) for d in data)
    if total == 0:
        raise ProviderError("donut: all values are zero")

    size = int(spec.get("size", 200))
    stroke = int(spec.get("stroke", 28))
    cx = cy = size / 2
    r = (size - stroke) / 2
    circumference = 2 * math.pi * r

    palette = spec.get("colors") or DEFAULT_PALETTE

    segments: list[str] = []
    rotation = -90.0
    for i, d in enumerate(data):
        pct = d["value"] / total
        if pct <= 0:
            continue
        dash = pct * circumference
        gap = circumference - dash
        color = palette[i % len(palette)]
        segments.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="none" '
            f'stroke="{color}" stroke-width="{stroke}" '
            f'stroke-dasharray="{dash:.2f} {gap:.2f}" '
            f'stroke-dashoffset="0" '
            f'transform="rotate({rotation:.2f} {cx} {cy})" />'
        )
        rotation += pct * 360.0

    title = spec.get("title", "donut chart")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" role="img" aria-label="{title}">'
        + "".join(segments)
        + "</svg>"
    )
