"""Phase 2 Day 6 — chart-donut + chart-bar + chart-sparkline."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.compose import compose, load_component
from core.image.inline_svg import (
    InlineSvgProvider,
    render_bar,
    render_sparkline,
)
from core.render import render_to_pdf
from core.tokens import load_base_tokens

REPO_ROOT = Path(__file__).resolve().parent.parent


# -------- tokens --------

def test_charts_palette_in_base_tokens():
    base = load_base_tokens()
    assert "charts" in base
    palette = base["charts"]["palette"]
    assert isinstance(palette, list)
    assert len(palette) == 8
    assert all(isinstance(c, str) and c.startswith("#") for c in palette)


# -------- schema / wiring --------

@pytest.mark.parametrize("name", ["chart-donut", "chart-bar", "chart-sparkline"])
def test_chart_section_validates(name):
    c = load_component(name)
    assert c["tier"] == "section"
    assert c["languages"] == ["en", "ar"]


@pytest.mark.parametrize("name", ["chart-donut", "chart-bar", "chart-sparkline"])
def test_chart_section_only_accepts_inline_svg(name):
    c = load_component(name)
    chart_decl = next(
        (
            next(iter(i.values()))
            for i in c["accepts"]["inputs"]
            if "chart" in i
        ),
        None,
    )
    assert chart_decl is not None
    assert chart_decl["sources_accepted"] == ["inline-svg"]


# -------- bar renderer --------

def test_bar_rejects_empty_data():
    with pytest.raises(Exception, match="data"):
        render_bar({"data": [], "colors": ["#000"]})


def test_bar_rejects_all_zero():
    with pytest.raises(Exception, match="zero"):
        render_bar({"data": [{"label": "a", "value": 0}], "colors": ["#000"]})


def test_bar_rejects_negative():
    with pytest.raises(Exception, match="negative"):
        render_bar({
            "data": [{"label": "a", "value": -5}],
            "colors": ["#000"],
        })


def test_bar_requires_palette():
    with pytest.raises(Exception, match="colors"):
        render_bar({"data": [{"label": "a", "value": 10}]})


def test_bar_en_axis_on_left():
    svg = render_bar({
        "data": [{"label": "X", "value": 100}, {"label": "Y", "value": 50}],
        "colors": ["#111", "#222"],
        "lang": "en",
        "width": 600,
        "label_gutter": 140,
    })
    # axis line: x1 == label_gutter (140) for EN
    assert 'x1="140"' in svg
    # first bar rect starts at axis_x (140) — rightward growth
    assert 'x="140.00"' in svg


def test_bar_ar_axis_on_right():
    svg = render_bar({
        "data": [{"label": "X", "value": 100}, {"label": "Y", "value": 50}],
        "colors": ["#111", "#222"],
        "lang": "ar",
        "width": 600,
        "label_gutter": 140,
    })
    # axis line: x1 == width - label_gutter (460) for AR
    assert 'x1="460"' in svg
    # no bar rect should start at 140 (that would be EN mode)
    assert 'x="140.00"' not in svg


# -------- sparkline renderer --------

def test_sparkline_rejects_empty():
    with pytest.raises(Exception, match="empty"):
        render_sparkline({"data": [], "colors": ["#000"]})


def test_sparkline_single_point_renders_dot():
    svg = render_sparkline({"data": [42], "colors": ["#111"]})
    assert "<circle" in svg
    assert "<polyline" not in svg


def test_sparkline_allows_negatives():
    svg = render_sparkline({
        "data": [-5, -2, 0, 3, 7],
        "colors": ["#111", "#222"],
    })
    assert "<polyline" in svg


def test_sparkline_flat_line_renders_mid():
    svg = render_sparkline({"data": [10, 10, 10, 10], "colors": ["#111"]})
    assert "<polyline" in svg


def test_sparkline_direction_always_ltr():
    """First point should have x==pad, last should have x~width-pad, regardless of lang."""
    data = [1, 2, 3, 4, 5]
    svg_en = render_sparkline({"data": data, "colors": ["#111", "#222"], "lang": "en", "width": 600})
    svg_ar = render_sparkline({"data": data, "colors": ["#111", "#222"], "lang": "ar", "width": 600})
    # direction is baked into the path — identical regardless of lang
    assert svg_en.replace('aria-label=""', '') == svg_ar.replace('aria-label=""', '')


# -------- provider dispatch --------

def test_provider_dispatches_bar():
    p = InlineSvgProvider()
    img = p.resolve(
        {"type": "bar", "data": [{"label": "A", "value": 10}], "colors": ["#111"]},
        Path("/tmp"),
    )
    assert img.inline_svg
    assert "<rect" in img.inline_svg


def test_provider_dispatches_sparkline():
    p = InlineSvgProvider()
    img = p.resolve(
        {"type": "sparkline", "data": [1, 2, 3], "colors": ["#111", "#222"]},
        Path("/tmp"),
    )
    assert img.inline_svg
    assert "<polyline" in img.inline_svg


def test_provider_rejects_unknown_type():
    p = InlineSvgProvider()
    with pytest.raises(Exception, match="unknown chart type"):
        p.resolve({"type": "pie", "data": []}, Path("/tmp"))


# -------- compose integration --------

def test_compose_injects_palette_into_inline_svg(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: palette-inject\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: chart-donut\n"
        "    inputs:\n"
        "      heading: Test\n"
        "      chart:\n"
        "        source: inline-svg\n"
        "        type: donut\n"
        "        data:\n"
        "          - {label: A, value: 10}\n"
        "          - {label: B, value: 20}\n"
        "      alt_text: test donut\n"
    )
    html, _ = compose(str(rfile), "en")
    # palette[0] from base tokens is #1F3A68 — should appear in resolved SVG
    assert "#1F3A68" in html
    # palette[1] is #D4A437
    assert "#D4A437" in html


def test_compose_recipe_colors_override_palette(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: palette-override\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: chart-donut\n"
        "    inputs:\n"
        "      heading: Test\n"
        "      chart:\n"
        "        source: inline-svg\n"
        "        type: donut\n"
        "        data:\n"
        "          - {label: A, value: 10}\n"
        "        colors: ['#FF00FF']\n"
        "      alt_text: test\n"
    )
    html, _ = compose(str(rfile), "en")
    # override color is used as SVG stroke
    assert 'stroke="#FF00FF"' in html
    # default palette[0] is not applied as an SVG stroke (it appears in --accent
    # CSS var, but should NOT be the donut segment color when recipe overrides)
    assert 'stroke="#1F3A68"' not in html


def test_compose_rejects_non_inline_svg_for_chart(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: bad-source\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: chart-bar\n"
        "    inputs:\n"
        "      heading: Test\n"
        "      chart:\n"
        "        source: user-file\n"
        "        path: /tmp/nope.png\n"
        "      alt_text: test\n"
    )
    with pytest.raises(Exception, match="sources_accepted"):
        compose(str(rfile), "en")


def test_sr_only_data_table_emitted(tmp_path):
    rfile = tmp_path / "r.yaml"
    rfile.write_text(
        "name: sr-test\n"
        "version: 0.1.0\n"
        "namespace: katib\n"
        "languages: [en]\n"
        "sections:\n"
        "  - component: chart-donut\n"
        "    inputs:\n"
        "      heading: Test\n"
        "      chart:\n"
        "        source: inline-svg\n"
        "        type: donut\n"
        "        data:\n"
        "          - {label: Alpha, value: 10}\n"
        "          - {label: Beta, value: 20}\n"
        "      alt_text: test donut\n"
    )
    html, _ = compose(str(rfile), "en")
    assert 'class="katib-sr-only"' in html
    assert "<table" in html
    assert "Alpha" in html
    assert "Beta" in html


# -------- end-to-end --------

def test_day6_showcase_renders_en(tmp_path):
    html, _ = compose("phase-2-day6-showcase", "en")
    assert "katib-chart-donut" in html
    assert "katib-chart-bar" in html
    assert "katib-sparkline" in html
    pdf = render_to_pdf(html, tmp_path / "d6.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 15000


def test_day6_showcase_renders_ar(tmp_path):
    html, _ = compose("phase-2-day6-showcase", "ar")
    assert 'dir="rtl"' in html
    pdf = render_to_pdf(html, tmp_path / "d6.ar.pdf", base_url=REPO_ROOT)
    assert pdf.stat().st_size > 15000
