# org-chart

Two-level organisational chart. Renders a single root node connected to a row of child nodes by a clean tree of lines. Each node carries a name and an optional role.

## When to use

- Org structures (CEO + direct reports, head of department + team)
- Governance diagrams (board chair + committee chairs)
- Parent-and-children unit layouts (parent company + subsidiaries)
- Any one-to-many hierarchy that fits on one row

For deeper hierarchies (3+ levels), render multiple `org-chart` sections — one per layer — rather than trying to nest them on a single page.

## Inputs

| Field | Required | Description |
|---|---|---|
| `eyebrow` | no | Small uppercase label above the section heading. |
| `title` | no | Optional section heading. |
| `root` | yes | Top node — `{label, role?, image?}`. |
| `children` | yes | Array of `{label, role?, image?}` — 2–5 entries recommended. |

## Per-node fields

- **`label`** — name (or unit name)
- **`role`** — optional title or descriptor
- **`image`** — optional avatar / logo path (rendered as a 32pt circle)

## Example

```yaml
- component: org-chart
  inputs:
    eyebrow: "GOVERNANCE"
    title: "Project leadership"
    root:
      label: "Jasem Al-Neaimi"
      role: "Founder & Chief Architect"
    children:
      - label: "Layla Al-Mansoori"
        role: "Engineering Lead"
      - label: "Omar Faraj"
        role: "Design Lead"
      - label: "Hessa Al-Suwaidi"
        role: "Product Lead"
      - label: "Yousef Khalid"
        role: "Operations"
```

## Notes

- Page mode is `atomic` — the chart never splits across pages.
- 2–5 children is the sweet spot. Beyond that, the boxes get cramped — split into multiple charts.
