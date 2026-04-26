# cover-page

Full-page document opener. First-class `cover` tier component.

## Variants

| Variant | Look | Image source |
|---|---|---|
| `minimalist-typographic` (default) | CSS-only — big display-font title, small eyebrow, brand logo top, footer strip with author + ref | none |
| `image-background` | Full-bleed photo/illustration with dark-scrim overlay; title in white | `user-file` · `url` |
| `neural-cartography` | Gemini-generated abstract background + softer scrim | `gemini` (requires `GEMINI_API_KEY`) |
| `framed-canvas` | Light editorial canvas — full-bleed warm off-white image, dark text on top, no scrim; for image compositions that frame a clean center for typography | `user-file` · `url` · `gemini` |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Category label — rendered in accent-2 color, uppercase |
| `title` | string | yes | Document title — 42pt display, auto-wraps |
| `subtitle` | string | no | Rendered 14pt under title |
| `reference_code` | string | no | Monospace code in footer-right |
| `image` | image | no | Required for `image-background` and `neural-cartography`. Missing → variant falls back to typographic. |

## Automatic brand fields (no input needed)

Cover pulls from the merged token context:
- `logo.primary` → rendered top if set
- `identity.author_name` → footer-left
- `name` (brand display name) → used as logo alt-text

Set these in your brand YAML or they render empty.

## Usage

### Minimalist-typographic (CSS-only)

```yaml
- component: cover-page
  variant: minimalist-typographic
  inputs:
    eyebrow: "Tutorial"
    title: "Bloom's AI Collaboration Framework"
    subtitle: "Six-level cognitive stack for deciding when AI should execute vs. when humans should evaluate."
    reference_code: "JN-AI-0001"
```

### Image-background (user-supplied image)

```yaml
- component: cover-page
  variant: image-background
  inputs:
    eyebrow: "Case study"
    title: "Dubai Internet City"
    subtitle: "Where the GCC's software gravity centered."
    image:
      source: user-file
      path: "~/Downloads/dic-hero.jpg"
      alt_text: "DIC campus aerial shot"
```

### Neural-cartography (Gemini-generated)

```yaml
- component: cover-page
  variant: neural-cartography
  inputs:
    eyebrow: "White paper"
    title: "The GCC AI Ecosystem"
    subtitle: "A field map from April 2026."
    image:
      source: gemini
      prompt: "abstract topographic map, warm amber and deep navy, editorial style, wide landscape"
      aspect: "3:4"
      style: editorial
```

A missing/invalid `GEMINI_API_KEY` at render time raises a fail-loud error from the provider layer — no silent placeholder.

## Page behaviour

- `break_after: always` — body content starts on page 2
- `break_inside: avoid` — cover never splits
- `min-height: 253mm` — fills A4 minus default margins (297mm − 2×22mm gutters)

## Behaviour when image is missing

If `variant: image-background` or `neural-cartography` is set but no `image` input is supplied (or the image spec is malformed), the template emits the cover without a background — effectively falling back to the minimalist layout. Rendering succeeds, but the cover will look different from the author's intent. Watch for this during review.
