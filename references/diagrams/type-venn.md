# Venn / Set Overlap

**Best for:** intersection of concepts/domains, shared attributes between categories, "where A meets B", ikigai-style frames (desirable × feasible × viable).

## Layout conventions

- **Prefer 2 or 3 circles.** Avoid 4+ (unreadable — use a matrix instead).
- **Circle stroke:** 1px hairline, color per-set (`colors.text`, `colors.text_secondary`, `colors.text_tertiary`).
- **Circle fill:** very low-opacity tint — `colors.text @ 0.04` for ink set, `colors.text_secondary @ 0.05` for muted. Tints compound naturally in overlap regions.
- **Radii:** equal when sets are comparable in size; proportional when sets are meaningfully different. Don't fake equal sizes for aesthetics.
- **Set labels** placed *outside* the circle, NEVER crossing the stroke. Body-sans 12–14px 600 for the set name, optional monospace 9px sublabel.
- **Intersection labels** placed inside the overlap region, body-sans 12px 600, centered. For small overlaps, use a leader line to a label in clear space.
- **Accent** on the ONE focal intersection — the "sweet spot". Either accent label stroke OR `clipPath`-bounded accent fill tint (`colors.accent @ 0.10`).
- Circle centers and radii divisible by 4.

## Two-circle primitive

```html
<!-- Circle A -->
<circle cx="320" cy="240" r="140"
        fill="{{ colors.text }}" fill-opacity="0.04"
        stroke="{{ colors.text }}" stroke-width="1"/>

<!-- Circle B (overlap at center) -->
<circle cx="480" cy="240" r="140"
        fill="{{ colors.text_secondary }}" fill-opacity="0.05"
        stroke="{{ colors.text_secondary }}" stroke-width="1"/>

<!-- Set A label (outside, left) -->
<text x="180" y="240" fill="{{ colors.text }}" font-size="13" font-weight="600"
      text-anchor="middle" font-family="inherit">Users</text>

<!-- Set B label (outside, right) -->
<text x="620" y="240" fill="{{ colors.text_secondary }}" font-size="13" font-weight="600"
      text-anchor="middle" font-family="inherit">Admins</text>

<!-- Intersection label (centered on overlap) -->
<text x="400" y="244" fill="{{ colors.text }}" font-size="12" font-weight="600"
      text-anchor="middle" font-family="inherit">Owners</text>
```

## Accent intersection (clipPath approach)

```html
<defs>
  <clipPath id="overlap-ab">
    <!-- Both circles intersected via clip-path -->
    <circle cx="320" cy="240" r="140"/>
  </clipPath>
</defs>

<!-- Accent tint inside the overlap only -->
<circle cx="480" cy="240" r="140"
        fill="{{ colors.accent }}" fill-opacity="0.10"
        clip-path="url(#overlap-ab)"/>

<!-- Accent label on top -->
<text x="400" y="244" fill="{{ colors.accent }}" font-size="13" font-weight="700"
      text-anchor="middle" font-family="inherit">Sweet spot</text>
```

## Three-circle (ikigai-style)

Classic triad — arrange three circles at 120° intervals around a center point. Each pair overlaps; all three overlap in the middle.

```html
<!-- Circles positioned at (0, -90), (78, 45), (-78, 45) from center (400, 240) -->
<circle cx="400" cy="150" r="130" fill="{{ colors.text }}" fill-opacity="0.04" stroke="{{ colors.text }}" stroke-width="1"/>
<circle cx="478" cy="285" r="130" fill="{{ colors.text_secondary }}" fill-opacity="0.05" stroke="{{ colors.text_secondary }}" stroke-width="1"/>
<circle cx="322" cy="285" r="130" fill="{{ colors.text_tertiary }}" fill-opacity="0.05" stroke="{{ colors.text_tertiary }}" stroke-width="1"/>
```

## Bilingual

- Set labels + intersection labels translate — overlay all text via `.diagram-label`.
- Geometry stays identical — overlap is a mathematical relationship, not directional.
- Don't mirror.

## Anti-patterns

- Unlabeled regions — reader can't tell which set is which.
- Circles that don't overlap when overlap is the point.
- Equal-sized circles when sets are obviously different (dishonest).
- `colors.accent` on multiple overlap regions — focal signal dies.
- Labels sitting on top of circle strokes (illegible).
- 4+ circles where 2–3 would do.
- Text inside the circle stroke area (reads as noise).
