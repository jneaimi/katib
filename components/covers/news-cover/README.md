# news-cover

**Tier:** cover · **Languages:** EN + AR · **Namespace:** user

## Purpose

Newspaper-style cover page. Stacked layout — eyebrow + thick top rule + large headline at the top, rectangular hero image in the middle, optional caption + byline strip + subtitle/deck under the image, footer with author and reference code at the bottom.

Designed for digital news stories and print article openers; mirrors front-page feature layouts in Al Ittihad / Al Bayan / The National.

Use this when the document is an **article that needs a clear headline-first reading order** (the eye lands on the title, then the image, then the deck). Compare to `cover-page` (full-bleed background image with text layered on top) which is better for branded covers, white papers, and reports.

## Variants

| Variant | Look |
|---|---|
| `default` | Stacked: masthead → image → deck → footer. The only variant. |

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Category label rendered uppercase (EN) or as-is (AR), accent-2 color. |
| `title` | string | **yes** | Headline. ~36pt EN / ~38pt AR. |
| `subtitle` | string | no | Deck rendered under the byline. |
| `image` | image | **yes** | Hero image (~3:2 rectangle, ~105mm tall). Sources: `user-file`, `url`, `gemini`. Falls back to a Gemini-generated placeholder if missing. |
| `caption` | string | no | Italic muted caption shown directly under the image. |
| `byline` | string | no | One-line strip — convention `"By X · City · Date · Reading time"` (EN) or `"بقلم X · المدينة · التاريخ · زمن القراءة"` (AR). |
| `reference_code` | string | no | Monospace code rendered footer-right. |

## Automatic brand fields

- `identity.author_name` → footer-left

## Usage example

```yaml
- component: news-cover
  inputs:
    eyebrow: "خبر · ثقافة"
    title: "ولي عهد أبوظبي يحضر «مهرجان الحصن 2026»"
    subtitle: "16 يوماً من الاحتفاء بالتراث الإماراتي في قلب العاصمة."
    byline: "بقلم الطالب · أبوظبي · 26 أبريل 2026 · 4 دقائق قراءة"
    reference_code: "AL-HOSN-2026"
    caption: "صورة: القلعة في ساعة الذروة الذهبية"
    image:
      source: gemini
      prompt: |
        Editorial photograph of the old fort at golden hour, palm trees,
        warm desert tones, no text, 3:2 horizontal composition.
```

## Accessibility notes

- Root element carries `lang` / `dir` attributes (EN ltr, AR rtl).
- `<img alt>` defaults to the caption when present.
- The thick top rule and thin hairline are decorative and present visually only — screen readers skip them naturally because they are CSS borders.
- The headline is `<h1>` (one per page).
