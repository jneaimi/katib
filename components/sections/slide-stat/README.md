# slide-stat

Single 16:9 landscape slide carrying one massive stat with a label and an optional supporting paragraph.

## When to use

- Traction slides in pitch decks
- Market-size slides (TAM / SAM / SOM)
- "What we learned" slides between case-study sections
- Any deck slide where one number is the message

For inline stats inside a body section, use `metric-block` instead.

## Inputs

| Field | Required | Description |
|---|---|---|
| `eyebrow` | no | Small uppercase label above the stat. |
| `value` | yes | The big number (e.g. "10M+", "AED 2.4B", "47%"). |
| `unit` | no | Small unit suffix (e.g. "users", "ARR"). |
| `label` | yes | One-line descriptor under the stat. |
| `body` | no | 1–2 sentence supporting note. |
| `delta` | no | Change indicator (e.g. "+34% YoY", "↑ 12pp"). |
| `delta_tone` | no | `"success"` (default), `"warn"`, `"danger"`, `"neutral"`. |

## Example

```yaml
- component: slide-stat
  inputs:
    eyebrow: "TRACTION"
    value: "10M+"
    unit: "documents rendered"
    label: "monthly across 2,400 katib installs"
    body: "From a standing start in March 2026. 92% retained month-over-month — once a team installs katib they stop using everything else."
    delta: "+128% MoM"
    delta_tone: success
```
