# section-divider-page

## Purpose

"Part II" style divider — a full page that marks a major section
boundary in a long document. Large part number + title + optional
subtitle, centered typography. Use between acts in a white-paper,
chapters in a report, or phases in a proposal. Atomic: always on its
own page, with page breaks before and after.

## Variants

| Variant | When to use |
|---|---|
| `numeric` | Default — big part number + horizontal rule + title. |
| `minimal` | No part number — just an oversized title + subtitle. Use for one-word chapter headings or when numbering doesn't apply. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `part_number` | string | no | "II", "02", "PART TWO" — rendered very large. Only used by `numeric` variant. |
| `eyebrow` | string | no | Small uppercase label above the part number (e.g. "SECTION"). |
| `title` | string | **yes** | The section title. |
| `subtitle` | string | no | Secondary line under the title. |
| `overview` | string | no | Short orientation paragraph — what's in this part. |

## Example

```yaml
- component: section-divider-page
  variant: numeric
  inputs:
    eyebrow: "PART"
    part_number: "II"
    title: "Implementation"
    subtitle: "How the system is actually built."
    overview: |
      The next five chapters walk through the component library, the
      graduation gate, the audit trail, and the render pipeline.
```

## Notes

- Uses the default portrait `@page` — atomic page breaks come from
  `page_behavior`, not a named page rule.
- Content is vertically and horizontally centered on the page.
- `minimal` variant for cases where a number block would be awkward
  (e.g. "Foreword", "Afterword").
