# video-card

**Tier:** section

## Purpose

Video preview card for print PDFs. Shows thumbnail with play overlay, platform badge, title, author/duration, clickable URL, and QR code. Bilingual EN+AR. For TikTok / YouTube Shorts / Instagram Reels in print.

## Variants

- default

## Inputs

- `title` (string, required): …

## Usage Example

```yaml
- component: video-card
  inputs:
    title: "Example title"
```

## Accessibility Notes

- Root element carries `lang` / `dir` attributes
