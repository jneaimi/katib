# tutorial-step

Numbered tutorial step — step-circle + title + description, with an optional screenshot image below.

## Inputs

| Name | Type | Required | Notes |
|---|---|---|---|
| `number` | int | yes | 1-based step number, rendered in a solid step-circle |
| `title` | string | yes | Step heading (h3) |
| `body` | string | no | Paragraph explaining the step |
| `screenshot` | image | no | Optional supporting screenshot |
| `screenshot_alt` | string | no | Falls back to `"Screenshot for step N"` (EN) / `"لقطة شاشة للخطوة N"` (AR) |
| `screenshot_caption` | string | no | Caption below screenshot |

## Image sources accepted

`screenshot` · `user-file`

**No gemini source.** Tutorial screenshots are factual depictions of a real UI — AI-generated substitutes would be misleading. This is an explicit component-level policy enforced by `sources_accepted`.

## Usage

### Text-only step

```yaml
- component: tutorial-step
  inputs:
    number: 1
    title: "Install the tool"
    body: "Run `npx @jasemal/katib install` to drop the skill into ~/.claude/skills/katib/."
```

### With a Playwright screenshot

```yaml
- component: tutorial-step
  inputs:
    number: 2
    title: "Verify the install"
    body: "Check that the settings page loads cleanly."
    screenshot:
      source: screenshot
      url: "https://example.com/settings"
      viewport: [1440, 900]
      wait_for: ".settings-loaded"
    screenshot_alt: "Settings page with 'loaded' indicator"
    screenshot_caption: "Settings page, rendered via Playwright at 1440×900."
```

### With a user-supplied image

```yaml
- component: tutorial-step
  inputs:
    number: 3
    title: "Review the output"
    body: "Open the generated PDF — it should look like the reference."
    screenshot:
      source: user-file
      path: "docs/reference-render.png"
    screenshot_alt: "Reference PDF output"
```

## Page behaviour

`break_inside: avoid` — step circle + heading + description + screenshot stay paired on one page.
