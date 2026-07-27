# outcome-preview

## Purpose

Hero "what you'll build" block — a target image + headline that sets the reader's mental model before any steps happen. Reduces anxiety, gives an early-success target, and honours Mayer's pre-training principle (the reader knows what they're committing to).

## When to use

- Page 2 of any tutorial, immediately after the cover and before objectives/prerequisites
- Top of an assembly guide (the finished item)
- Top of a recipe card (the finished dish, hero shot)
- Top of a course module (a 1-frame visual summary of what the unit produces)

## Inputs

```yaml
- component: outcome-preview
  variant: image-leading   # image-leading (default) | image-trailing | image-top
  inputs:
    eyebrow: "WHAT YOU'LL BUILD"
    title: "A working Stripe payment flow in 15 minutes"
    subtitle: "Customer hits Pay → Checkout → success → webhook."
    body: "Optional 1-2 line framing paragraph."
    image:
      source: user-file        # user-file or screenshot — NOT gemini
      path: /abs/path/to/target.png
    alt_text: "Stripe Checkout success screen"
    caption: "Final state — what you should see after step 8."
```

## Variants

- **image-leading** (default) — image on the logical-leading side (left in EN, right in AR), text on the trailing side. Best for landscape/widescreen targets.
- **image-trailing** — image on the trailing side. Useful when the cover already has art on the left and you want to alternate.
- **image-top** — image stacked on top, full-width, text below. Best for very-wide hero shots or when the target image needs the full column width to read.

## Bilingual notes

- AR mirrors the leading/trailing relationship logically — `image-leading` in AR puts the image on the right (the logical-start side), not the left. The CSS forces `flex-direction: row-reverse` for AR `image-leading` to enforce this even when the user agent doesn't auto-flip.
- AR title sizes up slightly (24pt vs 22pt) to compensate for Latin display fonts being denser than Arabic at the same point size.

## Pedagogy

Source pattern: IKEA opens with completed-product render; LEGO opens with overview illustration; every Apple SwiftUI tutorial leads with target screenshot; cookbook recipes lead with finished-dish photo. The block is deliberately image-first because pictures resolve "what am I building?" in a fraction of the time text does.

## Constraints

- The `image.source` MUST be `user-file` or `screenshot`. Gemini-generated images are excluded by contract: outcome previews are factual representations of the end state, not aspirational renders. (The same constraint applies to `tutorial-step`'s screenshot input.)
- The image renders with `object-fit: cover` at `max-height: 110mm` (90mm in `image-top`). Provide images at a comfortable 16:9 or 4:3 aspect to avoid awkward cropping.

## Companion components

- `cover-page` — the page-1 partner that this block follows
- `meta-strip` — sits between the cover and this block, giving time/difficulty/yield meta
- `objectives-box` — the bulleted "by the end you will…" companion that goes after this block

Part of the Tutorial Component Pack — Sprint 1 / Phase A.
