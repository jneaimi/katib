# summary

End-of-document recap. Heading + optional paragraph + optional bulleted takeaways, preceded by a separator rule.

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `eyebrow` | string | no | `"Wrap-up"` (EN) · `"خاتمة"` (AR) |
| `heading` | string | no | `"Summary"` (EN) · `"ملخص"` (AR) |
| `body` | string | no | — |
| `items` | array<string> | no | — |

At least one of `body` or `items` should be supplied (both are optional in the schema but an empty summary is pointless).

## Usage

```yaml
- component: summary
  inputs:
    heading: "What you should now know"
    body: "You've completed the three-module walkthrough."
    items:
      - "Environment is set up and verified"
      - "Core workflow runs end-to-end"
      - "Recovery paths for the three common failure modes"
```

## Composes

- `.katib-eyebrow` · `.katib-eyebrow--muted`
- Built-in `<h2>` styles from the page shell
