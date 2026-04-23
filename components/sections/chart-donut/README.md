# chart-donut

Proportional breakdown chart. Inline-SVG only — data becomes pixels, factual and reproducible.

## Variants

| Variant | Look |
|---|---|
| `default` | Donut + legend to the side |
| `with-legend` | Same as default (explicit name) |
| `centered-stat` | Large donut centered; legend replaced by the SVG's internal stat |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Small label above the heading |
| `heading` | string | no | Section title |
| `body` | string | no | Context paragraph |
| `chart` | image (inline-svg) | yes | Spec below |
| `alt_text` | string | yes | Text alternative — required for a11y |
| `caption` | string | no | Caption below the figure |

### `chart` spec

```yaml
chart:
  source: inline-svg
  type: donut
  data:
    - {label: "LinkedIn", value: 420}
    - {label: "Reddit", value: 280}
    - {label: "Twitter", value: 140}
  size: 200      # optional, default 200
  stroke: 28     # optional, default 28
  title: "..."   # optional aria-label
```

Colors come from `charts.palette` in tokens — injected automatically by compose(). Override per-bar via `data[i].color`.

## Usage

```yaml
- component: chart-donut
  inputs:
    heading: "Signal sources"
    body: "Share of findings by platform, last 30 days."
    chart:
      source: inline-svg
      type: donut
      data:
        - {label: "LinkedIn", value: 420}
        - {label: "Reddit", value: 280}
        - {label: "Twitter", value: 140}
    alt_text: "Donut chart: LinkedIn 420, Reddit 280, Twitter 140"
```

## Composes

- `.katib-eyebrow` · `.katib-eyebrow--muted`
- `.katib-sr-only` (visually-hidden data table alternative)
