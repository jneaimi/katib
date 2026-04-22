# Sketchy Filter (hand-drawn variant)

Optional displacement filter that wobbles every stroke and edge — turns any minimal diagram into a hand-drawn "editorial" register without changing the layout. Use when the diagram accompanies an essay rather than technical docs.

---

## Grammar

```html
<svg viewBox="0 0 600 320" role="img" aria-label="…">
  <defs>
    <filter id="sketchy" x="-2%" y="-2%" width="104%" height="104%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="4"/>
      <feDisplacementMap in="SourceGraphic" scale="1.5"/>
    </filter>
  </defs>

  <!-- Apply to a group wrapping shapes — NOT text -->
  <g filter="url(#sketchy)">
    <rect x="40"  y="60" width="160" height="80" rx="6"
          fill="{{ colors.page_bg }}" stroke="{{ colors.text }}" stroke-width="1"/>
    <rect x="260" y="60" width="160" height="80" rx="6"
          fill="{{ colors.page_bg }}" stroke="{{ colors.text }}" stroke-width="1"/>
    <line x1="200" y1="100" x2="260" y2="100"
          stroke="{{ colors.text_secondary }}" stroke-width="1"/>
  </g>

  <!-- Text sits OUTSIDE the filtered group — legibility stays crisp -->
  <text x="120" y="105" fill="{{ colors.text }}" font-size="14" font-weight="600"
        text-anchor="middle" font-family="inherit">Before</text>
  <text x="340" y="105" fill="{{ colors.text }}" font-size="14" font-weight="600"
        text-anchor="middle" font-family="inherit">After</text>
</svg>
```

---

## Tuning

| Parameter | Range | Effect |
|---|---|---|
| `baseFrequency` | 0.01–0.04 | Lower = lazy wavy lines; higher = jittery. 0.02 default. |
| `numOctaves` | 1–3 | More = more noise detail. 2 is plenty. |
| `scale` | 1–6 | 1 barely-there, 1.5 default, 2 visible, 4+ cartoon. |
| `seed` | integer | Swap for a different random pattern (deterministic — same seed → same wobble). |

---

## Critical rule

**Filter shapes, NOT text.** Displacement-mapped text becomes illegible. Structure your SVG so text lives in a sibling group *outside* the filtered group.

```html
<svg ...>
  <g filter="url(#sketchy)">
    <!-- shapes only -->
  </g>
  <!-- text here, unfiltered -->
  <text ...>Label</text>
</svg>
```

---

## When to use

- Essay / blog post / newsletter where the diagram is the hero of a narrative page.
- "Working sketch" register — showing something is mid-thought, not final architecture.
- Editorial domain (`white-paper`, `article`, `op-ed`, `case-study`).

## When not to use

- Technical documentation (precision matters).
- Business proposals, formal letters, legal docs, invoices (register mismatch).
- Diagrams with dense labels or tight alignments (the filter reads as noise).
- Dark backgrounds (wobble reads as artifact — test first).
- Anywhere the reader's job is to trace the diagram literally (flowcharts, sequence diagrams, ER).

---

## WeasyPrint notes

WeasyPrint supports `feTurbulence` + `feDisplacementMap` and renders the filter correctly at print DPI. The output is deterministic per seed, so the same source produces pixel-identical PDFs across machines.

If the filter doesn't appear in your PDF, check:
1. `<defs>` precedes the `<g>` that references the filter (SVG order matters).
2. The filter `id` matches the `filter="url(#id)"` reference exactly.
3. No typos — WeasyPrint silently drops filters it can't resolve.
