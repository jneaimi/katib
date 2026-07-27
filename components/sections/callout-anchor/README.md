# callout-anchor

## Purpose

Image with numbered pins overlaid + a matching legend list keyed by the same numbers. The annotated-diagram pattern from technical drawing — leader-line semantics for a static PDF where actual leader lines don't survive scaling, locale shifts, or RTL flips. Embodies Mayer's signaling principle: directing attention to specific regions of an image.

## When to use

- Annotating a UI screenshot (which buttons, fields, and regions matter)
- Annotating a photograph (anatomy of a dish, parts of a tool)
- Annotating a diagram (regions of an architecture sketch)
- Anywhere "this part of the image means X" needs to be unambiguous

## Inputs

```yaml
- component: callout-anchor
  variant: solid    # solid (default) | outline
  inputs:
    image:
      source: user-file        # user-file or screenshot — NOT gemini
      path: /abs/path/to/diagram.png
    alt_text: "Stripe webhook configuration screen"
    caption: "Stripe Dashboard — webhook configuration"
    pins:
      - n: 1
        x: 18         # 0-100, percentage from logical-leading edge
        y: 22         # 0-100, percentage from top
        label: "Endpoint URL — paste your server's webhook URL here."
      - n: 2
        x: 60
        y: 38
        label: "Events to send — start with checkout.session.completed only."
      - n: 3
        x: 82
        y: 65
        label: "Signing secret — copy and set as STRIPE_WEBHOOK_SECRET."
```

## Variants

- **solid** (default) — filled accent-coloured pins. Best for clean / minimal imagery where pins read clearly against the background.
- **outline** — outlined accent-coloured pins on a page-bg fill. Best for dense or colourful background imagery where solid pins clash with underlying art.

## Pin coordinates

- `x` is measured from the **logical-leading** edge (left in EN, right in AR)
- `y` is measured from the **top** in both EN and AR
- Both are 0–100 percentages of the image width/height
- The component automatically uses `right: <x>%` instead of `left: <x>%` in AR builds, so the same pin coordinates work for both languages without authoring two versions

## Pin markers

`n` is a short string — typically `1`, `2`, `3`, but can also be `A`, `B`, `C` or any short label. The markers in the image and in the legend stay in sync because both render from the same `pins` array in order.

## Bilingual notes

- AR mirrors x-axis (pins stay anchored to the same logical region of the image — e.g. "the URL field at the top" stays at the top, not flipped to the opposite side just because the locale changed).
- Legend reads RTL in AR; markers stay numeric/LTR (universal convention for diagram callouts).
- Caption uses italic in both, with `font-style: italic` translating cleanly to both Latin italic and Arabic oblique fallbacks.

## Pedagogy

Source pattern: LEGO sub-step callout bubbles; sewing-pattern symbol keys with leader lines; technical-drawing standards; IKEA close-up insets. Mayer's signaling principle: when you point the reader at a specific region, attention follows. The static-PDF version replaces leader lines with co-numbered pins + legend — the eye matches the number on the image to the number in the legend list.

## Constraints

- Pin coordinates must be 0-100 (percentages). Pixel coordinates are not supported because the component is responsive to the rendered image size.
- The image is required. Without an image, pins have nothing to anchor against and the component is meaningless.
- For dense annotations (10+ pins), consider splitting into two `callout-anchor` blocks side-by-side — the legend gets unwieldy past ~8 entries.

## Companion components

- `tutorial-step` — what comes before this block (the procedural steps that lead to needing the diagram)
- `before-after` — pairs naturally when the annotation is about a transformation (annotate the before, then annotate the after)
- `figure-with-caption` — the simpler alternative when no annotations are needed (just an image + caption)

Part of the Tutorial Component Pack — Sprint 2 / Phase B.
