# cover-magazine

Magazine-style full-page cover. A hero image (or accent block) sits on the leading half, a big editorial title and subtitle fill the trailing half, and an "Inside this issue" lineup runs along the bottom.

## When to use

- Quarterly customer magazines, brand publications, internal newsletters
- Editorial features where the cover needs to carry visual weight
- Any document where the cover is meant to feel like a publication, not a doc opener

Distinct from `cover-page` — that's a doc-style cover (title + subtitle + footer). `cover-magazine` is for editorial publications.

## Inputs

| Field | Required | Description |
|---|---|---|
| `issue_meta` | no | Top accent strip text — e.g. "Issue 04 · April 2026 · 12 min read". |
| `eyebrow` | no | Small uppercase label above the title — e.g. "FEATURE", "COVER STORY". |
| `title` | yes | The headline. Short, editorial, scannable. |
| `subtitle` | no | One- or two-sentence deck under the title. |
| `byline` | no | Author / contributors line — e.g. "By Jasem Al-Neaimi". |
| `image` | no | Hero image rendered on the leading half. Falls back to a monogram block if absent. |
| `lineup` | no | Array of `{title, page?}` — "Inside this issue" lineup along the bottom. |

## Example

```yaml
- component: cover-magazine
  inputs:
    issue_meta: "Issue 04 · April 2026 · 12 min read"
    eyebrow: "COVER STORY"
    title: "The Bilingual Document Engine"
    subtitle: "How katib turns markdown into print-grade PDFs that work in Arabic and English."
    byline: "By Jasem Al-Neaimi"
    image: { source: "user-file", path: "covers/issue-04-hero.jpg" }
    lineup:
      - title: "Inside the marketplace"
        page: 3
      - title: "Why bilingual is hard"
        page: 7
      - title: "Behind the scenes"
        page: 12
      - title: "What's next"
        page: 18
```

## Notes

- Page mode is `atomic` — the cover always stands on its own page.
- The hero side flips automatically for Arabic (the image moves to the leading edge in RTL).
- If no `image` is provided, the hero fills with an accent-tinted monogram of the first character of the title.
