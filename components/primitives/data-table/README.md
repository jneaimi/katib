# data-table

**Tier:** primitive

## Purpose

Accessible tabular data — headers, rows, per-column alignment, alt-row backgrounds. Serves:

- White-paper — numeric time-series (Indicator × years)
- Proposal — deliverables tables (# + Module + Focus + Outcome)
- Invoice — line-items with description sub-text (# + Desc + Qty + rates + totals)
- Onboarding — 30/60/90 text-only windows

## Variants

- `default` — alt-row backgrounds (zebra striping via `tag_bg`)
- `bordered` — every cell gets a border; no alt rows
- `dense` — tighter padding + smaller font for high-column-count tables (invoice line items)

## Inputs

- `caption` (string, optional) — screen-reader-friendly label above the table
- `columns` (array, required) — column descriptors:
  - `label` (string, required) — header text
  - `align` (string, optional) — `"num"` for right-aligned tabular-nums columns
  - `width` (string, optional) — CSS width hint (e.g. `"50pt"`)
- `rows` (array, required) — array of row arrays:
  - Each cell is either a **string** (simple) OR a **mapping** `{text, sub?}` (text + optional muted sub-line for invoice description cells)

## Usage Examples

### White-paper — 5-col numeric time-series

```yaml
- component: data-table
  inputs:
    caption: "Indicator trends, 2020–2026"
    columns:
      - label: "Indicator"
      - label: "2020"
        align: num
      - label: "2022"
        align: num
      - label: "2024"
        align: num
      - label: "2026"
        align: num
    rows:
      - ["[Metric 1]", "1,200", "1,580", "2,100", "2,600"]
      - ["[Metric 2]", "28%", "34%", "41%", "49%"]
```

### Invoice — 7-col dense with cell sub-text

```yaml
- component: data-table
  variant: dense
  inputs:
    columns:
      - label: "#"
        align: num
        width: "24pt"
      - label: "Description"
      - label: "Qty"
        align: num
      - label: "Unit Price"
        align: num
      - label: "VAT %"
        align: num
      - label: "VAT"
        align: num
      - label: "Total (AED)"
        align: num
    rows:
      - - "1"
        - {text: "[Service / product name]", sub: "[Scope note — dates, deliverable]"}
        - "1"
        - "10,000.00"
        - "5%"
        - "500.00"
        - "10,500.00"
```

### Onboarding — 3-col text-only

```yaml
- component: data-table
  inputs:
    columns:
      - label: "Window"
      - label: "Focus"
      - label: "Signal of success"
    rows:
      - ["Days 1–30", "Learn the codebase", "Your first PR is merged"]
```

## Accessibility Notes

- `<table>` is the semantic root with `lang` / `dir` attributes
- `<thead>` + `<tbody>` properly separated
- `<th scope="col">` for column headers — screen readers announce them on each data cell
- Optional `<caption>` as the table label (preferred over a sibling `<h3>` for screen-reader clarity)

## WeasyPrint constraints

- Table cells use physical text-align (`left`/`right`) rather than logical (`start`/`end`) — WeasyPrint behavior is more predictable this way across LTR/RTL.
- `page-break-inside: auto` on the `<table>` (allows row-level splitting for long tables) but each row individually doesn't split — rely on WeasyPrint's default row atomicity.
