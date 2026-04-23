"""Inline-SVG provider — chart SVG generation.

Renders simple charts from data as SVG strings that embed directly in
component HTML (no file on disk). Deterministic: same spec -> identical
string. Small enough that inline embedding beats caching on disk.

Supported chart types:
    donut      — proportional breakdown
    bar        — horizontal bars
    sparkline  — flat trendline

Colors always come from the spec — the provider never holds a default
palette. compose.py injects `colors` from merged tokens (`charts.palette`)
before calling the provider. That keeps the provider stateless and makes
brand overrides cascade automatically.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from core.image.base import ProviderError, ResolvedImage

_AXIS_FALLBACK = "#7A7268"


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
        elif chart_type == "bar":
            svg = render_bar(spec)
        elif chart_type == "sparkline":
            svg = render_sparkline(spec)
        else:
            raise ProviderError(
                f"inline-svg: unknown chart type {chart_type!r}. "
                f"Supported: donut, bar, sparkline"
            )
        return ResolvedImage(
            inline_svg=svg,
            content_hash=self.cache_key(spec),
            alt_hint=spec.get("alt_text") or spec.get("title"),
        )


def _require_palette(spec: dict, kind: str) -> list[str]:
    colors = spec.get("colors")
    if not colors:
        raise ProviderError(
            f"{kind}: `colors` not provided. compose() injects "
            f"charts.palette automatically; if calling the provider directly, "
            f"pass an explicit `colors` array."
        )
    if not isinstance(colors, list) or not all(isinstance(c, str) for c in colors):
        raise ProviderError(f"{kind}: `colors` must be a list of hex strings")
    return colors


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

    palette = _require_palette(spec, "donut")

    segments: list[str] = []
    rotation = -90.0
    for i, d in enumerate(data):
        pct = d["value"] / total
        if pct <= 0:
            continue
        dash = pct * circumference
        gap = circumference - dash
        color = d.get("color") or palette[i % len(palette)]
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
        f'role="img" aria-label="{_esc(title)}">'
        f"<title>{_esc(title)}</title>"
        + "".join(segments)
        + "</svg>"
    )


def render_bar(spec: dict) -> str:
    """Horizontal bar chart. Bars grow inward from the language-origin side.

    EN: axis on left, bars grow right.
    AR: axis on right, bars grow left.
    """
    data = spec.get("data")
    if not data:
        raise ProviderError("bar: `data` is required (list of {label, value})")

    values = [d.get("value", 0) for d in data]
    if any(v < 0 for v in values):
        raise ProviderError("bar: negative values not supported")
    max_v = max(values) if values else 0
    if max_v == 0:
        raise ProviderError("bar: all values are zero")

    palette = _require_palette(spec, "bar")
    lang = spec.get("lang", "en")
    rtl = lang == "ar"

    width = int(spec.get("width", 600))
    bar_height = int(spec.get("bar_height", 20))
    bar_gap = int(spec.get("bar_gap", 12))
    pad_top = 12
    pad_bottom = 12
    label_gutter = int(spec.get("label_gutter", 140))
    value_gutter = 56

    height = pad_top + pad_bottom + len(data) * bar_height + max(0, len(data) - 1) * bar_gap
    plot_w = max(0, width - label_gutter - value_gutter)

    if rtl:
        axis_x = width - label_gutter
    else:
        axis_x = label_gutter

    axis_color = spec.get("axis_color", _AXIS_FALLBACK)
    title = spec.get("title", "bar chart")

    parts: list[str] = [
        f'<line x1="{axis_x}" y1="{pad_top}" x2="{axis_x}" '
        f'y2="{height - pad_bottom}" stroke="{axis_color}" stroke-width="1" />'
    ]

    for i, d in enumerate(data):
        value = d.get("value", 0)
        label = str(d.get("label", ""))
        bar_w = (value / max_v) * plot_w if max_v else 0
        y = pad_top + i * (bar_height + bar_gap)
        color = d.get("color") or palette[i % len(palette)]

        if rtl:
            rect_x = axis_x - bar_w
            label_x = axis_x + 8
            label_anchor = "start"
            value_x = rect_x - 6
            value_anchor = "end"
        else:
            rect_x = axis_x
            label_x = axis_x - 8
            label_anchor = "end"
            value_x = rect_x + bar_w + 6
            value_anchor = "start"

        text_y = y + bar_height * 0.72

        parts.append(
            f'<rect x="{rect_x:.2f}" y="{y}" width="{bar_w:.2f}" '
            f'height="{bar_height}" fill="{color}" rx="2" />'
        )
        parts.append(
            f'<text x="{label_x}" y="{text_y:.1f}" '
            f'text-anchor="{label_anchor}" font-size="10" '
            f'fill="#141414">{_esc(label)}</text>'
        )
        parts.append(
            f'<text x="{value_x:.2f}" y="{text_y:.1f}" '
            f'text-anchor="{value_anchor}" font-size="10" '
            f'fill="#4A4A4A">{_fmt_num(value)}</text>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{_esc(title)}">'
        f"<title>{_esc(title)}</title>"
        + "".join(parts)
        + "</svg>"
    )


def render_sparkline(spec: dict) -> str:
    """Flat trendline. Line direction is always left-to-right regardless of
    lang — chronological convention in data-vis, time flows LTR universally.
    """
    data = spec.get("data")
    if data is None:
        raise ProviderError("sparkline: `data` is required (list of numbers)")
    data = list(data)
    if len(data) == 0:
        raise ProviderError("sparkline: `data` is empty")
    for v in data:
        if not isinstance(v, (int, float)):
            raise ProviderError(f"sparkline: non-numeric value {v!r} in data")

    palette = _require_palette(spec, "sparkline")
    line_color = palette[0]
    area_color = palette[1] if len(palette) > 1 else palette[0]

    width = int(spec.get("width", 600))
    height = int(spec.get("height", 80))
    pad = 6

    title = spec.get("title", "sparkline")

    if len(data) == 1:
        cx = width / 2
        cy = height / 2
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="{_esc(title)}">'
            f"<title>{_esc(title)}</title>"
            f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{line_color}" />'
            "</svg>"
        )

    mn = min(data)
    mx = max(data)
    plot_w = width - 2 * pad
    plot_h = height - 2 * pad

    def _x(i: int) -> float:
        return pad + (i / (len(data) - 1)) * plot_w

    if mx == mn:
        mid = height / 2
        points = [(_x(i), mid) for i in range(len(data))]
    else:
        span = mx - mn
        points = [
            (_x(i), pad + (1 - (v - mn) / span) * plot_h) for i, v in enumerate(data)
        ]

    poly = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    area_path = (
        f"M {points[0][0]:.2f},{height - pad} "
        + " ".join(f"L {x:.2f},{y:.2f}" for x, y in points)
        + f" L {points[-1][0]:.2f},{height - pad} Z"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{_esc(title)}">'
        f"<title>{_esc(title)}</title>"
        f'<path d="{area_path}" fill="{area_color}" fill-opacity="0.18" />'
        f'<polyline points="{poly}" fill="none" stroke="{line_color}" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" />'
        "</svg>"
    )


def _fmt_num(v: float | int) -> str:
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer()):
        return f"{int(v)}"
    return f"{v:.1f}"


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
