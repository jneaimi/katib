# callout

**Tier:** primitive

## Purpose

Boxed message with a left accent border and a tinted background. Two categories of use:

1. **Status callouts** (`info | warn | danger | tip`) — conventional UX patterns for advisory messages within body prose.
2. **Neutral highlights** (`neutral`) — non-status emphasized boxes like cover-letter subject lines, mou non-binding notices, or inline callout paragraphs where a colored status would be semantically wrong.

## Tones

| Tone | Background | Border + title color | Use for |
|---|---|---|---|
| `info` | `callout_info_bg` (pale blue) | `callout_info_accent` | informational asides, context notes |
| `warn` | `callout_warn_bg` (pale amber) | `callout_warn_accent` | cautions, prerequisites |
| `danger` | `callout_danger_bg` (pale red) | `callout_danger_accent` | hazards, destructive actions |
| `tip` | `callout_tip_bg` (pale green) | `callout_tip_accent` | best practices, rules of thumb |
| `neutral` (0.2.0) | `tag_bg` (neutral) | `accent` | subject lines, legal non-binding notices, other non-status highlights |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `tone` | string | yes | `info`, `warn`, `danger`, `tip`, or `neutral` |
| `title` | string | no | Optional bolded first line |
| `body` | string | yes | Plain text or minimal inline HTML (auto-escaped) |

## Usage Example

Status callout:

```yaml
- component: callout
  inputs:
    tone: warn
    title: "Heads up"
    body: "This section assumes you've already completed the setup."
```

Neutral highlight (subject line in a cover letter):

```yaml
- component: callout
  inputs:
    tone: neutral
    body: "Application for Senior AI Engineer"
```

## Page behaviour

- `break_inside: avoid` — callouts never split across pages
- Uses `border-inline-start` so the accent bar automatically lands on the left (LTR) or right (RTL) edge

## Accessibility Notes

- Rendered as `<aside role="note">` — screen readers announce as a supplementary note
- Title and body are plain text; embedded HTML is auto-escaped
- Root element carries `lang` / `dir` attributes
