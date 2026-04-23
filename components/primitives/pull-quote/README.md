# pull-quote

Emphasized blockquote for highlighting a short passage or testimonial.

## Variants

| Variant | Look |
|---|---|
| `rule-leading` (default) | 3px accent rule on leading edge |
| `large-quote` | Oversized `"` mark on leading edge, no rule |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `text` | string | yes | The quoted passage |
| `attribution` | string | no | Author, source, role — rendered with em-dash prefix |

## Usage

```yaml
- component: pull-quote
  variant: large-quote
  inputs:
    text: "The best time to plant a tree was twenty years ago."
    attribution: Chinese proverb
```

## Notes

- EN text is italicized; AR text is not (italic doesn't carry meaningful weight in Arabic typography).
- Uses `border-inline-start` / `inset-inline-start` so the accent flips to the correct side automatically under RTL.
- Declares `break_inside: avoid` — pull-quotes never split across pages.
