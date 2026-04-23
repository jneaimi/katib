# Layer Stack

**Best for:** OSI model, CSS cascade, context hierarchy, tech stack, abstraction layers, memory hierarchy.

## Layout conventions

- Horizontal bands stacked vertically. Each layer is a full-width rectangle (same x, same width). **4–6 layers total.**
- Layer height 56–72px, width typically 800–880px inside a 1000px viewBox.
- Each row contains (left→right):
  1. **Index tag** on the far left (`L3`, `07`, `APPLICATION`) — monospace 8–9px eyebrow.
  2. **Layer name** slightly right of center-left — brand body sans 14–16px 600.
  3. **Sublabel / note** on the far right — monospace 9–10px, `colors.text_secondary`.
- Border between layers: 1px hairline `colors.border`. Outer silhouette 1px `colors.text` or `colors.text_secondary`.
- Fills: either alternating subtle shades (`colors.page_bg` / `colors.tag_bg`) OR all `colors.page_bg` with hairline dividers. Pick one and hold it.
- **Direction indicator** on the LEFT margin (outside the stack): small up/down arrow + monospace label (`abstraction ↑`, `packets ↓`).
- `colors.accent` on **one** focal layer (stroke + subtle tint fill) — the bottleneck, the pay-rent layer, the layer under discussion.

## Layer primitive

```html
<!-- Standard layer -->
<rect x="80" y="LAYER_Y" width="800" height="64" rx="0"
      fill="{{ colors.page_bg }}"
      stroke="{{ colors.border }}" stroke-width="1"/>

<!-- Index tag -->
<text x="100" y="LAYER_Y+38" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace" letter-spacing="0.14em">L4</text>

<!-- Layer name -->
<text x="180" y="LAYER_Y+40" fill="{{ colors.text }}" font-size="14" font-weight="600"
      font-family="inherit">Transport</text>

<!-- Sublabel / note -->
<text x="860" y="LAYER_Y+40" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace" text-anchor="end">TCP / UDP</text>
```

## Focal layer (accent)

```html
<rect x="80" y="FOCAL_Y" width="800" height="64" rx="0"
      fill="{{ colors.accent }}" fill-opacity="0.06"
      stroke="{{ colors.accent }}" stroke-width="1.2"/>
<text x="180" y="FOCAL_Y+40" fill="{{ colors.accent }}" font-size="14" font-weight="700"
      font-family="inherit">Application</text>
```

## Direction arrow (left margin)

```html
<!-- Up arrow (abstraction) -->
<line x1="48" y1="STACK_BOTTOM" x2="48" y2="STACK_TOP"
      stroke="{{ colors.text_secondary }}" stroke-width="1"
      marker-end="url(#arrow)"/>
<text x="40" y="STACK_MIDDLE" fill="{{ colors.text_secondary }}" font-size="8"
      font-family="ui-monospace, monospace" text-anchor="middle"
      letter-spacing="0.14em"
      transform="rotate(-90 40 STACK_MIDDLE)">ABSTRACTION</text>
```

(Rotating monospace for axis-style vertical text is fine — it's an *axis label*, not an arrow label.)

## Bilingual

- Layer names translate: `Transport` → `النقل`, `Application` → `التطبيق`. Overlay via `.diagram-label`.
- Index tags (`L4`, `07`) stay in SVG — they're notation.
- Mirror? **No** — vertical stacking is direction-neutral (up = higher abstraction universally).

## Anti-patterns

- Layers that aren't actually hierarchical (use [type-swimlane.md](type-swimlane.md) or [type-architecture.md](type-architecture.md)).
- Skipped numbering (missing L4 between L3 and L5 without explanation).
- Every layer a different color — hierarchy invisible.
- Inconsistent layer heights without reason.
- More than 6 layers — compress by grouping.
