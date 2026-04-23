# cover-page

Full-page document opener. First-class `cover` tier component.

## Variants

| Variant | Look | Requires |
|---|---|---|
| `minimalist-typographic` (default, ships in Day 3) | CSS-only — big display-font title, small eyebrow, brand logo top, footer strip with author + ref | None |
| `image-background` (Day 4) | Full-bleed cover image with typographic overlay | `image` input, `user-file` or `gemini` source |
| `neural-cartography` (Day 4) | Gemini-generated decorative abstract background | `GEMINI_API_KEY` |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Category label — rendered in accent-2 color, uppercase |
| `title` | string | yes | Document title — 42pt display, auto-wraps |
| `subtitle` | string | no | Rendered 14pt under title |
| `reference_code` | string | no | Monospace code in footer-right |

## Automatic brand fields (no input needed)

Cover pulls from the merged token context:
- `logo.primary` → rendered top if set
- `identity.author_name` → footer-left
- `name` (brand display name) → used as logo alt-text

Set these in your brand YAML or they render empty.

## Usage

```yaml
- component: cover-page
  variant: minimalist-typographic
  inputs:
    eyebrow: "Tutorial"
    title: "Bloom's AI Collaboration Framework"
    subtitle: "A six-level cognitive stack for deciding when AI should execute vs. when humans should evaluate."
    reference_code: "JN-AI-0001"
```

With a brand that sets `logo.primary` and `identity.author_name`, this renders a complete branded cover with no additional recipe fields.

## Page behaviour

- `break_after: always` — body content starts on page 2
- `break_inside: avoid` — cover never splits
- `min-height: 253mm` — fills A4 minus default margins (297mm - 2×22mm gutters)
