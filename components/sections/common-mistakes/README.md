# common-mistakes

## Purpose

Structured **symptom → cause → fix** triple for tutorial troubleshooting. Each row is a complete failure mode: what the reader will see when it goes wrong, why it happens, and the exact step to recover. Pre-empts the most likely failures before they cascade — embodies the worked-example pedagogy that troubleshooting research consistently endorses.

## When to use

- After a complex code-step in a software walkthrough (the next-step-where-things-can-go-wrong)
- After every cooking step that has a failure mode you've seen before
- After every assembly step where there's a wrong way that produces a diagnosable wrong outcome
- As the body of a `tutorial-troubleshooting-runbook` recipe (multiple `common-mistakes` blocks chained)

## Inputs

```yaml
- component: common-mistakes
  variant: cards   # cards (default) | table
  inputs:
    heading: "Common mistakes"   # optional — defaults per-language
    items:
      - symptom: "401 Unauthorized when the webhook fires"
        cause: "STRIPE_WEBHOOK_SECRET in your .env doesn't match the one Stripe is signing with."
        fix: "Re-copy the secret from Stripe Dashboard → Developers → Webhooks → Signing secret."
        screenshot:
          source: user-file
          path: /abs/path/to/error-screenshot.png
      - symptom: "Hangs forever on stripe-cli listen"
        cause: "stripe-cli is logged into the wrong account."
        fix: "Run `stripe login` and check the printed account matches your dashboard."
```

## Variants

- **cards** (default) — each item is a stacked 3-row panel (symptom on top, cause middle, fix bottom). Best for items with longer prose or screenshots.
- **table** — each item collapses into a 3-column row. Best for terse items (one line each) when you have 5+ of them and want a scannable lookup table.

## Default labels

| Field | EN | AR |
|---|---|---|
| `heading` | `Common mistakes` | `أخطاء شائعة` |
| Symptom row | `IF YOU SEE` | `إذا رأيت` |
| Cause row | `CAUSE` | `السبب` |
| Fix row | `FIX` | `الحل` |

## Visual semantics

- Symptom uses **monospace font** + a soft warning-tinted background — it's meant to look like the literal error message the reader will read off their screen.
- Symptom row is **danger-red** accented; fix row is **success-green** accented; cause row is neutral. The colour-coding is consistent with editor "diagnostics" UI conventions.
- Cards have a dashed top border above the fix row, separating "what's wrong" from "what to do" inside each card.

## Bilingual notes

- AR symptom text keeps `direction: rtl` even though it's wrapped in monospace — error messages in modern dev tooling are typically Latin, but Arabic error messages exist and we honour them.
- AR labels are left in their natural ("not-uppercased") rendering, since Arabic doesn't shape well in tracked uppercase.

## Distinction from `callout warn`

| Feature | `common-mistakes` | `callout warn` |
|---|---|---|
| Number of failures | Multiple, structured | One, prose |
| Structure | Symptom + cause + fix triple per row | Single text block |
| Use case | "Here are the 3 ways this typically breaks" | "Be careful, X has a gotcha" |
| Length | Tens of items possible | Sentences |

If your warning is a single flag-this-one-thing, use `callout warn`. If it's a structured catalog of failures the reader can match against, use this.

## Pedagogy

Source pattern: standard developer troubleshooting docs across the web (Stripe, Vercel, Supabase, Next.js); IKEA's "if your part looks like X, you have it backwards" insets; Microsoft Learn's troubleshooting blocks. The structure mirrors how senior engineers describe debugging to junior ones: "what do you see → that means → here's the move." Action-mapping made physical.

## Companion components

- `callout` (existing primitive) — for single inline warnings ("be careful, X")
- `code-step` — pairs naturally above this block (the success path) followed by the failure modes
- `decision-branch` (Sprint 3) — for "if you see X, go to step Y" branching beyond the symptom-cause-fix structure

Part of the Tutorial Component Pack — Sprint 2 / Phase B.
