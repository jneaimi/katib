# metric-block

**Tier:** primitive

## Purpose

Key-metric display — label + value + optional delta arrow. Use for
dashboards, executive-summary rows, KPI tables, and report hero bands.
Renders inline-block so multiple metrics flow side-by-side.

## Variants

| Variant | When to use |
|---|---|
| `stacked` | Default — vertical label / value / note. Good for dashboards and report covers. |
| `inline` | Label and value on one line, compact. Good for dense tabular contexts. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `label` | string | **yes** | Metric name (e.g. "Revenue", "الإيرادات"). |
| `value` | string | **yes** | Headline number or short phrase. String, not float — recipe controls formatting. |
| `unit` | string | no | Unit suffix rendered beside the value (e.g. "AED", "%"). |
| `delta` | string | no | Change figure (e.g. "+18%", "-2.4pp"). Tinted by `delta_direction`. |
| `delta_direction` | string | no | `up` (accent tint), `down` (danger tint), `neutral` (warn tint, default). |
| `note` | string | no | Short context line below the value. |

## Usage Example

```yaml
sections:
  - component: module
    inputs:
      raw_body: |
        <div>
          <!-- Each metric-block renders inline — side-by-side layout. -->
          {% from 'primitives/metric-block/en.html' import metric %}
        </div>

  # In practice, embed metric-blocks inside a host section via raw_body:
  - component: module
    inputs:
      title: "2025 H1 Snapshot"
      raw_body: |
        <div style="margin-top: 8pt;">
          <div class="katib-metric-block katib-metric-block--stacked">...</div>
          <div class="katib-metric-block katib-metric-block--stacked">...</div>
        </div>
```

A cleaner pattern is to reference `metric-block` directly in recipe
`sections:` — each invocation produces one metric, and the primitive's
`display: inline-block` lays them out side-by-side naturally:

```yaml
- component: metric-block
  inputs:
    label: "Revenue"
    value: "3.1"
    unit: "M AED"
    delta: "+18%"
    delta_direction: up
    note: "vs. 2025 H1"

- component: metric-block
  inputs:
    label: "Active users"
    value: "94"
    unit: "K"
    delta: "+6%"
    delta_direction: up
```

## Accessibility Notes

- Root element carries `lang` / `dir` attributes — Arabic renders RTL
  with larger glyph sizes and no letter-spacing (which breaks Arabic
  shaping).
- Color alone doesn't carry the delta direction — the `+` / `-` sign
  in the value string is the accessible primary signal.
