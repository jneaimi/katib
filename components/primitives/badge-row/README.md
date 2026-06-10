# badge-row

## Purpose

A row of bordered badges for certifications, awards, accreditations,
memberships, and ratings. Each badge carries a bold label and an optional
smaller sublabel. Heavier and more structured than `tag-chips` (which is for
keywords / tags / technologies) — reach for `badge-row` when the items are
credentials a reader should take seriously.

## Variants

| Variant | When to use |
|---|---|
| `default` | Outlined badges — quiet, sits well inside body content. |
| `solid` | Accent-filled badges — a louder strip for a hero or sidebar. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `items` | `array` | yes | Each item is a plain string, or an object `{label, sublabel?}`. |

## Example usage

```yaml
- component: badge-row
  variant: default
  inputs:
    items:
      - { label: "ISO 9001", sublabel: "Quality" }
      - { label: "ISO 27001", sublabel: "Security" }
      - { label: "Great Place to Work", sublabel: "Certified 2024" }
      - "AWS Advanced Partner"
```

## Notes

- Mixed forms are fine in one row — plain strings and `{label, sublabel}`
  objects can be interleaved.
- The `solid` variant uses the `accent` / `accent_on` token pair so it inherits
  brand colours.
- `mode: atomic` — the whole row stays together; it will not split across a
  page break.
- RTL: badges align to the right, the trailing margin mirrors, and the sublabel
  drops uppercase / letter-spacing.
