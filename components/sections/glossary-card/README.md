# glossary-card

## Purpose

Term + definition pairs — the static-print substitute for the hover tooltip. Pre-defines jargon at the point of first use (margin), inline as a definition row inside body text, or batched at the end of a chapter as a glossary.

## When to use

- A technical term appears for the first time and the reader cannot pause to look it up
- A loaned word (English in an Arabic tutorial, Arabic in an English tutorial) needs phonetic or origin gloss
- An end-of-chapter glossary that doubles as a quick-reference index
- Any place a hover tooltip would be the digital answer — replace with margin-card on the same spread

## Inputs

```yaml
- component: glossary-card
  variant: grid              # margin-card | inline-row | grid (default)
  inputs:
    heading: "Glossary"      # optional — defaults to "Glossary" / "المعجم"
    columns: 2               # 1 | 2 | 3 — only for grid variant (default: 2)
    items:
      - term: "Idempotency"
        definition: "Property of an operation that can be applied multiple times without changing the result beyond the initial application."
        pronunciation: "/ˌaɪ.dəm.poʊˈtɛn.si/"   # optional — phonetic or loan-origin hint
        see_also: "Side effect, Replay"          # optional — comma-separated peer terms
      - term: "Webhook"
        definition: "An HTTP callback that fires when an event occurs in a third-party system."
```

## Variants

- **margin-card** — single sticky card (use one item). Sized to fit beside body text on the same spread. Accent leading-rule colour-codes it as a definition. Best for "first use" glossing where the reader must not flip pages.
- **inline-row** — definition lives in the reading flow as a single block, accented with a leading rule. Best for one-off glossing in tight prose.
- **grid** (default) — N-column batched glossary. Best for end-of-chapter or end-of-tutorial reference.

## Default labels

| Field | EN | AR |
|---|---|---|
| `heading` | `Glossary` | `المعجم` |
| `see_also.label` | `See also` | `انظر أيضاً` |

## Bilingual notes

- All edge rules use logical `border-inline-start` / `margin-inline-start`, so AR mirrors automatically.
- The `pronunciation` field is rendered in monospace and is direction-agnostic — useful for embedding an English IPA alongside an Arabic term, or an Arabic phonetic alongside a Latin technical term. WeasyPrint handles the direction inheritance correctly.
- In AR, headings drop their EN-styled letter-spacing + uppercase, since neither convention applies to Arabic typography.

## Visual semantics

- The headword sits in the display font, bold, at full text colour — it's the anchor.
- The definition steps down to secondary text colour to keep the reader's eye on the term first.
- `see_also` is in tertiary text, as a quiet cross-reference.
- The pronunciation field is monospace + tertiary — visually marked as metadata, not prose.

## Pedagogy

Replaces the hover-tooltip pattern (Stripe Docs, Microsoft Learn) with a print-native equivalent. Inline-row is the analogue to a gloss-on-first-use; grid is the back-of-book glossary; margin-card is the marginal note. All three support the "pre-training" principle from Mayer's multimedia learning theory: pre-define the vocabulary the reader will need, before they need it, so that working memory isn't taxed mid-procedure.

## Companion components

- `tutorial-step` — the procedure the glossary defines vocabulary for
- `cheat-sheet` — pairs naturally at the end of a tutorial; cheat-sheet is the procedural quick-ref, glossary is the conceptual one
- `objectives-box` — at the start of a module; glossary is the lexical scaffold for the objectives

Part of the Tutorial Component Pack — Sprint 3 / Phase C.
