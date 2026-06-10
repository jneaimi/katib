# testimonial-card

## Purpose

Client testimonial cards — each card carries a quote, the author's name, and an
optional role / company and avatar. Renders one per row (stacked) or two-up.
Use it for social-proof sections in company profiles, proposals, and
case-study decks. Reach for `pull-quote` instead when you need a single
editorial blockquote in running text; `testimonial-card` is the repeating,
attributed, card-framed pattern.

## Variants

| Variant | When to use |
|---|---|
| `default` | The standard bordered card. Layout is driven by `columns`, not a variant. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | `string` | no | Uppercase kicker. |
| `heading` | `string` | no | Section heading. |
| `columns` | `int` | no | `1` (default, stacked) or `2` (two-up). |
| `testimonials` | `array` | yes | List of testimonial objects (see below). |

Each `testimonials[]` entry:

| Field | Type | Required | Notes |
|---|---|---|---|
| `quote` | `string` | yes | The testimonial text. |
| `author` | `string` | yes | Person's name. |
| `role` | `string` | no | Title. Joined to `company` with a comma. |
| `company` | `string` | no | Organisation. |
| `photo` | `image path` | no | Small circular avatar. |

## Example usage

```yaml
- component: testimonial-card
  inputs:
    eyebrow: "What clients say"
    heading: "In their words"
    columns: 2
    testimonials:
      - quote: "They reframed the problem before writing a line of code. The result paid for itself in a quarter."
        author: "Fatima Al-Rashid"
        role: "COO"
        company: "Gulf Logistics"
      - quote: "The most disciplined delivery team we have worked with in the region."
        author: "James Carter"
        role: "VP Engineering"
        company: "Meridian"
```

## Notes

- An accent-tinted opening quotation mark is drawn in the top-start corner of
  each card and mirrors to the right in RTL.
- The italic quote is set upright in Arabic (italic has no meaning there) with
  a looser line-height.
- `mode: flowing-protect-items` keeps a card from splitting across a page break.
