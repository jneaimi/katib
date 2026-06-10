# team-grid

## Purpose

Leadership / team member grid — each member is a card with a photo (or an
initial-placeholder), name, role, optional credentials line, and a short bio,
laid out in 2–4 columns. Use it for company-profile leadership pages, about-us
team sections, advisory boards, and any people-with-bios layout. Reach for
`org-chart` instead when you need reporting hierarchy, and `feature-row` when
the cards carry ideas rather than people.

## Variants

| Variant | When to use |
|---|---|
| `default` | Open cards — photo + text, no frame. The standard look. |
| `bordered` | Each member framed in a thin-bordered card. Good when members sit on a busy or coloured page. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | `string` | no | Uppercase kicker above the heading. |
| `heading` | `string` | no | Section heading above the grid. |
| `columns` | `int` | no | `2`, `3` (default), or `4`. |
| `members` | `array` | yes | List of member objects (see below). |

Each `members[]` entry:

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | `string` | yes | Full name. |
| `role` | `string` | yes | Title / position. |
| `photo` | `image path` | no | Square crops look best. Falls back to a coloured initial. |
| `credentials` | `string` | no | Short line, e.g. `MBA, PMP`. |
| `bio` | `string` | no | One-paragraph blurb. |

## Example usage

```yaml
- component: team-grid
  inputs:
    eyebrow: "Leadership"
    heading: "The people behind the work"
    columns: 3
    members:
      - name: "Layla Al-Hashimi"
        role: "Chief Executive Officer"
        photo: "assets/layla.jpg"
        credentials: "MBA, INSEAD"
        bio: "Twenty years scaling regional consultancies across the GCC."
      - name: "Omar Saeed"
        role: "Head of Engineering"
        credentials: "MSc, PMP"
        bio: "Leads delivery for the platform and data practices."
```

## Notes

- The avatar is a fixed-diameter circle; the member card is a flex column so a
  fixed-width photo aligns to the inline-start edge in both LTR and RTL while
  the text blocks fill the cell.
- RTL: uppercase / letter-spacing is dropped from the eyebrow and credentials
  lines, and the bio uses a looser line-height.
- `mode: flowing-protect-items` keeps a single member card from splitting
  across a page break.
