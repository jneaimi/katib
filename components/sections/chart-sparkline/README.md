# chart-sparkline

Compact trendline with optional headline stat + delta badge. Line always flows left-to-right — time is chronological in data-vis regardless of text direction.

## Variants

| Variant | Look |
|---|---|
| `default` | Headline stat + sparkline |
| `with-delta-badge` | Adds a colored delta badge next to the stat |

## Inputs

| Name | Type | Required |
|---|---|---|
| `eyebrow` | string | no |
| `heading` | string | no |
| `stat` | string | no — headline number beside the line |
| `stat_delta` | string | no — short change indicator, used only by `with-delta-badge` |
| `body` | string | no — short prose |
| `chart` | image (inline-svg) | yes |
| `alt_text` | string | yes |
| `caption` | string | no |

### `chart` spec

```yaml
chart:
  source: inline-svg
  type: sparkline
  data: [12, 15, 14, 19, 22, 28, 34, 41, 48, 55, 62, 68]
  labels: [Jan, Feb, ...]   # optional, parallel array
  width: 600
  height: 80
  title: "..."
```

- Empty data → error
- Single point → dot at center
- Flat line → mid-height line
- Negatives → allowed, baseline auto-adjusts

## Composes

- `.katib-eyebrow` · `.katib-sr-only`
