# full-bleed-page

## Purpose

A single A4 page with zero margins — for full-bleed photography, chapter
opener images, product hero shots, or infographics that extend to the
sheet edge. Optional title overlay with legibility scrim; optional
caption strip at the bottom.

## Variants

| Variant | When to use |
|---|---|
| `with-overlay` | Default — image with eyebrow / title / subtitle text overlay. |
| `image-only` | Photography or infographics where the image speaks for itself. Caption still allowed. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `image` | image | **yes** | Full-page background. Supports `user-file`, `url`, `inline-svg`. |
| `eyebrow` | string | no | Small uppercase label above the title. |
| `title` | string | no | Large overlaid title. |
| `subtitle` | string | no | Smaller secondary line. |
| `caption` | string | no | Bottom strip — photo credit, source, or contextual note. |
| `position` | string | no | Where the overlay sits: `top-left`, `top-right`, `center` (default), `bottom-left`, `bottom-right`. |

## Example

```yaml
- component: full-bleed-page
  variant: with-overlay
  inputs:
    image:
      source: user-file
      path: assets/desert-wadi.jpg
    eyebrow: "CHAPTER TWO"
    title: "Into the Wadi"
    subtitle: "Where the road ends and the silence begins."
    position: bottom-left
    caption: "Photograph · Wadi Shawka, UAE, 2026."
```

## Notes

- Declares `@page full-bleed { margin: 0; }` — the only place in Katib
  that intentionally zeroes the base margin.
- A 3-stop `linear-gradient` scrim ensures the title stays legible over
  any image.
- `page_behavior: atomic` — always stands on its own page.
- RTL: caption right-aligns automatically; title overlay respects
  `dir="rtl"` for Arabic.
