# eyebrow

Small preheader label above a title or section heading.

## Purpose

A one-line noun phrase that classifies what follows (e.g., `CHAPTER 3`, `CASE STUDY`, `ملخص`). Draws the eye to the heading without competing with it.

## Variants

| Variant | Color | When |
|---|---|---|
| `muted` (default) | `--text-tertiary` | Default — neutral, understated |
| `accent` | `--accent` | Highlight important sections |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `text` | string | yes | Short noun phrase. Rendered uppercase in EN, natural case in AR. |

## Usage

```yaml
- component: eyebrow
  variant: accent
  inputs:
    text: "Case study"
```

## Accessibility

- Inherits the page's `lang` attribute via the root; also sets `lang` on the element for screen readers switching between EN and AR paragraphs.
- No interactive affordance. Not announced as a heading (intentional — it classifies the following heading).

## Languages

- `en.html` — uppercase + letter-spacing
- `ar.html` — natural case, mild letter-spacing only (Arabic doesn't benefit from letter-spacing the way Latin does)
