# Pyramid / Funnel

**Best for:** hierarchy of needs, prioritization ranks, value pyramids, conversion funnels, content importance stacks.

## Two orientations — pick one

- **Pyramid** (point up) — narrow apex = most important / rarest / most valuable. Base is broadest / foundational.
- **Funnel** (point down) — narrow end = conversion (smallest group). Top is widest / audience.

Don't mix orientations on one diagram.

## Layout conventions

- **4–6 layers.** Each layer is a trapezoid built from an SVG `<polygon>` with 4 points.
- Consistent layer height (56–72px).
- Widths decrease linearly from base to apex (pyramid) or top to bottom (funnel). **When showing real funnel data, widths must be honest** (proportional to count/percentage).
- Each layer has:
  - **Name label** centered inside the trapezoid — body-sans 12–14px 600.
  - **Sublabel** below or beside the name — monospace 9–10px.
  - **Side annotation** (right or left) — optional. For funnels: drop-off percentage here (`−40%`).
- **Fill:** subtle graded tints OR all `colors.page_bg` with hairline dividers (cleaner). Pick one.
- **Stroke:** 1px hairline between layers; outer silhouette 1px `colors.text_secondary` or `colors.text`.
- **Accent on ONE layer only:** apex of pyramid, conversion layer of funnel, or critical bottleneck.
- Optional left-margin axis arrow + monospace label (`rarer ↑`, `drop-off ↓`).

## Trapezoid primitive

A layer from `(x1, top_y)` to `(x2, top_y)` at top, `(x1-w, bottom_y)` to `(x2+w, bottom_y)` at bottom — widening downward (pyramid base direction):

```html
<!-- Layer 2 of a pyramid (widening downward) -->
<polygon points="320,80 480,80 520,140 280,140"
         fill="{{ colors.page_bg }}"
         stroke="{{ colors.text_secondary }}" stroke-width="1"/>
<text x="400" y="114" fill="{{ colors.text }}" font-size="13" font-weight="600"
      text-anchor="middle" font-family="inherit">Belonging</text>
```

## Apex (focal, accent)

```html
<!-- Pyramid apex — triangle polygon -->
<polygon points="380,40 420,40 440,80 360,80"
         fill="{{ colors.accent }}" fill-opacity="0.10"
         stroke="{{ colors.accent }}" stroke-width="1.2"/>
<text x="400" y="64" fill="{{ colors.accent }}" font-size="12" font-weight="700"
      text-anchor="middle" font-family="inherit">Self-Actualization</text>
```

## Funnel drop-off annotation

```html
<!-- Between layer 1 and layer 2 of a funnel -->
<text x="620" y="FUNNEL_MID_Y" fill="{{ colors.text_tertiary }}" font-size="10"
      font-family="ui-monospace, monospace"
      text-anchor="start">−42%</text>
```

Pair with a leader line from the layer edge to the annotation.

## Bilingual

- Layer names translate — overlay via `.diagram-label` centered inside the trapezoid.
- Drop-off percentages stay in SVG (numeric) but if you include an Arabic caption (`الانخفاض`), overlay it.
- **Don't mirror** pyramid/funnel — up/down carries semantic meaning (apex = rare, base = common).

## Anti-patterns

- 7+ layers (illegible — compress or split).
- Pyramid for non-hierarchical data (use a tree or bar chart).
- Dishonest widths (fake equal spacing when real drops are unequal).
- `colors.accent` on the base layer (dilutes the "apex = rare" signal).
- Mixing pyramid (up) + funnel (down) on the same diagram — pick one story.
- Trapezoid polygons with inconsistent angle steps — all transitions should use the same width delta.
