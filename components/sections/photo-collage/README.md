# photo-collage

**Tier:** section · **Languages:** EN + AR · **Namespace:** user

## Purpose

Magazine-style asymmetric photo collage. Six images arranged in a mosaic — one hero on the left at full collage height, three stacked supporting images in the right column, and two more in a wide bottom row. Optional eyebrow, title, subtitle, and source attribution.

Designed for news galleries, event coverage, photo essays.

## Layout

```
┌─────────────────────┬───────────────┐
│                     │   top_image   │
│                     ├───────────────┤
│     hero_image      │  middle_image │
│                     ├───────────────┤
│                     │  bottom_image │
├─────────────────────┴───────────────┤
│  wide_left_image  │  wide_right_image│
└─────────────────────────────────────┘
```

The grid is implemented with HTML `<table>` (rowspan on the hero) for WeasyPrint compatibility.

## Inputs

| Slot | Required | Notes |
|---|---|---|
| `eyebrow` | no | Small label above the title (e.g. "معرض الصور"). |
| `title` | no | Section heading rendered above the collage. |
| `subtitle` | no | One-line subtitle under the heading. |
| `hero_image` | **yes** | Left column, full collage height. Sources: `user-file`, `url`, `gemini`. |
| `top_image`, `middle_image`, `bottom_image` | **yes** | Right column, top-to-bottom. |
| `wide_left_image`, `wide_right_image` | **yes** | Bottom row, 50/50 split. |
| `*_caption` | no | Caption overlaid on each image with a soft dark gradient at the bottom. |
| `source_attribution` | no | Tiny credit line below the grid. |

All image slots accept `user-file`, `url`, or `gemini` sources. URLs are downloaded at render time; missing or 403'd URLs fall back to Gemini if `fallback: gemini` is added.

## Usage example

```yaml
- component: photo-collage
  inputs:
    eyebrow: "معرض الصور"
    title: "مهرجان الحصن 2026 في صور"
    hero_image:
      source: user-file
      path: tests/fixtures/cover-bg.jpg
    hero_caption: "القلعة — أقدم مبنى حجري في أبوظبي"
    top_image:
      source: gemini
      prompt: "Emirati heritage souq at golden hour..."
    top_caption: "السوق التراثي"
    # ... and so on for middle, bottom, wide_left, wide_right
    source_attribution: "المصدر: دائرة الثقافة والسياحة - أبوظبي"
```

## Accessibility notes

- Root element carries `lang` / `dir` attributes (EN ltr, AR rtl).
- `<img alt>` defaults to the caption when present.
- Captions are rendered as real text overlays (not baked into the image), so screen readers can read them.
- Each image cell has visible borders for printability.
