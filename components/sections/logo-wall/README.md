# logo-wall

## Purpose

Client / partner logo wall — a centered grid of logos with uniform sizing and
an optional caption under each mark. Use it for "trusted by", "our clients",
"partners", or "as featured in" bands in company profiles, proposals, and
decks. The heading is deliberately understated (rendered in a muted tone) so
the logos carry the section.

## Variants

| Variant | When to use |
|---|---|
| `default` | Clean centered grid, no frames. |
| `boxed` | Each logo in a thin-bordered cell — good on busy pages or when logos vary widely in shape. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | `string` | no | Uppercase kicker. |
| `heading` | `string` | no | Understated heading above the grid. |
| `columns` | `int` | no | `3`, `4` (default), `5`, or `6`. |
| `logos` | `array` | yes | List of logo objects (see below). |

Each `logos[]` entry:

| Field | Type | Required | Notes |
|---|---|---|---|
| `image` | `image path` | yes | SVG or transparent PNG looks best; sized to a uniform max-height. |
| `name` | `string` | no | Caption / alt text under the mark. |

## Example usage

```yaml
- component: logo-wall
  inputs:
    eyebrow: "Our clients"
    heading: "Trusted by leading organisations"
    columns: 4
    logos:
      - { image: "assets/clients/aramco.svg", name: "Aramco" }
      - { image: "assets/clients/emirates.svg", name: "Emirates" }
      - { image: "assets/clients/sabic.svg", name: "SABIC" }
      - { image: "assets/clients/mubadala.svg", name: "Mubadala" }
```

## Notes

- Logos are sized to a uniform `max-height` and centered in each cell, so
  mixed aspect ratios still read as a tidy row.
- `mode: flowing-protect-items` keeps a logo cell from splitting across a
  page break.
- RTL: the grid flow mirrors automatically; uppercase / letter-spacing is
  dropped from the eyebrow.
