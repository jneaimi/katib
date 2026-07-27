# prerequisites-grid

## Purpose

Gating checklist of required items — tools, skills, accounts, materials — placed before the first step. Prevents mid-tutorial dead-ends where the reader discovers they needed something they don't have. Implements Mayer's pre-training principle.

## When to use

- Page 2-3 of a tutorial, after `outcome-preview` and before the first numbered step
- Top of a recipe-card (ingredients box doubles as this)
- Top of an assembly guide (tools + parts list)
- Top of a course-module handout (skills/concepts the unit assumes)

## Inputs

```yaml
- component: prerequisites-grid
  variant: grid          # grid (default) | checklist
  inputs:
    heading: "Before you start"   # optional — defaults per-lang
    columns: 2                    # 1 | 2 | 3 | 4 (grid only; checklist is always 1)
    items:
      - name: "Node.js 20 or later"
        detail: "Verify with `node -v`"
      - name: "A Stripe account"
        detail: "Free tier is fine for testing"
      - name: "Basic terminal familiarity"
        detail: "Helpful, not strictly required"
        required: false           # optional item (dashed checkbox)
```

## Variants

- **checklist** — single column, dense vertical rhythm. Best when the list is long (6+ items) or when each item has a longer `detail`.
- **grid** (default) — N-column card layout, tag-bg-tinted. Best for short, scannable lists (3–6 items, terse details).

## `required` flag

- `required: true` (default) — solid-bordered checkbox; the reader is meant to tick it as they verify they have the item.
- `required: false` — dashed-bordered checkbox; the item is nice-to-have, not strictly needed.

## Default headings

| Language | Default `heading` |
|---|---|
| EN | `Before you start` |
| AR | `قبل أن تبدأ` |

## Bilingual notes

- Heading uses `display` font in uppercase + tracked in EN; AR strips both and bumps to 12pt.
- The grid columns flow LTR/RTL via `dir="rtl"` on the `<section>`. Card content stays logical (name first, detail under).

## Distinction from `sections-grid`

| Feature | `prerequisites-grid` | `sections-grid` |
|---|---|---|
| Intent | Gating list before a procedure | Summary cards after a procedure |
| Density | Tight (9-11pt cards) | Looser (cards have headlines + body paragraphs) |
| Checkbox column | Always present | None |
| Required flag | Yes (solid vs dashed) | No |
| Heading style | Small uppercase eyebrow | Large card titles |

If the content fits the gating-checklist semantics, use this. If it's a summary or a feature breakdown, use `sections-grid`.

## Companion components

- `outcome-preview` — sits above this on the same page
- `meta-strip` — sits above the outcome-preview
- `tutorial-step` — what comes after this block

Part of the Tutorial Component Pack — Sprint 1 / Phase A.
