# landscape-section

## Purpose

Wraps a block of content in a landscape-oriented page. Built for wide data
tables, horizontal timelines, multi-column charts, or any content that
doesn't fit the A4 portrait content area.

## How it works

The component declares a named `@page landscape` rule (A4 landscape,
20mm margins — mirrors the base portrait margin) and opts any instance
into it via the CSS `page: landscape` property. `page_behavior` sets
`break_before: always` and `break_after: always`, so the landscape page
always stands alone in the flow — no half-landscape content spilling
off neighboring portrait pages.

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Small label above the heading. |
| `title` | string | no | Page heading. Omit for chart-only pages. |
| `intro` | string | no | One-paragraph caption under the title. |
| `raw_body` | string | **yes** | Trusted HTML — tables, charts, figures. Not escaped. |

## Example usage in a recipe

```yaml
- component: landscape-section
  inputs:
    eyebrow: "APPENDIX A"
    title: "2025 Revenue by Region"
    intro: "Fiscal year data in a wide table that wouldn't fit portrait."
    raw_body: |
      <table>
        <thead>
          <tr><th>Region</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>YoY %</th></tr>
        </thead>
        <tbody>
          <tr><td>UAE</td><td>2.1M</td><td>2.4M</td><td>2.7M</td><td>3.1M</td><td>+18%</td></tr>
        </tbody>
      </table>
```

## Notes

- Long tables split cleanly across landscape pages — rows are
  `page-break-inside: avoid` by convention (same as `data-table`
  primitive).
- Arabic variant uses `dir="rtl"` on the section root so inline tables
  and figures flip directionality correctly.
- Can appear anywhere in a recipe's `sections:` list — surrounding
  portrait content resumes after the landscape page ends.
