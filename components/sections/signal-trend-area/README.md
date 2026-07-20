# signal-trend-area

**Tier:** section · **Namespace:** katib

## Purpose

Stacked-area trend chart for signal-volume-by-cluster over time. Used as Figure 0 in Signal Forge peer briefings — sits at the top of the brief and contextualises today against the last N run-days. Today's column is marked with a dashed amber rule and a "TODAY" annotation above the chart so a peer can read the chart in 2 seconds.

This is a **dumb renderer** — it takes pre-computed polygon points, axis ticks, and a chart-geometry box and draws them. The analytical work (SQL query, top-cluster selection, stacking math, polygon path generation) lives in the helper script `scripts/extract-signal-trend.py`. Run that script, paste its YAML output into the recipe under this component's `inputs:`.

## Variants

- default

## Inputs

| Field | Required | Type | Notes |
|---|---|---|---|
| `eyebrow` | optional | string | Small uppercase label above the chart |
| `title` | optional | string | Heading rendered above the eyebrow |
| `bands` | **required** | array | Stacked-area bands, bottom to top |
| `x_ticks` | **required** | array | X-axis ticks `[{x, label}]` |
| `y_ticks` | **required** | array | Y-axis ticks `[{y, label}]` |
| `today_x` | optional | number | X coordinate for the today highlight rule. Omit to skip highlight |
| `chart_geometry` | **required** | object | `{view_w, view_h, chart_top, chart_bottom, chart_left, chart_right}` |
| `caption` | optional | string | Italic note below the chart |

### Band shape

```yaml
- cluster: "AI agents in GCC"          # legend label
  color: "#F59E0B"                     # band fill
  points: "40.0,182.4 107.5,178.3 ..."  # full polygon point string (top L→R then bottom R→L)
  today_value: 191                     # optional, shown next to legend label
```

## Usage example

```yaml
# Step 1: generate the data block
# $ uv run scripts/extract-signal-trend.py --as-of 2026-05-14 > /tmp/trend.yaml

# Step 2: paste the contents into the recipe under signal-trend-area inputs
- component: signal-trend-area
  inputs:
    eyebrow: "Figure 0 · 14-day cluster trajectory · today = 14 May"
    chart_geometry:
      view_w: 600
      view_h: 240
      chart_top: 20
      chart_bottom: 210
      chart_left: 40
      chart_right: 580
    y_max: 600
    today_x: 580.0
    today_index: 8
    x_ticks:
      - { x: 40.0, label: "30 Apr" }
      - { x: 107.5, label: "1 May" }
      # ...
    y_ticks:
      - { y: 210.0, label: "0" }
      - { y: 146.7, label: "200" }
      - { y: 83.3, label: "400" }
      - { y: 20.0, label: "600" }
    bands:
      - cluster: "AI agents in GCC"
        color: "#F59E0B"
        points: "40.0,182.4 107.5,178.3 ..."
        today_value: 191
      # ...
    caption: "Today is 34% above the 8-day mean."
```

## Layout contract

- viewBox: `0 0 view_w view_h` (typically `600 × 240`)
- Y-axis: 4 horizontal grid lines + tick labels left of `chart_left`
- X-axis: tick labels centred under each `x_ticks[i].x`
- Today highlight: 1pt amber dashed rule + "TODAY" annotation above chart top
- Legend: HTML flex row below the SVG, with optional `today_value` annotation per band

## Accessibility notes

- Root carries `lang` and `dir` attributes
- `figure` element wraps the SVG with `role="group"` and `aria-label`
- Caption ties via the `figure` wrapper
- Bands use distinct hues from the brand palette so colour-blind readers can still distinguish them by stack order

## Why this exists

A peer reading a single-day brief asks two questions: "is today big?" and "is this cluster a fresh wave or a sustained build?" The trend chart answers both in one image. Without it, the brief reads as if today exists in isolation; with it, today reads as one frame in a 14-day arc.

The helper-script split keeps the SQL + analytical work where it belongs (Python) and the rendering work where it belongs (Jinja + SVG).
