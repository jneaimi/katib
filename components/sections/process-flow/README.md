# process-flow

Numbered step-by-step flow diagram. Renders 3–6 connected nodes — each with a number, label, and optional one-line description — as a horizontal row or vertical column.

## When to use

- "How it works" sections in marketing or proposals
- Onboarding flows
- Process documentation where the order matters
- Anywhere you'd otherwise reach for "Step 1, Step 2, Step 3" prose

Distinct from:
- `feature-row` — parallel ideas, no inherent order, no connectors
- `timeline` — date-anchored events, not abstract steps
- `tutorial-step` — single step with rich inline content (use multiple of these for long-form tutorials)

## Inputs

| Field | Required | Description |
|---|---|---|
| `eyebrow` | no | Small uppercase label above the section heading. |
| `title` | no | Optional section heading. |
| `orientation` | no | `"horizontal"` (default) or `"vertical"`. |
| `steps` | yes | Array of `{label, body?}`. 3–6 for horizontal; up to 8 for vertical. |

## Per-step fields

- **`label`** — bold one-line title for the step
- **`body`** — optional one-sentence description

## Example

```yaml
- component: process-flow
  inputs:
    eyebrow: "HOW IT WORKS"
    title: "Three steps to a print-grade PDF"
    orientation: horizontal
    steps:
      - label: "Author"
        body: "Write your content in markdown — bilingual EN+AR side by side."
      - label: "Compose"
        body: "Pick a template, fill in the recipe, drop in components."
      - label: "Render"
        body: "WeasyPrint produces an A4 PDF with proper page breaks."
```

## Notes

- Numbers are auto-generated from the array index — you don't pass them.
- The connector line between nodes flips automatically for RTL.
- Page mode is `flowing-protect-items` — individual steps won't split across pages, but the whole flow can break between steps if needed.
