# checkpoint

## Purpose

A boxed "you should now have…" panel that sits between step groups. Lets the reader verify they're on the right track before committing more attention. Implements Mayer's segmenting principle: chunked progression beats one undifferentiated stream.

## When to use

- Every 3–4 numbered steps in a tutorial
- After every functional unit (a working webhook, a kneaded dough, an assembled subassembly)
- Before any step that requires earlier work to be correct (so failures surface here, not 5 steps later)

## Inputs

```yaml
- component: checkpoint
  variant: neutral   # neutral (default) | success
  inputs:
    title: "Webhook reachable"     # optional — defaults per-lang
    body: "You should now see a 200 OK from /webhook with event_id printed in your terminal..."
    screenshot:
      source: user-file
      path: /abs/path/to/interim-state.png
    alt_text: "Terminal output showing 200 OK"
```

## Variants

- **neutral** (default) — accent-tinted background, accent leading rule. Use for routine "are you here?" checks.
- **success** — green-tinted background, green leading rule, green check icon. Use after the most important milestone in the tutorial (the moment the thing actually works).

## Default headings

| Language | Default `title` |
|---|---|
| EN | `Checkpoint` |
| AR | `نقطة تحقق` |

Override `title` for richer context ("Webhook reachable", "Dough ready", "Engine bay clear").

## Bilingual notes

- Leading rule mirrors: EN puts the 3pt accent rule on the left; AR puts it on the right (logical-leading edge).
- AR title bumps to 12pt and removes letter-spacing — Arabic doesn't shape well at tracked sizes.

## Pedagogy

Source pattern: LEGO per-bag completion previews; Microsoft Learn per-unit summaries; cookbook "the dough should look like…" inline checks; Apple SwiftUI tutorials' "Run the app and you should see…". The point is to fail-fast at chunk boundaries instead of letting an early misstep cascade silently to the end.

## Companion components

- `tutorial-step` — what comes before each checkpoint (the steps to verify against)
- `common-mistakes` (Sprint 2) — where to send a reader if their checkpoint state is wrong
- `whats-next` — checkpoint chains naturally lead into a final whats-next at the end of the tutorial

Part of the Tutorial Component Pack — Sprint 1 / Phase A.
