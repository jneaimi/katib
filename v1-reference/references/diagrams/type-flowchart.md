# Flowchart

**Best for:** decision logic, algorithms, user-facing branching flows ("Should I…?"), onboarding routing, support-triage trees.

## Layout conventions

**Shape carries type, not color:**

| Shape | SVG | Meaning |
|---|---|---|
| Oval | `<rect rx="20">` or `<ellipse>` | Start / end |
| Rectangle | `<rect rx="6">` | Step / action |
| Diamond | rotated `<polygon>` | Decision (≤3 exits) |
| Small filled dot | `<circle r="4">` filled `colors.text` | Merge point where branches rejoin |

- Flow runs top→down (or left→right in AR with mirroring).
- From a diamond: conventional exits — **Yes** to the right, **No** below — but label every outgoing arrow regardless.
- Use `colors.accent` on the **happy path** *or* on the single most consequential decision — never on every decision.
- If two arrows must cross, use a small arc jump on one so the crossing is readable.

## Diamond primitive

```html
<!-- Decision diamond (120 × 80 at center CX, CY) -->
<polygon points="CX,CY-40 CX+60,CY CX,CY+40 CX-60,CY"
         fill="{{ colors.page_bg }}"
         stroke="{{ colors.text }}" stroke-width="1"/>
<text x="CX" y="CY+4" fill="{{ colors.text }}" font-size="12" font-weight="600"
      text-anchor="middle" font-family="inherit">Condition?</text>
```

## Branch labels

Place labels on a masked rect above/beside the arrow:

```html
<rect x="LABEL_X-14" y="LABEL_Y-10" width="28" height="12" rx="2"
      fill="{{ colors.page_bg }}"/>
<text x="LABEL_X" y="LABEL_Y-1" fill="{{ colors.text_secondary }}" font-size="9"
      text-anchor="middle" font-family="inherit">Yes</text>
```

## Bilingual

- Labels (`Yes` / `No`, `Start` / `End`) move to `.diagram-label` overlays on AR (`نعم` / `لا`, `ابدأ` / `انتهِ`).
- The geometry (diamond, oval, rectangles) stays identical — flowcharts read correctly in either direction because shape carries meaning.
- Optional: mirror the top→down flow to bottom→top for AR? **No** — time/process flow is universal top→down regardless of reading direction.

## Anti-patterns

- Using fill color to signal node type (shape does that — color is for accent only).
- Decision diamond with 4+ exits — refactor into nested diamonds.
- Unlabeled decision branches.
- Crossing arrows without a jump arc.
- `colors.accent` on every decision — pick one path to highlight.
