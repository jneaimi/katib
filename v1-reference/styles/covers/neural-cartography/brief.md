---
engine: gemini
model: nano-banana-2
aspect: 9:16
size: 4K
temperature: 0.7
text_in_image: false
---

# Neural Cartography — Cover Brief

## Philosophy

Neural Cartography draws from the visual language of circuit diagrams, topographic mapping, and the invisible architectures that connect intelligence to outcome. Deep navy fields become the substrate upon which knowledge pathways are etched in gold. Every line, every node, every interval of silence speaks to the meticulous hand of a master cartographer charting unseen terrain.

The work must feel as though countless hours were spent calibrating each connection point, each gradient transition, each breath of negative space. Geometric nodes — circles, hexagons, precise intersections — anchor compositions the way waypoints anchor a map, yet the pathways between them curve and branch with the organic unpredictability of neural networks.

## Good for

`business-proposal`, `formal` — any domain where institutional weight and intellectual depth is the desired register.

## Avoid for

- `marketing-pitch` — too restrained, lacks emotional pull
- `personal` — too formal for correspondence
- `tutorial` — too serious for learning materials

## Prompt (generated image only — no text)

> Abstract cartographic composition on deep navy `#1B2A4A` background. Intricate network of thin warm-gold pathways `#C5A44E` connecting geometric nodes — circles, hexagons, precise intersections — rendered at varying scales. Organic curve flow between nodes, reminiscent of neural networks crossed with topographic contour lines. Subtle teal accent paths `#2E7D6B` trace secondary circuits. Light slate `#E8EDF4` atmospheric fog between depth layers. No text, no photographic elements, no human figures, no explicit icons. Negative space charged with potential — mapped territory against unmapped depth. Painterly precision, specimen-chart aesthetic, executed with calibrated restraint. Print-ready, 4K, vertical A4 composition. Leave the upper third visually calmer for overlaid title typography. Leave the lower right quadrant darker for subtitle contrast.

## Negative prompt

Avoid: bright rainbow colors, gradient backgrounds, photorealistic imagery, illustrated characters, logos, typography in the image, flat minimalist design, isometric perspective, 3D rendering.

## Arabic variant

Arabic covers use the **same generated image** — only the HTML text overlay changes position (title top-right instead of top-left, subtitle bottom-left instead of bottom-right). Do not regenerate with a new prompt for the AR version; it wastes Gemini credit and creates brand inconsistency.

## Title overlay rules

- Title zone (EN): top-left, 90×30mm, offset 25mm from top and left
- Title zone (AR): top-right, 90×30mm, offset 25mm from top and right
- Title color: near-white `#FAFAF8` (contrast ratio ≥ 7:1 on navy background)
- Title size: 36pt, weight 500
- Subtitle zone (EN): bottom-right, 60×15mm, offset 30mm from bottom, 25mm from right
- Subtitle zone (AR): bottom-left, 60×15mm, offset 30mm from bottom, 25mm from left
- Subtitle color: gold `#C5A44E`
- Subtitle size: 12pt
- Reference code (EN): bottom-left corner, 10mm inset, 8pt, `#E8EDF4`
- Reference code (AR): bottom-right corner, 10mm inset, 8pt, `#E8EDF4`

## Text contrast verification

All overlay text must achieve WCAG AA contrast (4.5:1 for body, 3:1 for large text) against the navy background. The prompt specifies the upper-third be visually calmer to support title legibility; verify by visual inspection of each generated cover.

## Cost

Gemini Nano Banana 2 at 4K, 9:16 aspect ≈ $0.12 per image.

Rerun only if:
- The image has visible text in the composition
- Node/pathway density dominates the title zone (making overlay unreadable)
- Color cast drifts outside the navy/gold/teal specification
