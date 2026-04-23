# signature-block

Signed-by / date / name block for formal documents, contracts, and letters.

## Variants

| Variant | Look |
|---|---|
| `line-over` (default) | Horizontal rule above the block — the signer signs above it |
| `label-prefix` | Small "SIGNED" / "التوقيع" label instead of the rule |

## Inputs

| Name | Type | Required | Default |
|---|---|---|---|
| `name` | string | yes | — |
| `title` | string | no | — |
| `date` | string | no | — |
| `label` | string | no | `Signed` (EN) · `التوقيع` (AR) |

## Usage

```yaml
- component: signature-block
  variant: line-over
  inputs:
    name: "Jasem Al Neaimi"
    title: "Founder"
    date: "2026-05-01"
```

## Notes

- Block is capped at 260pt wide so it reads as a signing slot, not a paragraph.
- Declares `break_inside: avoid` — signature block never splits across pages.
- Bilingual signature pages (side-by-side EN + AR witness slots) are a Tier 2 `signature-block-bilingual` section — authored later in Phase 2+.
