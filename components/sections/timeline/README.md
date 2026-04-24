# timeline

**Tier:** section

## Purpose

Vertical event list with a connecting rail. Each event renders as a
dated row with a title and optional descriptive body. Events carry a
status (`done`, `active`, `upcoming`) that tints the rail node. Flips
the rail to the right side for RTL so the reading flow (date → title)
matches Arabic direction.

## Variants

| Variant | When to use |
|---|---|
| `default` | Standard density — room to breathe, for main-flow reading. |
| `compact` | Denser rail, smaller typography. For dashboards, dense reports. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Uppercase label above the timeline (e.g. "ROADMAP"). |
| `title` | string | no | Optional heading above the event list. |
| `events` | array | **yes** | Each entry `{date, title, body, status}`. `status` accepts `done` / `active` / `upcoming`. |

## Usage Example

```yaml
- component: timeline
  variant: default
  inputs:
    eyebrow: "PROGRESS"
    title: "2026 delivery schedule"
    events:
      - date: "Jan"
        title: "Phase 0 — archive + ADRs"
        body: "v1 frozen under v1-reference/. Five ADRs signed off."
        status: done
      - date: "Feb-Mar"
        title: "Phase 1 — core engine"
        body: "Composer, renderer, token system, first 8 primitives."
        status: done
      - date: "Apr"
        title: "Phase 2 — sections + first recipe"
        status: done
      - date: "Apr-May"
        title: "Phase 3 — layout + builder"
        body: "Page-layout primitives + AI-assisted component builder."
        status: active
      - date: "May-Jun"
        title: "Phase 4 — sharing + import/export"
        status: upcoming
```

## Accessibility Notes

- Status is encoded by both color and node shape variation (filled,
  ringed, outlined) — color alone doesn't carry the semantic.
- Root element carries `lang` / `dir` attributes; AR flips the rail
  side from left-edge to right-edge.
- `page-break-inside: avoid` on each event keeps event rows atomic.
