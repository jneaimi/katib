# step-circle

Numbered circle marker used in step-by-step procedures.

## Variants

| Variant | Look |
|---|---|
| `solid` (default) | Filled circle using `--step-circle-bg`/`--step-circle-fg` |
| `outline` | Transparent circle with 1.5pt accent border |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `number` | int | yes | 1-based step number |
| `label` | string | no | Short description beside the circle |

## Usage

```yaml
- component: step-circle
  inputs:
    number: 1
    label: "Install the tool"
```

## Notes

- Digits are Western (1, 2, 3) in both EN and AR variants by convention. If a brand requires Eastern Arabic numerals (١, ٢, ٣), pre-convert the `number` input at the recipe level.
- The flex container auto-flips direction under RTL, so the circle stays on the leading edge (left in EN, right in AR).
