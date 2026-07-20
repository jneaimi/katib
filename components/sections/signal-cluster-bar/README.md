# signal-cluster-bar

**Tier:** section · **Namespace:** katib

## Purpose

Data-driven horizontal cluster-density bar chart. Built for Signal Forge peer briefings (Figure 1 in every miner-daily brief), generalises to any "rank these N items by a numeric value" visualisation. Bars auto-scale from data; value labels never overflow the viewBox; colour tiers are enum-controlled.

## What this is, and what it isn't

| | This component | `chart-bar` |
|---|---|---|
| Input shape | Structured data (`items: [{label, value, ...}]`) | Hand-crafted SVG |
| Bar widths | Auto-scaled from data | Author-set in source SVG |
| Value labels | Auto-positioned, never overflow | Author-positioned |
| Intensity colour tiers | `high` / `mid` / `low` enum | Manual fill values |
| Use when | You have data and want bars | You have a bespoke SVG you already drew |

If you have a CSV-shaped list and want bars, use this. If you have a hand-illustrated SVG with custom annotations, use `chart-bar`.

## Variants

- default

## Inputs

| Field | Required | Type | Notes |
|---|---|---|---|
| `eyebrow` | optional | string | Small uppercase label above the chart |
| `title` | optional | string | Heading rendered above the eyebrow |
| `x_axis_label` | optional | string | Top-of-chart axis hint, e.g. `"CROSS-PLATFORM VIEWS · 24-HOUR PULL"` |
| `items` | **required** | array | One item per bar |
| `caption` | optional | string | Italic note rendered below the chart |

### Item shape

```yaml
- label: "Claude Code adoption"        # bar label
  value: 1830000                       # number, used for bar-width scaling
  value_display: "1.83M"               # string, what shows next to the bar
  intensity: high                      # one of: high | mid | low
```

`value_display` is separate from `value` so you can show `"1.83M"`, `"~340K"`, `"211K (single video)"`, or any human-readable form without losing the numeric basis for the chart.

`intensity` controls colour:
- `high` → amber (`#F59E0B`)
- `mid` → orange (`#FB923C`)
- `low` → grey (`#A1A1AA`)

## Usage example

```yaml
- component: signal-cluster-bar
  inputs:
    eyebrow: "Figure 1 · Cluster discourse density · 24-hour pull"
    x_axis_label: "CROSS-PLATFORM VIEWS · 24-HOUR PULL · 7-DAY WINDOW"
    items:
      - label: "Claude Code adoption"
        value: 1830000
        value_display: "1.83M"
        intensity: high
      - label: "Agentic commerce resolution"
        value: 1770000
        value_display: "1.77M"
        intensity: high
      - label: "Agent memory architecture"
        value: 340000
        value_display: "~340K"
        intensity: mid
      - label: "Non-tech Claude monetisation"
        value: 21000
        value_display: "~21K"
        intensity: low
    caption: "Two clusters carry the day at near-equal weight; the rest sit well below."
```

## Layout contract

- viewBox: `0 0 600 H`, where `H = 32 + (rows × 30) + 12`
- EN: bars start at `x=240`, max width 290, value labels render with 8px gap after the bar end
- AR: bars end at `x=360` (RTL mirror), max width 290, value labels render with 8px gap to the left of bar start
- Smallest bar clamps to 6px so single-signal rows still render
- Auto-generated `<table class="katib-sr-only">` mirrors the data for screen readers

## Accessibility notes

- Root carries `lang` and `dir` attributes
- `figure` element wraps the SVG with `role="group"` and an `aria-label`
- Hidden `<table>` provides cluster/value pairs for assistive tech

## Why this exists

Hand-rolled SVG charts in recipe yamls drift. Three problems showed up across the first three Signal Forge peer briefs (12, 13, 14 May):

1. Value labels positioned by hand often overflow the viewBox when the longest bar grows
2. Bar widths require manual recalculation when source data changes
3. Colour tiers get inconsistent across recipes

This component solves all three by computing bar widths from the data and clamping label positions to safe ranges.
