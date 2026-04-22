# Swimlane

**Best for:** cross-functional processes, RACI-style flows, vendor handoffs, multi-team shipping workflows.

## Layout conventions

- Horizontal lanes (or vertical columns) — one per actor / team / role.
- Label each lane in the left margin (or top) with a monospace eyebrow.
- Lane dividers: 1px hairlines in `colors.border`.
- Process steps are rectangles placed inside the lane of the actor performing them.
- Arrows show the flow of work across lanes.
- **Handoffs** (arrows crossing lane boundaries) are the most important edges — consider `colors.accent` on the handoff that introduces the most coupling or latency.
- Don't force equal step count per lane; a lane with one step is fine.

## Lane primitive

```html
<!-- Lane divider -->
<line x1="0" y1="LANE_Y" x2="VIEWBOX_W" y2="LANE_Y"
      stroke="{{ colors.border }}" stroke-width="1"/>

<!-- Lane label (left margin) -->
<text x="20" y="LANE_Y+24" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace" letter-spacing="0.14em">DESIGN</text>
```

## Step (inside a lane)

Standard node-box from [primitives.md](primitives.md), positioned at `x, y` inside the lane:

```html
<rect x="120" y="LANE_Y+20" width="140" height="48" rx="6"
      fill="{{ colors.page_bg }}"
      stroke="{{ colors.text }}" stroke-width="1"/>
<text x="190" y="LANE_Y+48" fill="{{ colors.text }}" font-size="12" font-weight="600"
      text-anchor="middle" font-family="inherit">Wireframe</text>
```

## Handoff arrow (crosses lanes)

```html
<!-- Accent on the critical handoff -->
<path d="M 260 LANE1_Y+44 Q 300 LANE1_Y+44 300 LANE2_Y+44 T 340 LANE2_Y+44"
      fill="none" stroke="{{ colors.accent }}" stroke-width="1.2"
      marker-end="url(#arrow-accent)"/>

<rect x="282" y="MID_Y-10" width="36" height="12" rx="2" fill="{{ colors.page_bg }}"/>
<text x="300" y="MID_Y-1" fill="{{ colors.accent }}" font-size="8"
      font-family="ui-monospace, monospace" text-anchor="middle"
      letter-spacing="0.06em">HANDOFF</text>
```

## Bilingual

- Lane labels (team / role names) go in `.diagram-label` overlays for AR: `التصميم`, `الهندسة`, `المنتج`.
- Step names similarly overlaid.
- **Mirror horizontal flow for AR** — processes in Arabic read right→left (use the `direction` transform from [rtl-notes.md](rtl-notes.md)).
- Lane *order* stays fixed regardless of direction — role hierarchy is not directional.

## Anti-patterns

- Lanes without labels.
- A step drawn across two lanes (pick one owner — that's the whole point).
- Arrows that snake back and forth — reorder steps so the flow is mostly straight.
- More than 5 lanes — split by subsystem or project phase.
- `colors.accent` on every handoff — pick one (usually the one with the longest delay or the most coupling).
