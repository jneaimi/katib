# before-after

## Purpose

Paired panels showing **initial vs final state** with the same aspect ratio enforced. Same camera angle, same crop, same framing — so the reader's eye lands on what *changed* instead of recomposing the scene. Common in editing, refactoring, assembly, and cooking tutorials.

## When to use

- After a refactor, redesign, or migration step (the diff between old and new state)
- After a cooking step that transforms ingredients visibly (raw vs cooked, mixed vs kneaded)
- After an assembly step that reveals a "wrong vs right" pairing (IKEA's reversed-part insets)
- Anywhere the most concise way to teach is "look at what changed"

## Inputs

```yaml
- component: before-after
  variant: side-by-side    # side-by-side (default) | stacked | filmstrip
  inputs:
    heading: "Before & after"   # optional — defaults per-lang
    before:
      image:
        source: user-file        # user-file or screenshot (no gemini)
        path: /abs/path/to/before.png
      label: "Before"            # optional badge — defaults to per-lang "Before"
      caption: "Initial state — describe what the reader sees here."
    after:
      image:
        source: user-file
        path: /abs/path/to/after.png
      label: "After"
      caption: "Final state — describe what's different."
    middle:                       # OPTIONAL — only used in filmstrip variant
      image:
        source: user-file
        path: /abs/path/to/midstate.png
      label: "Mid-state"
      caption: "Interim state — what should appear at the halfway mark."
```

## Variants

- **side-by-side** (default) — panels in a row. Best for portrait source images that read clearly at half the page width.
- **stacked** — panels stacked vertically (full-width each). Best for landscape source images where side-by-side would shrink each too small to read.
- **filmstrip** — 3 panels: before, middle, after. Use the `middle` input. Best when one interim state is critical to the story (a dough mid-rise, a truck mid-install, a refactor halfway through).

## Default labels

| Field | EN | AR |
|---|---|---|
| `heading` | `Before & after` | `قبل وبعد` |
| `before.label` | `Before` | `قبل` |
| `middle.label` | `Mid-state` | `حالة وسيطة` |
| `after.label` | `After` | `بعد` |

## Visual semantics

- The "before" badge is **accent-coloured**. The "after" badge is **success-green**. The "middle" badge is **neutral grey**. Colour codes the temporal direction at a glance.
- Both/all panels lock to the same image height (70mm side-by-side; 80mm stacked; 55mm filmstrip). Source images crop with `object-fit: cover` so irregular sources don't break the grid.
- Captions sit below each image with a subtle separator rule, allowing per-panel commentary without breaking the comparison rhythm.

## Bilingual notes

- Badge `position: absolute` flips from `left` (EN) to `right` (AR) so the label always sits in the logical-leading corner of each panel.
- Captions inherit `direction: rtl` from the section root in AR, so prose flows correctly.
- The "before is on the left" convention DOES flip in AR — `flex-direction: row` + `dir="rtl"` puts before on the visual right (which is the AR logical-leading side, matching reading order).

## Pedagogy

Source pattern: cookbook before/after of dough rising; Apple HIG redesign before/after; IKEA's "wrong vs right" reversed-part panels; technical-editing diff illustrations. The pedagogical move is: **anchor the unchanged framing**. When the camera doesn't move, the reader's perceptual system locks onto the delta automatically.

## Constraints

- The component enforces the same image dimensions across panels via `object-fit: cover`. If your source images are wildly different aspect ratios, the cover-fit will crop them inconsistently — pre-process them to similar ratios for cleanest output.
- For comparisons of more than 3 states, use a different component (e.g. a custom `module raw_body` with a custom grid). This component is deliberately scoped to the canonical 2 (or 3) states.

## Companion components

- `callout-anchor` — pairs naturally when the comparison is about specific regions (annotate the before, then annotate the after with the same numbering scheme)
- `tutorial-step` — what comes before this block (the step that produced the change)
- `checkpoint` — alternative pattern when the reader doesn't need to see "the wrong way" — just "here's what you should now have"

Part of the Tutorial Component Pack — Sprint 2 / Phase B.
