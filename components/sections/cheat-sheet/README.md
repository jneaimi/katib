# cheat-sheet

## Purpose

Quick-reference recap of commands, env vars, shortcuts, or formulas grouped by topic. The "tear-out page" of a tutorial — distilled, scannable, monospace-friendly. Visually distinct from `data-table` (which is for tabular comparison) by intent: a cheat-sheet is for *lookup*, not for *reading*.

## When to use

- Final page of a tutorial as a take-away reference
- Mid-tutorial recap after a long step-block (env vars introduced so far)
- A shareable "print this and pin it to your monitor" artefact
- Anywhere the reader will return to look up a specific value, not to learn

## Inputs

```yaml
- component: cheat-sheet
  variant: card-grid          # card-grid (default) | dense-table
  inputs:
    heading: "Cheat sheet"        # optional — defaults per-lang
    subtitle: "Print this page"   # optional
    columns: 2                    # 2 or 3 — only for card-grid (default: 2)
    groups:
      - heading: "Environment variables"
        items:
          - label: "[KEY]"
            value: "sk_test_..."
            hint: "Authenticates SDK calls"
          - label: "[WEBHOOK_SECRET]"
            value: "whsec_..."
            hint: "Verifies inbound signatures"
      - heading: "CLI commands"
        items:
          - label: "stripe listen"
            value: "--forward-to localhost:4242/webhook"
          - label: "stripe trigger"
            value: "[event.type]"
```

## Variants

- **card-grid** (default) — groups laid out as cards in a 2- or 3-column grid. Best for visual variety and 4+ topic groups. Each card stays page-break-safe.
- **dense-table** — groups stacked vertically, items as single-line rows with right-aligned values (left-aligned in AR). Best for one-page recap of many small items.

## Default labels

| Field | EN | AR |
|---|---|---|
| `heading` | `Cheat sheet` | `البطاقة المرجعية` |

## Bilingual notes

- Headings drop letter-spacing + uppercase in AR; the bottom-rule under headings is preserved.
- In `dense-table`, value text-align flips: `right` in EN (so the eye lands on the value at the end of the row), `left` in AR (the same logical-trailing edge).
- Subtitle italic dropped in AR.

## Visual semantics

- Top heading sits on a heavy accent rule, signalling "this is the take-away page".
- Group headings are accent-coloured and small-caps to act as section dividers within the recap, never to compete with the main heading.
- Labels in display font + bold so the eye locks onto the headword.
- Values in monospace by default — cheat-sheets typically contain commands, code, file paths, env names. Monospace also visually marks them as "things to copy" vs. prose.
- Hints in primary font + tertiary text — the soft gloss when a value alone isn't enough.

## Distinct from `data-table`

| Pattern | `data-table` | `cheat-sheet` |
|---|---|---|
| Intent | Read row-by-row, compare across columns | Lookup a specific label, copy the value |
| Layout | True table with column headers | Grouped label/value pairs |
| Density | Lower — built for prose | Higher — built for scanning |
| Position | Mid-document, body of a section | End-of-document, recap |
| Font | Mostly primary | Mostly monospace |

## Pedagogy

Sources: O'Reilly tear-out cheat-sheets, Stripe's API quick-reference cards, every cooking-conversion table at the back of a cookbook, vim/emacs keybinding cards. The pedagogical move: front-load the recap *as a recap*, not as a learning beat. The reader has already absorbed the material; the cheat-sheet is a memory aid for *next time*. Embodies Mayer's signaling principle: separate the lookup-layer from the reading-layer with distinct visual chrome so the brain mode-switches automatically.

## Companion components

- `glossary-card` — the conceptual cheat-sheet (vocabulary lookups), pairs naturally on a facing page
- `data-table` — when you need column headers and prose comparison, not a recap
- `whats-next` — the "you've finished, here's the cheat-sheet, here's where to go" trio is the canonical tutorial ending

Part of the Tutorial Component Pack — Sprint 3 / Phase C.
