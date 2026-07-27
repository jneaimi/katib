# code-step

## Purpose

The verification unit for software tutorials. A code block paired with optional per-line annotations and an optional "expected output" panel. Lets the reader confirm they're on the right track without actually running the code — Mayer's spatial-contiguity principle made physical.

## When to use

- Every code-bearing step in a software walkthrough
- Config snippets that need explanation alongside the values
- Install/setup sequences where each command needs context
- Anywhere a `code-block` primitive isn't carrying enough context to stand alone

## Inputs

```yaml
- component: code-step
  variant: terminal   # terminal (dark, default) | editor (light, filename-window look)
  inputs:
    label: "stripe-server.ts"
    language: "typescript"
    code: |
      import { Stripe } from "stripe";
      const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
      app.post("/webhook", async (req, res) => {
        const sig = req.headers["stripe-signature"];
        // ...
      });
    annotations:
      - line: 1
        note: "Official Stripe Node SDK."
      - line: 2
        note: "Initialise once at module load."
      - line: 4
        note: "The signature header proves authenticity."
    output: |
      ✓ Server listening on :4242
      ✓ Webhook handler registered
    output_label: "Expected output"
```

## Variants

- **terminal** (default) — code panel uses the theme's `code_bg` (typically dark) for that "I'm running a terminal" feel. Best for shell commands and any code that the reader will paste into a terminal.
- **editor** — code panel uses page background + border, like an editor filename window. Best for source files where the editor metaphor reads more naturally.

In both variants, the **output** panel is always terminal-styled — output IS terminal output, regardless of where the code "lives."

## Default labels

| Field | EN | AR |
|---|---|---|
| `output_label` | `Expected output` | `المخرجات المتوقعة` |
| Annotations heading | `Notes` | `ملاحظات` |

## Bilingual notes

- The `<pre>` blocks force `direction: ltr` even inside AR pages — code is universally LTR.
- The annotations block flips its leading 2.5pt accent rule to the right edge in AR.
- Annotations themselves can be written in AR; the line markers stay numeric/LTR but render correctly within the RTL flow.

## Pedagogy

Source pattern: Stripe Docs code blocks with inline comments and `<<YOUR_SECRET_KEY>>` placeholders; Apple SwiftUI tutorials' source + canvas preview pairing; O'Reilly/Manning convention of "running the example" panels. The "expected output" panel is the static-PDF analogue of an interactive REPL — it gives the reader a verification target without an interactive sandbox.

## Constraints

- `code` accepts raw HTML (Jinja `| safe`) so callers can embed `<span class="katib-code-step__highlight">…</span>` for inline emphasis. This matches the existing `code-block` primitive's contract.
- Lines are NOT auto-numbered. If you want numbered lines, embed them in the `code` string yourself or reference logical names ("the import line", "the constructEvent call") in `annotations[].line`.
- For multi-line annotations, use ranges like `5-8` or `import block` in the `line` field — it's a free-form short string, not just an integer.

## Companion components

- `tutorial-step` — for non-code steps (procedural instructions with optional screenshots)
- `checkpoint` — sits after a group of code-steps to verify the cumulative state
- `common-mistakes` (also Sprint 2) — for the failures that the most common pitfalls produce

Part of the Tutorial Component Pack — Sprint 2 / Phase B.
