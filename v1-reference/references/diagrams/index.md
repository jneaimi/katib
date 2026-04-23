# Katib — Diagram Catalog

**Print-grade editorial diagrams. Inline SVG. Jinja-tokenized colors. WeasyPrint-native.**

Thirteen diagram types, two editorial primitives, one shared design system. Type-specific conventions live in their own `type-*.md` files and are loaded only when you pick a type. This index is the entry point — philosophy, selection guide, complexity budget, universal anti-patterns.

> **Attribution.** The catalog structure, complexity budget, and anti-pattern taxonomy are adapted from Cathryn Lavery's [`diagram-design`](https://github.com/cathrynlavery/diagram-design) skill (MIT). Katib-specific additions: Jinja color interpolation, WeasyPrint constraints, bilingual (EN + AR) overlay patterns, per-domain font inheritance.

---

## 1. Philosophy

**The highest-quality move is usually deletion.** Every node earns its place. Every connection carries information. The accent color is reserved for the 1–2 things the reader should look at first.

Applied to Katib diagrams:

- Two nodes that always travel together are one node.
- If a relationship is obvious from layout, remove the line.
- Accent (`colors.accent`) is **editorial, not a flag.** Using it on 5 nodes erases the signal.
- The diagram isn't done when everything is added — it's done when nothing can be removed.

**Target density: 4/10.** Enough to be technically complete. Not so dense it needs a guide. Above 9 nodes, it's probably two diagrams.

---

## 2. When to reach for a diagram

Use for any of the 13 types (§3) when the reader will learn more from a visual than from prose, a table, or a bulleted list.

**Don't diagram:**
- Lists of things → table or bullets.
- Simple before/after → two-column table.
- One-shape "diagrams" → just write the sentence.
- Very dense data → chart, not diagram.

Before drawing, ask: *Would the reader learn more from this than from a well-written paragraph?* If no, don't draw.

---

## 3. Type selection

| If you're showing… | Use | Reference |
|---|---|---|
| Components + connections in a system | **Architecture** | [type-architecture.md](type-architecture.md) |
| Decision logic with branches | **Flowchart** | [type-flowchart.md](type-flowchart.md) |
| Time-ordered messages between actors | **Sequence** | [type-sequence.md](type-sequence.md) |
| States + transitions + guards | **State machine** | [type-state.md](type-state.md) |
| Entities + fields + relationships | **ER / data model** | [type-er.md](type-er.md) |
| Events positioned in time | **Timeline** | [type-timeline.md](type-timeline.md) |
| Cross-functional process with handoffs | **Swimlane** | [type-swimlane.md](type-swimlane.md) |
| Two-axis positioning / prioritization | **Quadrant** | [type-quadrant.md](type-quadrant.md) |
| Hierarchy through containment / scope | **Nested** | [type-nested.md](type-nested.md) |
| Parent → children relationships | **Tree** | [type-tree.md](type-tree.md) |
| Stacked abstraction levels | **Layer stack** | [type-layers.md](type-layers.md) |
| Overlap between sets | **Venn** | [type-venn.md](type-venn.md) |
| Ranked hierarchy or conversion drop-off | **Pyramid / funnel** | [type-pyramid.md](type-pyramid.md) |

### Rules of thumb
- If a 3-column table communicates the same thing, pick the table.
- If you're combining two types, pick the dominant axis — don't hybridize grammars.
- If you're past the complexity budget (§6), split into overview + detail.

**Always load the relevant `type-*.md` before drawing** — it contains layout conventions, anti-patterns, and per-type primitives.

---

## 4. Shared primitives

Before jumping into a specific type, every diagram needs these shared pieces:

| File | Contents |
|---|---|
| [style.md](style.md) | Semantic role map — `colors.accent` vs `colors.text` etc. — and the node-type → treatment table. **Read first.** |
| [primitives.md](primitives.md) | Arrow markers, mask rects, node-box pattern, legend strip, arrow labels |
| [rtl-notes.md](rtl-notes.md) | Arabic overlay pattern, flow-direction mirroring, bilingual alt text |
| [primitive-annotation.md](primitive-annotation.md) | Italic-serif editorial callouts (marginalia) |
| [primitive-sketchy.md](primitive-sketchy.md) | Optional hand-drawn SVG-filter variant for essays |

