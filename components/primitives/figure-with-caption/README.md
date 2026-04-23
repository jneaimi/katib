# figure-with-caption

Image with optional caption — the core visual primitive every section builds on.

## Variants

| Variant | Look |
|---|---|
| `full-width` (default) | Image spans 100% of the content column |
| `inset` | Image constrained to 70%, centered |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `image` | image | yes | Resolved via the image-provider layer (Day 5+) |
| `alt_text` | string | yes | Accessibility alt text — read by screen readers |
| `caption` | string | no | Caption below the image in muted type |

## Image sources

Declares `sources_accepted: [user-file, url, gemini]`. Recipes pick the source per invocation; `screenshot` is deliberately excluded (screenshots belong on `tutorial-step`, not the general-purpose figure).

## Usage

```yaml
- component: figure-with-caption
  inputs:
    image:
      source: user-file
      path: "~/Downloads/diagram.png"
    alt_text: "System architecture — ingest pipeline"
    caption: "Fig 1. Data flow from producers through the event bus."
```

## Status

Authored Day 3 with the long-term `type: image` schema. Provider resolution wires up in Day 5 (`core/image/`). Phase-1-trivial recipe doesn't yet include this component — it joins the test harness once providers are online.
