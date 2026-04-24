# executive-summary

**Tier:** section

## Purpose

Key takeaways box for the top of reports, proposals, and white-papers.
Eyebrow + title + optional intro + 2-5 labeled bullet rows + optional
footer. Sets reader expectations before the body. Rendered with a
left-accent rail (flipped to right for RTL) for visual separation from
regular document flow.

## Variants

| Variant | When to use |
|---|---|
| `default` | Minimal chrome — just the left-accent rail. Good for white-papers and memos. |
| `bordered` | Full border + left-accent rail. Good for executive dashboards and cover-adjacent summaries. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Small uppercase label above the title (e.g. "EXECUTIVE SUMMARY"). |
| `title` | string | **yes** | Summary heading. |
| `intro` | string | no | Single paragraph above the bullet rows. |
| `items` | array | **yes** | List of `{label, body}` objects. Expected 2-5. |
| `footer` | string | no | Call-to-action or closing line, rendered muted+italic. |

## Usage Example

```yaml
- component: executive-summary
  variant: default
  inputs:
    eyebrow: "EXECUTIVE SUMMARY"
    title: "The bottom line"
    intro: |
      Katib v2 separates templates from content entirely. Components
      are the atomic unit of reuse; doc-types become YAML recipes.
    items:
      - label: "Problem"
        body: "Hardcoded sample content corrupted skill updates on reinstall."
      - label: "Fix"
        body: "Two-tier content layout with shadow semantics."
      - label: "Impact"
        body: "Users extend the library without touching the skill dir."
    footer: "See Section II for the technical design."
```

## Accessibility Notes

- Root element carries `lang` / `dir` attributes.
- RTL variant flips the accent rail to the right edge and adjusts the
  label separator direction.
- `page-break-inside: avoid` on each item keeps bullet rows atomic
  across page breaks.
