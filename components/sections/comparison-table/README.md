# comparison-table

Feature × option comparison grid — features as rows, options (vendors / tiers / variants) as columns, with semantic check / cross / value cells.

## When to use

- Pricing tables (Starter / Pro / Enterprise)
- Vendor evaluations in RFP responses
- "This vs that" decision documents
- Feature comparisons across product variants

For a generic spreadsheet (no semantic comparison), use `data-table` instead.

## Inputs

| Field | Required | Description |
|---|---|---|
| `eyebrow` | no | Small uppercase label above the table. |
| `title` | no | Optional heading. |
| `options` | yes | Column headers — array of strings or `{label, sublabel?, recommended?}` mappings. |
| `rows` | yes | Array of `{feature, sub?, group?, cells}`. `cells` length must equal `options` length. |

## Cell formats

Each cell can be:

- `true` → ✓ (green check)
- `false` → ✗ (red cross)
- string or number → rendered as a value
- `{kind: 'check'}` → ✓
- `{kind: 'cross'}` → ✗
- `{kind: 'value', value: 'AED 49/mo'}` → value
- `{kind: 'note', value: 'On request'}` → small grey note

## Example

```yaml
- component: comparison-table
  inputs:
    eyebrow: "PRICING"
    title: "Choose your plan"
    options:
      - label: "Starter"
        sublabel: "For solo founders"
      - {label: "Pro", sublabel: "For small teams", recommended: true}
      - {label: "Enterprise", sublabel: "Custom"}
    rows:
      - feature: "Monthly price"
        cells: ["AED 49", "AED 199", {kind: note, value: "Quoted"}]
      - feature: "Templates"
        sub: "Marketplace + your own"
        cells: ["Up to 10", "Unlimited", "Unlimited"]
      - feature: "Bilingual rendering"
        cells: [true, true, true]
      - feature: "Custom brand profiles"
        cells: [false, true, true]
```

## Optional row grouping

Add a `group` key on a row to insert a group header above it:

```yaml
rows:
  - {group: "Core features"}
  - feature: "Templates"
    cells: ["Up to 10", "Unlimited", "Unlimited"]
  - {group: "Brand & customisation"}
  - feature: "Brand profiles"
    cells: [false, true, true]
```
