# signal-intensity-matrix

**Tier:** section · **Namespace:** katib

## Purpose

Two-column dot-grid matrix for comparing intensity scores across N findings. Each row shows N dots filled per column tier; below-threshold dots render as outlined circles. Default columns are "GLOBAL DISCOURSE" vs "GCC RESONANCE" but both labels are configurable, so the component generalises to any "two scores per row" comparison.

Used as Figure 2 in Signal Forge peer briefings.

## Variants

- default

## Inputs

| Field | Required | Type | Notes |
|---|---|---|---|
| `eyebrow` | optional | string | Small uppercase label above the matrix |
| `title` | optional | string | Heading rendered above the eyebrow |
| `column_a_label` | optional | string | Header for column A. Defaults to `"GLOBAL DISCOURSE"` |
| `column_b_label` | optional | string | Header for column B. Defaults to `"GCC RESONANCE"` |
| `max_intensity` | optional | number | Number of dots per cell. Defaults to `5` |
| `rows` | **required** | array | One row per finding |
| `caption` | optional | string | Italic note rendered below the matrix |

### Row shape

```yaml
- label: "Protocol war resolved (24h)"
  a: 5         # column A intensity (0..max_intensity)
  b: 3         # column B intensity (0..max_intensity)
```

## Usage example

```yaml
- component: signal-intensity-matrix
  inputs:
    eyebrow: "Figure 2 · Signal-intensity matrix · global discourse vs GCC resonance"
    rows:
      - { label: "Protocol war resolved (24h)", a: 5, b: 3 }
      - { label: "Claude Code as team-productivity platform", a: 5, b: 4 }
      - { label: "GCC dual-track (enterprise vs SMB)", a: 3, b: 5 }
      - { label: "Agent memory architecture", a: 4, b: 3 }
      - { label: "Non-tech monetisation · Arabic gap", a: 2, b: 3 }
    caption: "Today's GCC column carries weight, unlike yesterday's read where every row sat at zero."
```

## Layout contract

- viewBox: `0 0 600 H`, where `H = 30 + (rows × 40) + 50`
- EN: row labels left-aligned at `x=20`, column A dots centered at `x=320`, column B dots at `x=500`
- AR: row labels right-aligned at `x=580`, columns mirror to `x=280` and `x=100`
- Filled dots use the column's tier colour (column A amber `#F59E0B`, column B orange `#FB923C`)
- Below-threshold dots use a 0.6pt grey stroke, transparent fill
- Three-item legend strip at the bottom

## Accessibility notes

- Root carries `lang` and `dir` attributes
- `figure` element wraps the SVG with `role="group"` and an `aria-label`
- Dot intensities should be calibrated and explained in the figure caption — they're an editorial measure, not raw data

## Why this exists

Hand-rolled SVG dot matrices in recipe yamls drift across rows. Fill counts get miscounted when a finding moves up or down. This component computes dot positions and fills from a clean `{label, a, b}` data shape, eliminating that class of bug.
