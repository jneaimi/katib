# tag

Inline badge or chip label.

## Variants

| Variant | Look |
|---|---|
| `filled` (default) | Solid background tint, no border |
| `outline` | Transparent background, 1px border in tone accent |

## Tones

`neutral` (default) · `info` · `warn` · `danger` · `tip`

Tones map to the brand's callout color pairs — each tone has a background + accent.

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `text` | string | yes | — |
| `tone` | string | no | `neutral` |

## Usage

```yaml
- component: tag
  variant: filled
  inputs:
    text: "Draft"
    tone: warn
```
