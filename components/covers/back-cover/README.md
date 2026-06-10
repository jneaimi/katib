# back-cover

## Purpose

The closing / contact page — the back-matter counterpart to `cover-page`. It
carries the brand logo, a closing statement (eyebrow + title + message), a
labelled contact block, and a footer strip. Use it to end a company profile,
proposal, or report on a deliberate call-to-action instead of letting the
document trail off.

## Variants

| Variant | When to use |
|---|---|
| `minimalist-typographic` | CSS-only — clean type on the page background. The default. |
| `image-background` | Full-bleed photo with a dark scrim and light text. Needs an `image`. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | `string` | no | Kicker above the title (e.g. "Get in touch"). |
| `title` | `string` | no | Closing headline. |
| `message` | `string` | no | One short closing paragraph. |
| `contacts` | `array` | no | Labelled rows: each `{label, value}`. |
| `reference_code` | `string` | no | Monospace footer code. |
| `image` | `image` | no | Background for the `image-background` variant. |

The brand `logo.primary` and `identity.author_name` flow in from the active
brand profile, mirroring `cover-page`.

## Example usage

```yaml
- component: back-cover
  variant: minimalist-typographic
  inputs:
    eyebrow: "Get in touch"
    title: "Let's build what's next."
    message: "Tell us where you're headed and we'll show you the shortest credible path."
    contacts:
      - { label: "Email", value: "hello@acme.com" }
      - { label: "Phone", value: "+971 4 000 0000" }
      - { label: "Web", value: "acme.com" }
    reference_code: "PROFILE-2026"
```

## Notes

- `mode: atomic` + `break_before: always` — the page is never split and always
  begins on a fresh sheet, so it reads as a true back cover.
- The `image-background` variant pulls out of the page margin to bleed to the
  sheet edge and overlays a dark scrim; all text turns light over the image.
- RTL: uppercase / letter-spacing is dropped from the eyebrow and contact
  labels, and the title uses a looser line-height.
