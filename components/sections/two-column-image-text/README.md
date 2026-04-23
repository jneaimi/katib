# two-column-image-text

Most flexible image-consuming section. Image on one side, text on the other. Accepts every image source the provider layer knows about.

## Variants

| Variant | Layout |
|---|---|
| `image-left` (default) | Image column left, text column right (auto-flipped under RTL) |
| `image-right` | Image column right, text column left |
| `image-top` | Image full-width at top, text below (good for narrow sections or mobile-first source docs) |

**RTL behaviour:** `image-left` in an Arabic recipe renders image on the *right* (the LTR-logical "left" — the reading origin). If you want the image physically on the left in Arabic, use `image-right`.

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `image` | image | yes | See sources below |
| `alt_text` | string | yes | Accessibility alt text |
| `eyebrow` | string | no | Small accent label above heading |
| `heading` | string | no | H2 above body |
| `body` | string | no | Short paragraph. Multi-paragraph content belongs in module. |
| `caption` | string | no | Caption under image |

## Image sources accepted

`user-file` · `url` · `gemini` · `screenshot`

The most permissive image declaration in the v2 library. Screenshots are allowed because the pattern "browser screenshot + explanatory text" is common in product walkthroughs. Gemini is allowed for editorial/decorative uses.

## Usage

### With a user-supplied photo

```yaml
- component: two-column-image-text
  variant: image-left
  inputs:
    eyebrow: "Case study"
    heading: "Our team at launch"
    image:
      source: user-file
      path: "~/Downloads/team.jpg"
      alt_text: "Five people at the 2026 launch event"
    alt_text: "Five people at the 2026 launch event"
    body: |
      We shipped v1 in 48 hours. Here's what was in the room.
```

### With a Gemini-generated illustration

```yaml
- component: two-column-image-text
  variant: image-right
  inputs:
    heading: "Our approach"
    image:
      source: gemini
      prompt: "abstract geometric pattern, warm amber and navy, editorial"
      aspect: "4:3"
    alt_text: "Abstract geometric pattern in amber and navy"
    body: |
      Composition over inheritance — every section does one thing.
```

### With a Playwright screenshot

```yaml
- component: two-column-image-text
  variant: image-top
  inputs:
    heading: "The result"
    image:
      source: screenshot
      url: "https://example.com/dashboard"
      viewport: [1440, 900]
      wait_for: ".dashboard-loaded"
      hide: [".cookie-banner"]
    alt_text: "Product dashboard with live metrics"
    caption: "Screenshot captured 2026-04-23 via Playwright + Chromium."
```

## Page behaviour

`break_inside: avoid` — the image and text should stay paired on one page.
