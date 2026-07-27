# try-it-yourself

## Purpose

Exercise + answer block. The static-print substitute for the interactive knowledge-check quiz. Forces the reader to attempt the problem before peeking at the solution.

## When to use

- After a step-group, to verify the reader can apply what they just read
- Mid-tutorial, as a "stop and try" beat between concept and next concept
- End of a chapter / module as a reinforcement exercise
- Anywhere the digital version would be a "Check your understanding" widget

## Inputs

```yaml
- component: try-it-yourself
  variant: flipped-answer    # inline-answer (default) | flipped-answer
  inputs:
    heading: "Try it yourself"   # optional — defaults per-lang
    prompt: |
      Given the [endpoint] handler from page 4, what error response should
      the server return if the [signature-header] is missing?
    hint: "See the constructor signature on page 5."   # optional
    answer: |
      A 401 Unauthorized. The signature header is required for verification —
      without it, the request can't be trusted to have come from [service].
    answer_label: "Answer"      # optional — defaults per-lang
```

## Variants

- **inline-answer** (default) — answer rendered immediately below the prompt, separated by a dashed rule. Use when peeking is fine (e.g. the answer is short and the reader is quickly self-checking).
- **flipped-answer** — answer rotated 180° (the puzzle-book convention). The reader has to physically turn the book to read it, so they're forced to attempt the exercise first. Use for reinforcement exercises where commitment matters.

## Default labels

| Field | EN | AR |
|---|---|---|
| `heading` | `Try it yourself` | `جرّب بنفسك` |
| `hint.label` | `Hint` | `تلميح` |
| `answer_label` | `Answer` | `الإجابة` |

## Bilingual notes

- The icon character flips: Latin `?` becomes the Arabic question mark `؟` (U+061F) which is the correct logical-directional glyph.
- Border accent (`border-left` LTR / `border-right` AR) flips so the accent always sits on the logical-leading edge.
- In AR, headings drop the EN-specific letter-spacing + uppercase. Hint label loses its uppercase + letter-spacing too.
- Italic prompt styling — none used. Italic isn't a native Arabic typographic convention, so we avoid it for parity.

## Visual semantics

- Block sits in `callout-tip-bg` with an accent leading-rule so the eye recognises it as an interactive beat (same shape as other tutorial callouts).
- The `?` icon in an accent-coloured circle is the consistent "this is a question" cue across languages.
- The dashed rule between prompt and answer signals that what follows is a peek-protected zone (especially in `flipped-answer`).
- In `flipped-answer`, the rotation is purely cosmetic for sighted readers — screen readers still announce the answer in normal order, which is correct for accessibility (a quiz should be *visually* hidden, not semantically hidden).

## Pedagogy

Sources: O'Reilly's "Try It Out" sidebars, Microsoft Learn's knowledge-check blocks, classic puzzle-book solution-key conventions, Cathy Moore's action-mapping practice activities. The print analogue to a digital quiz is a forcing function that's mechanical rather than adaptive: the reader must commit before the answer becomes legible. Embodies Mayer's generative-activity principle (active retrieval improves retention).

## Constraints

- The `flipped-answer` variant uses CSS `transform: rotate(180deg)`. WeasyPrint supports this in the print pipeline. The PDF will show inverted text — both for selection (text remains selectable, just visually inverted) and for screen readers (which read the underlying text in normal order).
- Keep the answer concise (1-3 sentences). Long worked-solutions read poorly upside-down even by puzzle-book standards.

## Companion components

- `tutorial-step` — the procedure that the exercise tests
- `checkpoint` — the alternative pattern when you want a verification cue without an explicit Q+A
- `glossary-card` — the alternative pattern when the gap is conceptual (vocabulary), not procedural

Part of the Tutorial Component Pack — Sprint 3 / Phase C.
