# reference-strip

Compact list of further-reading or source citations. Typical last section of a document, preceded by a horizontal rule separator.

## Variants

| Variant | Look |
|---|---|
| `flat` (default) | Simple bulleted list |
| `tagged` | Each item may carry an outline-tag marker (e.g. `PAPER`, `BLOG`, `SPEC`) |

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `eyebrow` | string | no | `"References"` (EN) · `"المراجع"` (AR) |
| `heading` | string | no | `"Further reading"` (EN) · `"قراءات إضافية"` (AR) |
| `items` | array | yes | — |

`items` supports two forms:
- plain strings → rendered as-is
- objects `{label, url?, note?, tag?}` → bold label + monospace URL + muted note + optional outline tag (tagged variant only)

## Usage

```yaml
- component: reference-strip
  variant: tagged
  inputs:
    heading: "Further reading"
    items:
      - label: "Katib v2 ADR"
        url: "github.com/jneaimi/katib"
        note: "Component architecture + graduation flow"
        tag: "ADR"
      - label: "shadcn/ui"
        url: "ui.shadcn.com"
        note: "Copy-in component model reference"
        tag: "WEB"
      - "Plain-string reference still works"
```

## Composes

- `.katib-rule` · `.katib-rule--hairline`
- `.katib-eyebrow` · `.katib-eyebrow--muted`
- `.katib-tag` · `.katib-tag--outline` (tagged variant)
