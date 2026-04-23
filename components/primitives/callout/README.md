# callout

Boxed message with a left accent border and a tinted background.

## Tones

`info` · `warn` · `danger` · `tip`

Each tone has a matched background + accent pair in the brand's token set.

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `tone` | string | yes | — |
| `title` | string | no | — |
| `body` | string | yes | — |

## Usage

```yaml
- component: callout
  inputs:
    tone: warn
    title: "Heads up"
    body: "This section assumes you've already completed the setup."
```

## Page behaviour

- `break_inside: avoid` — callouts never split across pages.
- Uses `border-inline-start` so the accent bar automatically lands on the left (LTR) or right (RTL) edge.

## Accessibility

- Rendered as `<aside role="note">` — screen readers announce it as a supplementary note.
- Title and body are plain text; embedded HTML is auto-escaped.
