# gcc-sector-heatmap

**Tier:** section · **Namespace:** katib

## Purpose

Finding × sector relevance heatmap. Each cell carries a relevance label (`HIGH` / `MED` / `LOW`) that tints the cell from amber (high) through warm-cream (medium) to pale-peach (low). Sector columns are configurable; default is GCC-tuned (Banking, Government, Real Estate, Energy, SME / SMB).

Used as Figure 3 in Signal Forge peer briefings on richer-volume days.

## Variants

- default

## Inputs

| Field | Required | Type | Notes |
|---|---|---|---|
| `eyebrow` | optional | string | Small uppercase label above the table |
| `title` | optional | string | Heading rendered above the eyebrow |
| `sectors` | optional | array of strings | Column headers. Defaults to GCC sectors |
| `rows` | **required** | array | One row per finding |
| `caption` | optional | string | Italic note rendered below the table |

### Row shape

```yaml
- label: "Protocol war resolved"
  cells: [HIGH, MED, HIGH, LOW, MED]    # one per sector column
```

Cell values are case-insensitive; `HIGH`, `High`, and `high` all work. `MED` and `MEDIUM` are equivalent. Anything not matching `HIGH`/`MED`/`MEDIUM` falls through to the LOW colour band.

## Usage example

```yaml
- component: gcc-sector-heatmap
  inputs:
    eyebrow: "Figure 3 · GCC sector relevance · finding × sector"
    rows:
      - label: "Protocol war resolved"
        cells: [HIGH, MED, HIGH, LOW, MED]
      - label: "Claude Code · team-productivity"
        cells: [HIGH, HIGH, MED, MED, HIGH]
      - label: "GCC dual-track (enterprise vs SMB)"
        cells: [HIGH, HIGH, MED, HIGH, HIGH]
      - label: "Agent memory architecture"
        cells: [HIGH, HIGH, LOW, HIGH, LOW]
      - label: "Non-tech monetisation · Arabic gap"
        cells: [LOW, LOW, LOW, LOW, HIGH]
    caption: "Banking and Government carry the most HIGH cells. SME/SMB pulls HIGH on three of five findings."
```

## Sector overrides

For non-GCC use cases, pass your own `sectors` array:

```yaml
- component: gcc-sector-heatmap
  inputs:
    sectors: [Healthcare, Logistics, Retail, FinTech]
    rows:
      - label: "AI agents in customer service"
        cells: [HIGH, HIGH, HIGH, MED]
```

## Layout contract

- Standard HTML table; column widths auto-distribute
- Cell tints: HIGH `#F59E0B` (amber on white), MED `#FCD34D` (warm yellow on dark text), LOW `#FED7AA` (pale peach on dark text)
- Inline-block tag chips inside each cell for consistent width
- Table is wrapped in `figure` + `figcaption` for caption pairing

## Accessibility notes

- Root carries `lang` and `dir` attributes
- Real `<table>` semantics (no faux-grid div soup) so screen readers and PDF tagged-table readers work
- Caption tied to table via the `figure` wrapper
- Cell labels are inside the cell text, not relied on for colour-only meaning

## Why this exists

The first three Signal Forge peer briefs hand-rolled this table inline three times with subtly different cell paddings, font sizes, and colour values. Promoting to a component locks the visual identity and reduces the per-recipe surface area of the figure to just `{rows, sectors}`.
