# slide-quote

Single 16:9 landscape slide carrying a dramatic centered pull quote with attribution.

## When to use

- Testimonial slides in pitch decks and sales decks
- Founder-vision slides
- Customer-quote slides between case studies
- Any slide where one person's words should carry the moment

For block quotes inside the body of a long-form document, use the `pull-quote` primitive instead.

## Inputs

| Field | Required | Description |
|---|---|---|
| `eyebrow` | no | Small uppercase label above the quote (e.g. "WHAT CUSTOMERS SAY"). |
| `quote` | yes | Quote body — pass words only, no curly quotes. |
| `author` | yes | Person being quoted. |
| `role` | no | Role + organisation (e.g. "Head of Procurement, Acme"). |
| `source` | no | Optional source citation (publication + date). |

## Example

```yaml
- component: slide-quote
  inputs:
    eyebrow: "WHAT CUSTOMERS SAY"
    quote: "We replaced six different document templates with one katib install. The first month saved my team about forty hours of formatting."
    author: "Layla Al-Mansoori"
    role: "Head of Procurement, Acme Corp"
    source: "Customer interview, March 2026"
```
