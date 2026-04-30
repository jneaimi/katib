# risk-matrix

Likelihood × impact heatmap with risk items pinned into cells.

## When to use

- SOWs and project plans
- Audit and compliance reports
- Project risk register summaries
- Any risk-conversation document where a single-page visual carries the message

## Inputs

| Field | Required | Description |
|---|---|---|
| `eyebrow` | no | Small uppercase label above the matrix. |
| `title` | no | Optional heading. |
| `size` | no | `"3x3"` (default) or `"4x4"`. |
| `likelihood_labels` | no | Override likelihood (Y axis) labels — array length must match size. |
| `impact_labels` | no | Override impact (X axis) labels — array length must match size. |
| `items` | yes | Array of `{id, label, likelihood, impact}` to plot. `likelihood` and `impact` are 1-indexed integers within the matrix size. |

## Default labels

**3×3** — Likelihood: Low / Medium / High · Impact: Low / Medium / High
**4×4** — Likelihood: Rare / Unlikely / Likely / Almost Certain · Impact: Minor / Moderate / Major / Severe

## Cell tones

Cell colour follows total severity (likelihood + impact):
- low (sum ≤ size+1) → green (success tone)
- medium (size+1 < sum ≤ 2·size−1) → amber (warn tone)
- high (sum ≥ 2·size) → red (danger tone)

## Example

```yaml
- component: risk-matrix
  inputs:
    eyebrow: "TOP RISKS"
    title: "Project risk register"
    size: "3x3"
    items:
      - {id: "R1", label: "Vendor delay (long-lead hardware)", likelihood: 3, impact: 3}
      - {id: "R2", label: "Key-person availability", likelihood: 2, impact: 3}
      - {id: "R3", label: "Currency fluctuation", likelihood: 2, impact: 2}
      - {id: "R4", label: "Minor scope creep", likelihood: 3, impact: 1}
      - {id: "R5", label: "Cyber incident on staging", likelihood: 1, impact: 2}
```
