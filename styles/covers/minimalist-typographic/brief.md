---
engine: css
model: none
aspect: 1:1.414
text_in_image: true
---

# Minimalist Typographic — Cover Brief

## Philosophy

No image. The cover is pure typography against paper. The work sits in the restraint.

A field of warm ivory. A single thin rule. Title in a generous display size, near-black. Subtitle in a warm accent at moderate scale. A small reference code or date at the bottom. Negative space does the heavy lifting — nothing competes with the words.

## Good for

`cheatsheet`, `how-to`, `tutorial` — any domain where the content itself is the product and the cover should not overshadow it.

## Avoid for

- `business-proposal` — too restrained for institutional deliverables that need visual weight
- Any doc where a hero image is the strongest first impression

## Engine

**CSS-only.** The cover page is rendered by the layout/template via HTML + CSS; no image generation, no Gemini call, no `assets/cover.png`. Saves $0.12 per document and keeps the typographic purity intact.

## Overlay rules (rendered in HTML, not baked into an image)

- Title zone: centered horizontally, 35% from top
- Title: 48pt display weight (600), near-black `#2A2A2A`, letter-spacing tight for Latin, normal for Arabic
- Subtitle zone: centered, directly below title with 16pt gap
- Subtitle: 14pt, warm terracotta `#C85A3E`, weight 400
- Reference code: bottom-left (EN) / bottom-right (AR), 9pt, warm muted `#7A7268`, monospace
- Date: bottom-right (EN) / bottom-left (AR), 9pt, warm muted, monospace
- A single 0.5pt horizontal rule separates title-area from page, 45% from top

## Cost

$0.00 per cover.

## Rerender

N/A — the cover is part of the HTML render, regenerated every time the document is built.
