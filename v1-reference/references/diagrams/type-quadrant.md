# Quadrant

**Best for:** prioritization (Impact × Effort), positioning (Reach × Frequency), portfolio maps, 2×2 decision frames.

## Layout conventions

- 2×2 grid. **Axis lines:** 1px `colors.text` cross through the center.
- **Axis labels — Jobs-minimal.** One single word at each arrow tip:
  - No glyphs (`↑`, `→`, `←`, `↓`) baked into the label.
  - No parentheticals, no `HIGH` / `LOW` modifiers.
  - Monospace 9px, regular weight, tracked 0.18em, uppercase.
  - Flank the arrow tips — never sit labels on top of the axis line.
  - Shorten the arrow ~60–80px inside the viewBox edge to leave breathing room.
- Never label at the midpoint.
- **Items:** small labeled dots (`r=4`) positioned in the quadrants. Labels 8–10px away; don't let labels cross axis lines.
- `colors.accent` on the "do first" item (typically top-right).
- Limit to ~12 items; cluster or split beyond that.

## Axis cross

```html
<!-- Horizontal axis -->
<line x1="80" y1="200" x2="720" y2="200"
      stroke="{{ colors.text }}" stroke-width="1"
      marker-end="url(#arrow)"/>

<!-- Vertical axis -->
<line x1="400" y1="360" x2="400" y2="40"
      stroke="{{ colors.text }}" stroke-width="1"
      marker-end="url(#arrow)"/>

<!-- Axis labels (beyond the tips, Jobs-minimal) -->
<text x="400" y="28" fill="{{ colors.text }}" font-size="9"
      font-family="ui-monospace, monospace" text-anchor="middle"
      letter-spacing="0.18em">IMPACT</text>
<text x="736" y="204" fill="{{ colors.text }}" font-size="9"
      font-family="ui-monospace, monospace" text-anchor="start"
      letter-spacing="0.18em" dominant-baseline="middle">EFFORT</text>
```

## Item

```html
<circle cx="560" cy="120" r="4" fill="{{ colors.text }}"/>
<text x="568" y="124" fill="{{ colors.text }}" font-size="10"
      font-family="inherit">Refactor billing</text>
```

## Focal item (accent)

```html
<circle cx="560" cy="80" r="5" fill="{{ colors.accent }}"/>
<text x="568" y="84" fill="{{ colors.accent }}" font-size="11" font-weight="600"
      font-family="inherit">Launch v2</text>
```

## Bilingual

- Axis labels translate: `IMPACT` → `الأثر`, `EFFORT` → `الجهد`. Overlay via `.diagram-label` with Jobs-minimal styling preserved.
- Item labels overlay.
- **Don't mirror** quadrants — axes have fixed directional meaning (up/right = more). Reversing them confuses the reader, regardless of language.

## Anti-patterns

- Four filled quadrants in different colors — position + label does the work; color noise weakens it.
- Items placed on axis lines (ambiguous quadrant).
- Missing axis names.
- Bolded axis labels, arrow glyphs in the text (`↑ IMPACT`), or `HIGH / LOW` parentheticals — all forbidden. Jobs-minimal is non-negotiable.
- `colors.accent` on multiple items — pick the single "do first".

---

## Consultant 2×2 variant (scenario matrix)

A **layout variant** of the standard quadrant — same house skin. The grammar shifts: axes hold a **range** rather than a measurement; cells hold **named scenarios** rather than positioned items.

**Use when:** you're framing four futures, archetypes, or strategic options across two independent drivers — classic scenario planning, positioning frames, or 2×2 strategy decks. The reader should come away with four named bets, not a point cloud.

**Do not use** for prioritization, density maps, or anything where the *position inside* a cell carries meaning — that's the standard quadrant above.

### What makes it the consultant variant

| Move | Standard quadrant | Consultant variant |
|---|---|---|
| Axis arrows | single-ended | **double-ended** (`marker-start` + `marker-end`) |
| Cell content | small dots with labels | **named scenario + 1–3 line description** |
| Quadrant corner | short tag (e.g. `DO FIRST`) | **numbered tag + axis combination** (`01 · DRIVER-A / DRIVER-B`) |
| Focal accent | `accent` on one *item* | `accent` on one *quadrant* — tinted bg + accent stroke + accent corner tag |
| Axes | 1px `text` | **1.2px `text`** — axes carry more of the figure |

### Layout

- Four cells, equal size (240×160 or 280×180 are good defaults), arranged with a 40–60px gap from the axis cross.
- Axis cross passes *between* the cells, not through them.
- Arrow tips live ~20–40px outside the outermost cell edge; single-word axis labels sit ~12px beyond each tip.
- Exactly **one** focal cell. Picking none makes it a placeholder; picking two erases the signal.
- Keep the legend strip + horizontal rule at the bottom.

### Cell treatment

| Cell | Fill | Stroke |
|---|---|---|
| Focal (1 only) | accent tint (triple-rect pattern from [style.md](style.md)) | `colors.accent` at 1.2px |
| Non-focal | `store` treatment (`ink @ 0.04` + `muted @ 0.28`) | as above |

### Anti-patterns (variant-specific)

- Unnamed cells ("Scenario 1/2/3/4") in a shipped diagram — OK as a template; not OK as a finished artifact.
- `colors.accent` on more than one cell.
- 3×3 or 2×3 grids — those are different diagrams, not this variant.
- Positioning dots *inside* the cells — if position matters, use the standard quadrant.
- Corner tags that disagree with the axis labels (e.g. axis says `REMOTE / IN-PERSON` but tag reads `HIGH REMOTE / LOW AI`).
