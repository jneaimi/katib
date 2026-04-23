# front-matter

Title-first title-page section — a lighter alternative to a full `cover-page` when you want a typographic entry without a background image.

## Layout

```
EYEBROW
Document Title
Optional subtitle paragraph
─────────────
Author · Date · REF-CODE
```

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `eyebrow` | string | no | `"Document"` (EN) · `"وثيقة"` (AR) |
| `title` | string | yes | — |
| `subtitle` | string | no | — |
| `author` | string | no | — |
| `date` | string | no | — |
| `reference_code` | string | no | — |

## Page behaviour

- `break_after: always` — body content starts on the next page
- `break_inside: avoid` — the whole block stays together

## Usage

```yaml
- component: front-matter
  inputs:
    eyebrow: "Strategy brief"
    title: "GCC AI Ecosystem — H2 2026"
    subtitle: "Where the puck is going, and where it isn't"
    author: "Jasem Al Neaimi"
    date: "2026-04-23"
    reference_code: "JN-STRAT-0042"
```

## Composes

References primitive CSS classes:
- `.katib-eyebrow` · `.katib-eyebrow--accent`
- `.katib-rule` · `.katib-rule--hairline`

## Accessibility

- `<h1>` for the document title — announced as the top-level heading
- Meta strip uses spans with no aria-role overrides — sighted-only convention is reasonable here
