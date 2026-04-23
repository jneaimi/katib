# masthead-personal

**Tier:** section

## Purpose

Personal-identity masthead for personal-brand documents — cover letters, CVs, bio sheets. Renders the author's **name + tagline** on the leading side and a **contact stack** (email, phone, location) on the trailing side, separated by a bottom accent rule.

**Distinct from `letterhead`:** use `letterhead` for organizational identity (company + reference + date — business letters, NOCs, invoices). Use `masthead-personal` when the document represents a person (cover letter, CV, bio).

## Variants

None. Use `letterhead` if you need variant styling — different tone, different role, different component.

## Inputs

| Name | Type | Required | Purpose |
|---|---|---|---|
| `name` | string | yes | Full name; rendered large + accent |
| `tagline` | string | no | Professional headline (e.g., "Senior AI Engineer") |
| `email` | string | no | Email — falls back to `brand.identity.email` if unset |
| `phone` | string | no | Phone — falls back to `brand.identity.phone` if unset |
| `location` | string | no | City / country line (e.g., "Dubai, UAE") |

All fields except `name` are optional. Missing contact fields simply don't render (no placeholder, no empty lines).

## Usage Example

With brand identity fallback:

```yaml
# Assumes active brand profile has identity.email + identity.phone set.
- component: masthead-personal
  inputs:
    name: "Jasem Al Neaimi"
    tagline: "Senior AI Engineer"
    location: "Dubai, UAE"
```

Explicit contact (no brand fallback):

```yaml
- component: masthead-personal
  inputs:
    name: "Jasem Al Neaimi"
    tagline: "Senior AI Engineer"
    email: "jasem@example.com"
    phone: "+971 50 000 0000"
    location: "Dubai, UAE"
```

## Accessibility Notes

- Semantic `<section>` wrapper; bar is a `<div>` (no `<header>` because this is a document-level identity block, not a section nav)
- Root element carries `lang` / `dir`; RTL flips flex direction so identity stays on the visual start
- `email` + `phone` are forced `dir="ltr"` in Arabic templates (addresses + numbers are LTR inside RTL documents)
- All colors resolve via tokens (`--accent`, `--text-secondary`, `--text-tertiary`)

## Brand fields

- `identity.email` → default for `email` input when the recipe doesn't supply it
- `identity.phone` → default for `phone` input when the recipe doesn't supply it

## When NOT to use

- **Business letters / NOCs / invoices** — use `letterhead` (organizational identity)
- **Title pages / full cover** — use `front-matter` or `cover-page`
- **Repeating body sections** — use `module`
