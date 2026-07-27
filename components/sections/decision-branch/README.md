# decision-branch

## Purpose

Static-print substitute for the interactive tabbed-tutorial control. Pick one canonical branch, lay it out in full, demote the alternates to a compact appendix block. Keeps the reader on a single happy path while signalling that other paths exist.

## When to use

- A tutorial supports multiple languages, frameworks, or operating systems and the digital version uses tabs
- A recipe has a primary path and substitutions worth surfacing
- A procedure has a "common case" and a few edge variants
- Any place the digital answer is "Tabs" or a "Pick one" radio control

## Inputs

```yaml
- component: decision-branch
  variant: branched-list      # tabs-static | branched-list (default)
  inputs:
    heading: "Choose your path"     # optional — defaults per-lang
    prompt: "Operating system?"     # optional — the question being branched on
    branches:
      - label: "macOS"
        when: "Apple silicon or Intel"
        primary: true                # exactly ONE branch should set primary: true
        body: |
          1. Install via `brew install [tool]`
          2. Run `[tool] init` from your project root.
      - label: "Linux"
        when: "Ubuntu / Debian"
        body: |
          Install with `apt install [tool]`. Same `init` step applies.
      - label: "Windows"
        when: "WSL2 recommended"
        body: |
          Use the WSL2 Ubuntu image, then follow the Linux steps.
    alternates_label: "Other paths"  # optional — defaults per-lang
```

## Variants

- **branched-list** (default) — primary branch presented as a highlighted block with leading marker; alternates listed below as a small appendix. Cleanest for prose-heavy tutorials.
- **tabs-static** — visual tab chrome at the top with the selected tab highlighted. Best when the digital version uses literal tabs and you want to mirror that affordance for the reader.

## Default labels

| Field | EN | AR |
|---|---|---|
| `heading` | `Choose your path` | `اختر مسارك` |
| `alternates_label` | `Other paths` | `مسارات أخرى` |

## Bilingual notes

- The leading marker on the primary branch flips: `▶` (LTR pointing-right) becomes `◀` (RTL pointing-left), so the directional cue always points "into" the body content.
- Border accent rules (`border-left` for LTR, `border-right` for AR) keep the accent on the logical-leading edge of both the primary block and the alternates list.
- Italic styling for `when` and `prompt` is dropped in AR (italic is not a native Arabic typographic convention).

## Visual semantics

- The primary branch sits in a tinted box with an accent leading-rule, headed by the option label and the `when` condition. This is the "do this" path.
- The tab chrome (in `tabs-static`) renders inactive tabs in muted tag-bg colour with secondary text, so the reader's eye lands on the active tab without effort.
- The alternates appendix is rendered in smaller type below a hairline divider, signalling secondary-reference status.

## Pedagogy

Mirrors the "Pick canonical path" pattern from Stripe's docs (which sometimes uses tabs but always recommends a primary path) and Microsoft Learn (which often surfaces a "common case" before edge cases). Replaces interactive tabs with what print can do: spatial demotion. The reader still sees that other paths exist (so they're not stuck on the wrong one) but the page real estate is given to the recommended path. Embodies Mayer's coherence principle: don't dilute attention with parallel tracks when one is canonical.

## Companion components

- `prerequisites-grid` — fans out before this; once prerequisites are checked, branch on environment
- `code-step` — what fills the `body` of each branch (use raw markdown / `module`-style prose)
- `tutorial-step` — alternative content for the body when the branch is procedural

Part of the Tutorial Component Pack — Sprint 3 / Phase C.
