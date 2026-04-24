# code-block

**Tier:** primitive
**Version:** 0.1.0
**Namespace:** katib
**Languages:** EN + AR

## Purpose

Preformatted code / shell-command block with consistent styling across
tutorials, how-to guides, and handoff docs. Two variants — a dark
`terminal` look for CLI / install / config samples, and a lighter
theme-aware `inline` look for single-command references. Atomic: code
blocks never split across pages.

## When to use

| Use | Component |
|-----|-----------|
| Multi-line CLI samples, config files, install sequences | `code-block variant: terminal` |
| Short deploy / rollback / one-liner commands | `code-block variant: inline` |
| Keyboard shortcuts, tags, pill-style indicators | `tag-chips` |
| Structured key/value pairs | `kv-list` |
| Prose with emphasis | `callout` |

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `code` | string | yes | Code content. Raw HTML permitted — inline comment spans may use `class="katib-code-block__comment"` for zinc-400 color on the terminal variant. |
| `label` | string | no | Filename or small caption rendered above the block (e.g., `~/.config/katib/config.yaml`). |

## Variants

- `terminal` (default) — dark zinc background (`#27272A`), zinc-100 text, 8.5pt mono.
- `inline` — theme-aware light (`tag_bg` background), 9pt mono. For single-command references.

## Example — terminal with comment and label

```yaml
- component: code-block
  variant: terminal
  inputs:
    label: "~/.katib/brands/acme.yaml"
    code: |
      <span class="katib-code-block__comment"># brand identity</span>
      name: Alex Acme
      accent: "#1F3A68"
```

## Example — inline single command

```yaml
- component: code-block
  variant: inline
  inputs:
    code: "deploy rollback --service api --to-version abc123"
```

## Pagination

`page_behavior.mode: atomic` — code blocks never split. For unusually
long code samples that exceed a page, override at the recipe level with
`page_behavior: flowing` on the section.

## Token contract

`text`, `tag_bg`, `font-mono`.

## RTL

Code content always renders LTR (`direction: ltr`) regardless of document
direction — mandatory for code correctness. Label inherits document direction.
