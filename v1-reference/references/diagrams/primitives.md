# Core SVG Primitives

Universal building blocks, used by every diagram type. Type-specialized primitives (lifeline, activation bar, trapezoid polygon, axis cross) live in the relevant `type-*.md`.

---

## Background

**Default: transparent.** The diagram sits directly on the page — no container background. The document's body color bleeds through.

### Optional: dotted paper

For long-form editorial diagrams that benefit from textured ground (essays, hero diagrams on a dedicated page), add the dots pattern:

```html
<svg viewBox="0 0 800 400" role="img" aria-label="…" style="max-width:100%;">
  <defs>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.9" fill="{{ colors.text }}" opacity="0.10"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="{{ colors.page_bg }}"/>
  <rect width="100%" height="100%" fill="url(#dots)" opacity="0.6"/>
  <!-- diagram body -->
</svg>
```

**Don't** add the dot pattern to diagrams inside a product page, slide deck, or financial doc — the texture compounds with surrounding chrome and reads as noise.

---

## Arrow markers

Define all three variants in `<defs>` at the top of every SVG. Re-use via `marker-end="url(#arrow)"` on any `<line>` or `<path>`.

```html
<defs>
  <!-- Default: muted / neutral arrows -->
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{{ colors.text_secondary }}"/>
  </marker>

  <!-- Accent: focal / primary flow -->
  <marker id="arrow-accent" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{{ colors.accent }}"/>
  </marker>

  <!-- Link: HTTP/API/external -->
  <marker id="arrow-link" viewBox="0 0 10 10" refX="8" refY="5"
          markerWidth="6" markerHeight="6" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{{ colors.accent_2 }}"/>
  </marker>
</defs>
```

### Arrow variants

| Variant | Stroke | Marker | When |
|---|---|---|---|
| Default | `colors.text_secondary` | `#arrow` | Internal, generic flow |
| Accent | `colors.accent` | `#arrow-accent` | Primary / highlighted / headline flow |
| Link | `colors.accent_2` | `#arrow-link` | HTTP/API calls, external systems |
| Dashed | any color, `stroke-dasharray="5,4"` | matching marker | Optional, passive, return, async |

**Draw arrows before nodes** so z-order puts lines behind shapes.

```html
<!-- Default arrow -->
<line x1="120" y1="40" x2="240" y2="40"
      stroke="{{ colors.text_secondary }}" stroke-width="1" marker-end="url(#arrow)"/>

<!-- Accent arrow (primary flow) -->
<line x1="120" y1="40" x2="240" y2="40"
      stroke="{{ colors.accent }}" stroke-width="1.2" marker-end="url(#arrow-accent)"/>

<!-- Dashed async/return -->
<line x1="240" y1="40" x2="120" y2="40"
      stroke="{{ colors.text_secondary }}" stroke-width="1"
      stroke-dasharray="5,4" marker-end="url(#arrow)"/>
```

---

## Node box (full pattern)

The canonical node — five layers, in z-order:

```html
<!-- 1. Opaque paper mask — prevents arrows bleeding through transparent fills -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="{{ colors.page_bg }}"/>

<!-- 2. Styled box -->
<rect x="X" y="Y" width="W" height="H" rx="6"
      fill="FILL" stroke="STROKE" stroke-width="1"/>

<!-- 3. Type tag — rectangular (rx=2), NOT a pill -->
<rect x="X+8" y="Y+6" width="28" height="12" rx="2"
      fill="none" stroke="STROKE" stroke-width="0.8" opacity="0.40"/>
<text x="X+22" y="Y+15" fill="STROKE" font-size="7"
      font-family="ui-monospace, monospace" text-anchor="middle"
      letter-spacing="0.08em" opacity="0.8">API</text>

<!-- 4. Node name — brand body sans, human-readable -->
<text x="CX" y="CY+2" fill="{{ colors.text }}" font-size="12" font-weight="600"
      text-anchor="middle" font-family="inherit">Node Name</text>

<!-- 5. Technical sublabel — monospace -->
<text x="CX" y="CY+18" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace" text-anchor="middle">tech:port</text>
```

`FILL` and `STROKE` come from the node-type → treatment table in [style.md](style.md).

---

## Arrow labels

Every arrow label needs an opaque rect behind it. Without one, it bleeds through the line.

```html
<!-- Opaque mask -->
<rect x="MID_X-18" y="ARROW_Y-12" width="36" height="12" rx="2"
      fill="{{ colors.page_bg }}"/>

<!-- Label -->
<text x="MID_X" y="ARROW_Y-3" fill="{{ colors.text_tertiary }}" font-size="8"
      font-family="ui-monospace, monospace" text-anchor="middle"
      letter-spacing="0.06em">WRITE</text>
```

**Rules:**
- ≤14 characters
- Uppercase, tracked `letter-spacing="0.06em"`
- Centered on segment midpoint
- 8–10px above the line
- Never `writing-mode: vertical-rl` — unreadable in print

---

## Legend strip

**Never put the legend inside the diagram area.** Place it as a horizontal strip below all nodes, with a hairline separator.

```html
<!-- Expand the SVG viewBox height by ~60px to accommodate the legend -->
<line x1="30" y1="LEGEND_Y-8" x2="VIEWBOX_W-30" y2="LEGEND_Y-8"
      stroke="{{ colors.border }}" stroke-width="0.8"/>
<text x="30" y="LEGEND_Y+8" fill="{{ colors.text_secondary }}" font-size="8"
      font-family="ui-monospace, monospace" letter-spacing="0.14em">LEGEND</text>

<!-- Items — horizontal row, ~160px apart -->
<!-- swatch 1 -->
<rect x="110" y="LEGEND_Y+2" width="16" height="10" rx="2"
      fill="{{ colors.accent }}" opacity="0.08"
      stroke="{{ colors.accent }}" stroke-width="1"/>
<text x="132" y="LEGEND_Y+10" fill="{{ colors.text }}" font-size="9"
      font-family="inherit">Focal</text>

<!-- swatch 2 -->
<line x1="240" y1="LEGEND_Y+8" x2="260" y2="LEGEND_Y+8"
      stroke="{{ colors.text_secondary }}" stroke-width="1"/>
<text x="270" y="LEGEND_Y+10" fill="{{ colors.text }}" font-size="9"
      font-family="inherit">Default arrow</text>
```

---

## Hairline dividers

For internal dividers, lane separators, axis baselines — 1px, soft color.

```html
<line x1="0" y1="Y" x2="W" y2="Y" stroke="{{ colors.border }}" stroke-width="1"/>
```

For axis or emphasis baselines, step up to `stroke-width="1.2"` and use `{{ colors.border_strong }}` or `{{ colors.text }}`.

---

## Quick-copy snippets

Ready-to-include Jinja partials live in [snippets/](snippets/):

| File | What it provides |
|---|---|
| `snippets/arrow-markers.svg.j2` | All three marker definitions |
| `snippets/node-box.svg.j2` | Parameterized node box with type tag + name + sublabel |
| `snippets/annotation-callout.svg.j2` | Italic-serif callout with Bézier leader |
| `snippets/legend-strip.svg.j2` | Bottom legend strip |

Use via `{% include 'snippets/arrow-markers.svg.j2' %}` inside your `<defs>` block.

---

## Constraints

- `viewBox` required. `width` / `height` on the `<svg>` root forbidden.
- Round all coordinates to integers — sub-pixel values cause WeasyPrint rendering artifacts.
- Keep text ≥8pt (smaller won't print cleanly at 150 DPI).
- 4–6pt padding inside boxes (see [index.md](index.md) §7).
