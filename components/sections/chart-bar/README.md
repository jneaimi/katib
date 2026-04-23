# chart-bar

Horizontal bar chart. Bars grow from the language-origin side: left-to-right in EN, right-to-left in AR. Inline-SVG only.

## Variants

| Variant | Look |
|---|---|
| `default` | Horizontal bars, category labels in the axis gutter, value labels at the bar tip |

Vertical bars are a future variant — Day 6 ships horizontal only.

## Inputs

| Name | Type | Required |
|---|---|---|
| `eyebrow` | string | no |
| `heading` | string | no |
| `body` | string | no |
| `chart` | image (inline-svg) | yes |
| `alt_text` | string | yes |
| `caption` | string | no |

### `chart` spec

```yaml
chart:
  source: inline-svg
  type: bar
  data:
    - {label: "Product", value: 3200}
    - {label: "Services", value: 1800}
    - {label: "Partnerships", value: 750}
  width: 600          # optional
  bar_height: 20      # optional
  label_gutter: 140   # optional — space reserved for category labels
  title: "..."
```

- Negative values are **rejected** (bar: negative values not supported)
- Empty data is rejected
- All-zero data is rejected
- Per-bar color via `data[i].color`; otherwise palette from tokens

## Composes

- `.katib-eyebrow` · `.katib-sr-only`
