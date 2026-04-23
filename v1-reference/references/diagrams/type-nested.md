# Nested Containment

**Best for:** hierarchy through containment — scope boundaries, CLAUDE.md cascade, trust zones, folder nesting, blast radius. Outer = broader, inner = more specific.

## Layout conventions

- 3–5 rounded rectangles (`rx=8`), nested with consistent inset padding (24–32px horizontal, 32–36px vertical recommended).
- Each level labeled at the top-left in monospace eyebrow style (7–8px, letter-spacing 0.14em). Labels sit on a `colors.page_bg` mask rect over the ring's top border.
- **Stroke hierarchy:** outer rings faint (`colors.border` at opacity 0.30–0.45), progressing to `colors.text_secondary`, to `colors.text`, to `colors.accent` at the innermost focal.
- **Fills step up in opacity** from outer to inner: `colors.text @ 0.015` → `colors.text @ 0.025` → accent-tint on the innermost.
- Optional file-icon glyph (folded-corner rect) inside each level hints at scope content.
- Italic editorial callouts welcome — max 2 (see [primitive-annotation.md](primitive-annotation.md)).

## Ring primitive

```html
<!-- Outermost (faintest) -->
<rect x="40" y="40" width="880" height="560" rx="8"
      fill="{{ colors.text }}" fill-opacity="0.015"
      stroke="{{ colors.border }}" stroke-width="1"/>

<!-- Label mask -->
<rect x="56" y="32" width="120" height="12" fill="{{ colors.page_bg }}"/>
<text x="64" y="42" fill="{{ colors.text_tertiary }}" font-size="8"
      font-family="ui-monospace, monospace" letter-spacing="0.14em">ORGANIZATION</text>

<!-- Middle ring -->
<rect x="80" y="80" width="800" height="480" rx="8"
      fill="{{ colors.text }}" fill-opacity="0.025"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>

<!-- Innermost focal (accent) -->
<rect x="320" y="200" width="280" height="160" rx="8"
      fill="{{ colors.accent }}" fill-opacity="0.06"
      stroke="{{ colors.accent }}" stroke-width="1.2"/>
```

## File-icon glyph (optional)

```html
<!-- Folded-corner rectangle, 24×32, top-left of a ring -->
<path d="M X Y l 18 0 l 6 6 l 0 26 l -24 0 z M X+18 Y l 0 6 l 6 0"
      fill="none" stroke="{{ colors.text_secondary }}" stroke-width="0.8"/>
```

## Bilingual

- Level labels (`ORGANIZATION`, `DEPARTMENT`, `TEAM`) translate: `المنظمة`, `الإدارة`, `الفريق`. Overlay via `.diagram-label` with the `dl-xs` size + monospace styling preserved.
- Ring geometry stays identical — hierarchy reads the same in either direction.
- **Don't mirror** — inside/outside is a containment relationship, not a reading direction.

## Anti-patterns

- More than 6 levels (information disappears inward).
- Irregular padding between levels — unaligned nesting looks accidental.
- Content inside rings that isn't part of the hierarchy — use a sibling diagram.
- `colors.accent` on multiple levels — hierarchy collapses.
- Labels sitting on top of the ring stroke without a mask rect — reads as overlap.
