# signature-field-block

**Tier:** primitive  
**Version:** 0.1.0  
**Namespace:** katib  
**Languages:** EN + AR

## Purpose

Blank-field signature grid for counterparty execution. Renders N parties side
by side as columns, each column containing an uppercase eyebrow label, optional
bold party name, and an ordered list of labeled blank input lines (Name /
Title / Signature / Date). Use when a document will be printed, countersigned
by hand, and returned.

## When to use

| Component | Use case |
|-----------|----------|
| `signature-block` | **Pre-filled, single** named signatory (closing block or addressee). |
| `multi-party-signature-block` | **Pre-filled, multiple** signatories with known names + titles. |
| `signature-field-block` *(this one)* | **Blank form fields** to be filled by the counterparty in pen. Typical in MoUs, commercial quotes, service agreements. |

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `parties` | array[1–3] | yes | One column per party. |

Each party object:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `label` | string | yes | Uppercase eyebrow label above the party column. |
| `name` | string | no | Bold party name below the label. Omit for fully-blank columns. |
| `fields` | array[1–6] | yes | Ordered labeled blank input lines. Typical set: `["Name", "Title", "Signature", "Date"]`. |

## Example — bilateral MoU execution (two parties, same fields)

```yaml
- component: signature-field-block
  inputs:
    parties:
      - label: "For Party A"
        name: "jasem | katib"
        fields: ["Name", "Title", "Signature", "Date"]
      - label: "For Party B"
        name: "[Party B]"
        fields: ["Name", "Title", "Signature", "Date"]
```

## Example — commercial quote (one filled party + one blank)

```yaml
- component: signature-field-block
  inputs:
    parties:
      - label: "For jasem | katib"
        name: "Jasem Al Neaimi"
        fields: ["Signature", "Date"]
      - label: "For [Client Name]"
        fields: ["Name", "Title", "Signature", "Date"]
```

## Pagination

`page_behavior.mode: atomic` — signature grids never split across pages.
Engine emits `break-inside: avoid` on the section wrapper.

## Token contract

`text`, `text_tertiary`, `border_strong`, `font-primary`, `font-display`.

## Notes

- RTL handled by grid + lang attribute — no physical-property flips needed
  because all content inside each column is block-level.
- `fields` strings are displayed verbatim (e.g., "Name" or "Name & Title" or
  "اسم") — caller localizes.
