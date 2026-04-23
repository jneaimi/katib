# signature-block

**Tier:** primitive

## Purpose

Named-party block for formal documents — renders either **signatories** (closing signature slots at the end of letters, MoUs, contracts) or **addressees** (recipient blocks at the start of letters, proposals, envelopes) depending on variant.

Semantically "a named party appearing in a document's context" — one primitive covers both the person who signed it and the person it's addressed to.

## Variants

| Variant | Role | Look |
|---|---|---|
| `line-over` (default) | Signatory | Horizontal rule above the block — the signer signs above it |
| `label-prefix` | Signatory | Small `SIGNED` / `التوقيع` label instead of the rule |
| `recipient` | Addressee | No top border; addressee spacing; intended for the recipient block at the top of a letter |

## Inputs

| Name | Type | Required | Default | Purpose |
|---|---|---|---|---|
| `name` | string | yes | — | Full name |
| `title` | string | no | — | Job title or role |
| `organization` | string | no | — | Company/organization (added 0.2.0) |
| `location` | string | no | — | City / country line (added 0.2.0) |
| `date` | string | no | — | Signing date (free-form) |
| `label` | string | no | `Signed` / `التوقيع` | Prefix label — not rendered for `line-over` or `recipient` |

## Usage Example

Closing signature (letter, MoU):

```yaml
- component: signature-block
  inputs:
    name: "Jasem Al Neaimi"
    title: "Managing Director · jasem | katib"
    date: "23 April 2026"
```

Recipient (letter addressee):

```yaml
- component: signature-block
  variant: recipient
  inputs:
    name: "Ms. Sara Al-Hashimi"
    title: "VP of Learning & Development"
    organization: "ACME Corp"
    location: "Dubai, United Arab Emirates"
```

## Accessibility Notes

- Block is capped at 260pt wide so it reads as a named-party slot, not a paragraph
- Declares `break_inside: avoid` — never splits across pages
- All colors resolve via tokens (`--text`, `--text-secondary`, `--border-strong`)

## Notes

- Bilingual signature pages (side-by-side EN + AR witness slots) are covered by a future Tier-2 `multi-party-signature-block` section — this primitive is single-party.
- `recipient` variant was added in 0.2.0; pre-0.2.0 code that only declares `line-over` / `label-prefix` variants remains compatible (those variants are unchanged).
