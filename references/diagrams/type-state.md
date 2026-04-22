# State Machine

**Best for:** finite state logic — order status, auth state, connection lifecycle, form wizard, job queue status.

## Layout conventions

- States are rounded rectangles (`rx=8`), labeled in brand body sans.
- **Start:** filled ink dot (`r=6`), `colors.text`.
- **End:** ringed dot — outer outline `r=8` + inner filled `r=5`, both `colors.text`.
- **Transitions:** curved arrows labeled in monospace as `event [guard] / action` (omit sections you don't need).
- **Self-loops** curve above the state.
- Orient along the dominant flow direction (left→right or top→down). Rearrange before crossing transitions.
- `colors.accent` on the state the reader should notice — typically the **error state**, or the **"happy completion"**. One, maybe two.

## Start / end primitives

```html
<!-- Start -->
<circle cx="CX" cy="CY" r="6" fill="{{ colors.text }}"/>

<!-- End (ringed) -->
<circle cx="CX" cy="CY" r="8" fill="none"
        stroke="{{ colors.text }}" stroke-width="1"/>
<circle cx="CX" cy="CY" r="5" fill="{{ colors.text }}"/>
```

## Transition label

```html
<rect x="LX-28" y="LY-10" width="56" height="12" rx="2" fill="{{ colors.page_bg }}"/>
<text x="LX" y="LY-1" fill="{{ colors.text_secondary }}" font-size="9"
      font-family="ui-monospace, monospace" text-anchor="middle">submit / save</text>
```

Format: `event [guard] / action`. Any section is optional; keep total ≤ ~24 characters.

## Self-loop

```html
<path d="M CX-20 Y-30 Q CX Y-60 CX+20 Y-30"
      fill="none" stroke="{{ colors.text_secondary }}" stroke-width="1"
      marker-end="url(#arrow)"/>
```

## Bilingual

- State names translate: `Pending` → `قيد الانتظار`. Overlay via `.diagram-label`.
- Transition labels often stay in English (they're code-like: `submit`, `timeout`, `reset`). When translating, keep them short and put them in overlays.

## Anti-patterns

- More transitions than states × 2 → likely two state machines hiding in one.
- "From any state" transitions drawn from every state — use a single annotation callout instead (`* → Error on timeout`).
- Unlabeled transitions (the whole point is *what triggers this*).
- `colors.accent` on both error AND success — pick one.
