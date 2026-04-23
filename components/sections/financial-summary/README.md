# financial-summary

**Tier:** section

## Purpose

Totals box for invoices and quotes. Right-aligned numeric rows with labels on the leading side; one emphasized Total row with accent background. Container is flex-end positioned (70mm wide) so it naturally aligns to the trailing edge of the page.

Used by:
- `financial/invoice` — 4-row totals (Subtotal / Discount / VAT / Total)
- `financial/quote` — same shape, compact variant for slimmer quotes

## Variants

- `default` — 70mm box, standard typography
- `compact` — 60mm box, slimmer rows (for quotes or shorter totals lists)

## Inputs

- `rows` (array, required) — list of `{label, value, variant?}`:
  - `label` (string) — row label (e.g. "Subtotal (excl. VAT)")
  - `value` (string) — right-aligned numeric string (formatted, e.g. "17,000.00")
  - `variant` (optional) — `"total"` triggers the accent-bg emphasized Total row (usually the final row)
- `currency` (string, optional) — currency code shown next to the Total row label (e.g. "AED"). Displayed as `"TOTAL AED"` when the row has `variant: total`.

## Usage Example

### Invoice totals (4 rows)

```yaml
- component: financial-summary
  inputs:
    currency: "AED"
    rows:
      - {label: "Subtotal (excl. VAT)", value: "17,000.00"}
      - {label: "Discount", value: "0.00"}
      - {label: "VAT (5%)", value: "600.00"}
      - {label: "TOTAL", value: "17,600.00", variant: total}
```

### Quote totals (compact)

```yaml
- component: financial-summary
  variant: compact
  inputs:
    currency: "AED"
    rows:
      - {label: "Subtotal", value: "10,000.00"}
      - {label: "VAT (5%)", value: "500.00"}
      - {label: "TOTAL", value: "10,500.00", variant: total}
```

## Accessibility Notes

- Root `<section>` carries `lang` / `dir` attributes
- Numeric values use `font-variant-numeric: tabular-nums` for aligned monospaced digits
- Under RTL, numeric values are forced `direction: ltr` so amounts render LTR (standard Arabic-document convention for currency figures)

## WeasyPrint constraints

- Uses physical `flex` positioning with `justify-content: flex-end` — auto-flips under RTL without directional overrides.
- Explicit width (70mm default, 60mm compact) — avoids WeasyPrint's fragile width inheritance in flex containers.
