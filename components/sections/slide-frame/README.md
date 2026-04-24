# slide-frame

## Purpose

A single 16:9-style landscape page sized for slide-deck content — talk
slides, pitch decks, keynote frames. Each slide is atomic (one slide =
one page, never splits). Chain multiple `slide-frame` sections in a
recipe to build a full deck.

## Variants

| Variant | When to use |
|---|---|
| `title-only` | Section opener or hero slide — large centered title + optional subtitle. |
| `content` | Default talk slide — eyebrow + title + bullet list or short paragraph. |
| `two-column` | Side-by-side layout — main content on the left, supporting stat/quote/figure on the right (RTL for Arabic). |
| `image-background` | Full-bleed image slide with white text + scrim for legibility. |

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Category/section label above the title (e.g. `"01 · INTRODUCTION"`). |
| `title` | string | no* | Slide headline. *Required for title-only and content variants. |
| `subtitle` | string | no | Secondary line under the title. |
| `raw_body` | string | no* | HTML body — bullets, figures. *Required for content + two-column. |
| `raw_body_secondary` | string | no | Right-column HTML for two-column variant. |
| `image` | image | no | Full-bleed background — only used by image-background variant. |

## Example — title slide + two content slides

```yaml
- component: slide-frame
  variant: title-only
  inputs:
    eyebrow: "KEYNOTE 2026"
    title: "Bilingual Print for the AI Era"
    subtitle: "Why the next generation of documents is composable."

- component: slide-frame
  variant: content
  inputs:
    eyebrow: "01 · THE PROBLEM"
    title: "Templates don't scale."
    raw_body: |
      <ul>
        <li>Hardcoded sample content corrupts skill updates.</li>
        <li>Each new doc-type adds entropy instead of reuse.</li>
        <li>Bilingual handling gets duplicated everywhere.</li>
      </ul>

- component: slide-frame
  variant: two-column
  inputs:
    eyebrow: "02 · THE FIX"
    title: "Composable components."
    raw_body: |
      <p>Every visible element is a reusable component. Doc-types become
      YAML recipes that reference components by name.</p>
    raw_body_secondary: |
      <blockquote>
      "One slide, one page. One component, many slides."
      </blockquote>
```

## Notes

- Uses a named `@page slide { size: A4 landscape; }` rule. Recipe
  authors who want true 16:9 sizing can override with a custom CSS
  block in their recipe.
- `page_behavior: atomic` + `break_before/after: always` ensures every
  slide stands alone.
- Image-background variant automatically applies a white scrim over the
  image so title + subtitle + eyebrow stay legible.
