# multi-party-signature-block

**Tier:** section

## Purpose

Multi-party signature grid for formal documents — NOC certificates, MOUs, contracts, and similar documents where two or more named parties sign side-by-side. Each party renders as a "signing box" with name + optional title + optional email, with an optional top border acting as the signing line.

**Distinct from `signature-block`:** `signature-block` is a primitive for a single signatory (or a single addressee via `recipient` variant). `multi-party-signature-block` is a section-tier component that lays out N parties in a responsive grid.

## Variants

| Variant | Look |
|---|---|
| `line-over` (default) | Top border on each party box — the signing line |
| `minimal` | No borders, just spacing — for documents where signatures don't need a visible line |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `parties` | array | yes | List of `{name, title?, email?}` mappings |
| `heading` | string | no | Optional heading above the grid (e.g., "Signed by the undersigned") |

Each party object:

| Field | Type | Required |
|---|---|---|
| `name` | string | yes |
| `title` | string | no |
| `email` | string | no |

## Usage Example

Two-party NOC signature:

```yaml
- component: multi-party-signature-block
  inputs:
    parties:
      - name: "Jasem Al Neaimi"
        title: "HR Manager"
        email: "hr@jasem-katib.example"
      - name: "Authorised signatory"
        title: "Signature & company stamp"
```

Three-party MOU signature (minimal variant, no signing lines):

```yaml
- component: multi-party-signature-block
  variant: minimal
  inputs:
    heading: "Signed by the Parties"
    parties:
      - name: "Party A"
        title: "First Party representative"
      - name: "Party B"
        title: "Second Party representative"
      - name: "Witness"
        title: "Legal counsel"
```

## Accessibility Notes

- Semantic `<section>` wrapper with `lang`/`dir` attributes
- Email field forced `dir="ltr"` inside Arabic templates (addresses are structurally LTR)
- Grid uses `repeat(auto-fit, minmax(200pt, 1fr))` — auto-flows 2-N parties across the page width
- `page-break-inside: avoid` — signature block stays together across pages
- All colors resolve via tokens (`--text`, `--text-secondary`, `--text-tertiary`) — zero hex in stylesheet

## When NOT to use

- **Single signatory** (letters, memos) — use `signature-block` primitive
- **Addressee at top of letter** — use `signature-block` with `recipient` variant
- **Witness-only attestation without principal parties** — still use this component with 1 party and `minimal` variant, or consider a dedicated witness component
