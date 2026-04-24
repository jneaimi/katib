# two-column-page

## Purpose

Newspaper / magazine two-column text flow. The title, byline, and lead
paragraph span both columns at the top; the body splits into two
columns that flow naturally across the page and continue to subsequent
pages if the article is long. Best for editorial essays, long-form
articles, and primary-source excerpts where a single column feels
lonely.

## Inputs

| Input | Type | Required | Notes |
|---|---|---|---|
| `eyebrow` | string | no | Category label (e.g. `"ESSAY"`, `"LONG READ"`). |
| `title` | string | no | Article title — spans both columns. |
| `byline` | string | no | Author + dateline. |
| `lead` | string | no | Deck paragraph in a larger font, above the two-column flow. |
| `raw_body` | string | **yes** | Article body. Flows as two justified columns. |

## Example

```yaml
- component: two-column-page
  inputs:
    eyebrow: "ESSAY"
    title: "The Last Typewriter in Dubai"
    byline: "By Alex Acme · Dubai, 2026"
    lead: "In a corner of Deira, one shop still repairs the machines that built a city's paperwork."
    raw_body: |
      <p>The shop door has no name. A sun-bleached sticker in the
      window says only: typewriter repair, upper floor.</p>
      <p>Inside, on a wooden desk that long predates the current
      business license, sits Mahmoud. He is the only person in the
      emirate, he tells you, who still fixes the Olympia SM9.</p>
      <blockquote class="span-cols">
        "The keys remember. The paper forgives. Everything after
        that is habit."
      </blockquote>
      <p>The shop opened in 1979...</p>
```

## Notes

- Uses standard CSS multi-column (`column-count: 2`). WeasyPrint
  supports this natively — no named `@page` rule required.
- Content **flows across multiple pages** when long — `page_behavior:
  flowing`. Readers follow column 1 → column 2 → page 2 column 1 →
  page 2 column 2 etc.
- Use `class="span-cols"` on any element inside `raw_body` to make it
  break out and span both columns (e.g. pull-quotes, wide figures).
- Arabic variant right-aligns, uses slightly larger font and looser
  line-height for legibility, and disables hyphenation.
- `orphans: 2; widows: 2` on paragraphs keeps single-line dangles out
  of the column breaks.
