---
engine: gemini
model: nano-banana-2
aspect: "2:3"
size: 4K
temperature: 0.8
text_in_image: false
---

# Friendly Illustration — Cover Brief

## Philosophy

Friendly Illustration is the warm counterpart to Neural Cartography. Where Neural Cartography projects institutional weight, Friendly Illustration invites the reader in. This cover style belongs on tutorials, onboarding guides, how-tos, and cheatsheets — documents whose job is to reduce friction, not to impress.

The visual language is flat editorial illustration: confident shapes, deliberate negative space, a palette drawn from warm ivory and terracotta with calibrated teal accents. Characters, when present, are small and abstracted — geometric silhouettes rather than rendered figures, closer to an airport wayfinding icon than a stock illustration. Objects (documents, screens, paths, tools) read as gentle metaphor, never literal product shots.

The register is competent and approachable. A reader should open the document expecting to be guided, not lectured.

## Good for

`tutorial`, `how-to`, `cheatsheet`, `onboarding`, `handoff` — any documentation domain where approachability outweighs formality.

## Avoid for

- `business-proposal` — too casual for commercial deliverables; use `neural-cartography`
- `legal` — tone mismatch
- Documents intended to signal institutional authority

## Engine

Gemini Nano Banana 2 at 4K, 2:3 aspect. 2:3 (0.667) is closer to A4 portrait (0.707) than 9:16 (0.562) — the cover fills more of the page with less cropping.

## Prompt (generated image only — no text)

> Flat editorial illustration on warm ivory background `#FBF8F3`. A single, calm central composition — abstract geometric shapes suggesting a guided path, an open workspace, or stepping stones toward a goal. Rendered in confident flat colors: warm terracotta `#C85A3E` as the primary accent, slate teal `#3A7D8B` as the secondary, sage `#5A8549` and muted amber `#B8842A` as supporting tones. No gradients, no textures, no photographic elements. Shapes are deliberate and geometric — circles, arcs, rectangles, soft angles — with generous negative space around them. If human presence is suggested, it must be fully abstracted: simple silhouette forms, no faces, no hands in detail, closer to pictogram than illustrated character. Editorial poster aesthetic, like a well-designed conference booklet cover. Print-ready, 4K, vertical composition. Leave the upper third visually calmer (more negative space on ivory) to host overlaid title typography. The lower third should be the compositional weight, where the shapes settle.

## Negative prompt

Avoid: photorealism, 3D rendering, isometric perspective, detailed faces or hands, rendered characters, stock-illustration clichés, gradients, glow effects, textured backgrounds, hand-drawn sketchiness, watercolor, pencil, rainbow colors, cute cartoon mascots, business-cliché imagery (handshakes, gears, lightbulbs), typography in the image, logos.

## Arabic variant

Arabic covers use the **same generated image** — only the HTML text overlay position changes (title on the right side for RTL). Do not regenerate with a new prompt for AR. Arabic title rendering is handled by the HTML template overlay, since Gemini cannot reliably render Arabic script.

## Title overlay rules

- Title zone (EN): top-left, 90×30mm, offset 22mm from top and left
- Title zone (AR): top-right, 90×30mm, offset 22mm from top and right
- Title color: near-black `#2A2A2A` (prompt reserves ivory upper-third for contrast)
- Title size: 36pt, weight 600
- Subtitle zone (EN): below title, left-aligned, 85×12mm, offset 60mm from top
- Subtitle zone (AR): below title, right-aligned, 85×12mm, offset 60mm from top
- Subtitle color: terracotta `#C85A3E`
- Subtitle size: 14pt
- Reference code (EN): bottom-left, 10mm inset, 8pt, muted warm `#7A7268`, monospace
- Reference code (AR): bottom-right, 10mm inset, 8pt, muted warm `#7A7268`, monospace
- Date (EN): bottom-right, 10mm inset, 8pt, muted warm, monospace
- Date (AR): bottom-left, 10mm inset, 8pt, muted warm, monospace

## Text contrast verification

Upper-third ivory background provides 12:1+ contrast with near-black title — well above WCAG AAA. Subtitle terracotta on ivory ≈ 4.9:1 — meets WCAG AA for 14pt. If a generated cover fails this (e.g., shapes drift into the upper-third), rerun with the prompt's "upper third calmer" emphasis reinforced.

## Cost

Gemini Nano Banana 2 at 4K, 2:3 aspect ≈ $0.12 per image.

Rerun only if:
- The composition encroaches the upper third (title illegible)
- Shapes use colors outside the specified palette
- Human figures are rendered with facial detail (should be abstract silhouettes only)
- Any text or symbols appear in the image (prompt asks for none)