Type-specialized primitives (lifeline, activation bar, trapezoid polygon) live in the relevant `type-*.md`.

---

## 5. Universal anti-patterns

These mark "AI slop" diagrams regardless of type:

| Anti-pattern | Why it fails |
|---|---|
| Dark mode + cyan/purple glow | Reads "technical" without design decisions |
| Identical boxes for every node | Erases hierarchy |
| Legend floating *inside* the diagram area | Collides with nodes |
| Arrow labels with no masking rect | Bleeds through the line |
| Vertical `writing-mode` text on arrows | Unreadable |
| Shadow on any element | Shadows are out. Hairlines are in. |
| `rounded-2xl` / heavy radius on boxes | Max radius 6–10px or none |
| Accent (`colors.accent`) on every "important" node | Accent is 1–2 editorial highlights, not a signaling system |
| 3 equal-width summary cards as default "cover" for the diagram | Generic grid — vary widths, or drop the grid |
| Monospace as a blanket "dev" font | Mono is for *technical* content (ports, URLs, field types). Names go in the body sans. |

Type-specific anti-patterns live in each `type-*.md`.

---

## 6. Complexity budget

Hard ceilings, per diagram:

| Limit | Rule |
|---|---|
| Max nodes | 9 |
| Max arrows / transitions | 12 |
| Max accent elements | 2 |
| Max lifelines (sequence) | 5 |
| Max lanes (swimlane) | 5 |
| Max items (quadrant) | 12 |
| Max entities (ER) | 8 |
| Max nesting levels (nested) | 6 |
| Max tree depth | 4 |
| Max layers (layer stack) | 6 |
| Max circles (venn) | 3 |
| Max layers (pyramid / funnel) | 6 |
| Max annotation callouts | 2 |

Over budget → split into two diagrams (overview + detail). Don't compress.

---

## 7. Layout hygiene

### 4px grid

**All values — font sizes, padding, node dimensions, gaps, x/y coords — divisible by 4.** Non-negotiable.

| Category | Allowed values |
|---|---|
| Font sizes (px) | 8, 9, 12, 14, 16, 20, 24, 28, 32, 40 |
| Node width / height | 80, 96, 112, 120, 128, 140, 144, 160, 180, 200, 240, 320 |
| x / y coordinates | multiples of 4 |
| Gap between nodes | 20, 24, 32, 40, 48 |
| Padding inside boxes | 8, 12, 16 |
| Border radius | 4, 6, 8 |

Exempt: stroke widths (0.8, 1, 1.2), opacity values, and the 22×22 dot-pattern.

Quick check: if a coordinate ends in 1, 2, 3, 5, 6, 7, 9 — fix it.

### Sizing

- **Always set `viewBox`** — it's what makes the SVG scale crisply.
- **Omit hardcoded `width`/`height`** on the `<svg>` root. Size via CSS (`style="max-width: 100%;"`).
- **`role="img"` + `aria-label`** — for PDF accessibility tree and AR/EN captioning.

```html
<figure>
  <svg viewBox="0 0 600 80" role="img" aria-label="Process: Plan → Build → Ship" style="max-width: 100%;">
    <!-- ... -->
  </svg>
  <figcaption>Figure 1: Three-phase delivery</figcaption>
</figure>
```

---

## 8. Focal rule

`colors.accent` goes on **1–2 elements per diagram. Maximum.**

Everything else is `colors.text` / `colors.text_secondary` / `colors.border`. If you're tempted to accent 4 things, you haven't decided what's focal yet. Go back, pick one.

---

## 9. Loading order (progressive disclosure)

1. **This file** (`index.md`) — always in context when a diagram is being made.
2. **`style.md`** — always before the first diagram in a new template.
3. **`type-<name>.md`** — only when you pick a type.
4. **`primitives.md`** — as needed (most types use the arrow marker + node-box primitives).
5. **`primitive-annotation.md`** / **`primitive-sketchy.md`** — only if the chosen diagram uses them.
6. **`rtl-notes.md`** — only on `.ar.html` templates.

Keeps the working context tight even with 17 reference files.

---

## 10. Legacy

The old monolithic `references/diagrams.md` still exists as a compatibility stub pointing here. `scripts/build.py --check` still references it in error messages for the Arabic-in-SVG rule — that rule is now documented in [rtl-notes.md](rtl-notes.md), with the stub left in place so existing error strings don't break.
