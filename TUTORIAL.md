# Tutorial — Build your first custom Katib component

A 20-minute walkthrough. You'll build a `testimonial` component — an
inline quote block with an attribution line — and wire it into a
recipe. By the end, the component lives in your `~/.katib/components/`
tier, survives skill reinstalls, and can be shared with other Katib
users under the Phase 4 sharing flow.

**Prerequisites:** Katib v2-alpha installed (`npx @jasemal/katib@alpha install`)
and Claude Code running.

---

## Why use the AI-assisted builder?

The classic flow — `scripts/component.py new <name>` — produces empty
boilerplate files. You fill them in by hand. That works, but three things
go wrong in practice:

- **The schema has traps.** Naming an input `description` clashes silently.
  Declaring a token in `requires.tokens` that your CSS doesn't use
  triggers warnings.
- **Bilingual typography is subtle.** Arabic needs larger font sizes,
  looser line-height, and no letter-spacing transforms — every time.
- **WeasyPrint is a specific CSS subset.** `inset: 0` gets silently
  ignored. `@page` interacts with `page-break-*` in ways the browser
  doesn't train you for.

The AI-assisted builder handles all of that. You focus on **what the
component shows**. The builder handles **how to encode it correctly**.

---

## Step 1 — Invoke the builder

In Claude Code, type:

```
/katib component new testimonial
```

(Or just describe what you want — "I need a testimonial block component"
— and Claude will recognize the intent and pivot into builder mode.)

Claude follows the
[COMPONENT-BUILDER.md](COMPONENT-BUILDER.md) playbook. First, it asks
you 5 questions in one shot:

1. **Name** → `testimonial`
2. **Tier** → `primitive` (small, inline reusable piece)
3. **Languages** → `en + ar`
4. **Inputs** — you describe them, Claude structures them:
   - `quote` (string, required) — the quote itself
   - `author` (string, required) — who said it
   - `role` (string, optional) — title / company
   - `avatar` (image, optional) — headshot image
5. **Closest exemplar** — Claude suggests `pull-quote` (similar structural
   shape — quote with attribution) and `figure-with-caption` (has an
   image slot). Pick `pull-quote` — it's closer.

---

## Step 2 — Scaffold runs automatically

Claude runs the deterministic scaffolder:

```bash
uv run scripts/component.py new testimonial \
    --tier primitive \
    --namespace user \
    --languages en,ar \
    --description "Quote block with author + optional role + optional avatar. For proposals, about-pages, case studies."
```

This creates:
- `~/.katib/components/primitives/testimonial/component.yaml` (with TODO markers)
- `en.html`, `ar.html` (stub templates)
- `README.md` (stub)
- Audit entry in `~/.katib/memory/component-audit.jsonl`

The `--namespace user` flag matters — the component lands in your user
tier (`~/.katib/`), survives reinstall, and can be shared with other
users.

---

## Step 3 — Claude generates the real files

Claude reads the exemplar (`components/primitives/pull-quote/`) to
match the house style. It writes:

**`component.yaml`:**

```yaml
name: testimonial
tier: primitive
version: 0.1.0
namespace: user
description: Quote block with author + optional role + optional avatar.
languages: [en, ar]
requires:
  tokens: [text, text_secondary, accent, border]
  fonts: [display, primary]
accepts:
  inputs:
    - quote:
        type: string
        required: true
    - author:
        type: string
        required: true
    - role:
        type: string
        required: false
    - avatar:
        type: image
        required: false
        sources_accepted: [user-file, url]
variants:
  - default
  - with-avatar
```

**`en.html`:**

```jinja
{%- set v = variant or 'default' %}
<blockquote class="katib-testimonial katib-testimonial--{{ v }}" lang="en">
    <p class="katib-testimonial__quote">{{ input.quote }}</p>
    <footer class="katib-testimonial__attribution">
{%- if v == 'with-avatar' and input.avatar and input.avatar.resolved_path %}
        <img class="katib-testimonial__avatar" src="{{ input.avatar.resolved_path }}" alt="">
{%- endif %}
        <div class="katib-testimonial__meta">
            <span class="katib-testimonial__author">{{ input.author }}</span>
{%- if input.role %}
            <span class="katib-testimonial__role">{{ input.role }}</span>
{%- endif %}
        </div>
    </footer>
</blockquote>
```

Similar `ar.html` with `dir="rtl"` and Arabic-aware class usage.

**`styles.css`** — Claude uses the token system (`var(--accent)`,
`var(--font-display)`), handles the RTL quote-mark flip, increases
Arabic font size, removes italic from the Arabic variant.

---

## Step 4 — Validate

```bash
uv run scripts/component.py validate testimonial
```

```
components/primitives/testimonial — validate
  ✓ all checks passed

0 error(s), 0 warning(s).
```

If the validator reports errors (missing input declared in HTML,
unknown token, schema violation), Claude reads them, fixes the files,
and re-runs. You see the iteration loop in real time.

---

## Step 5 — Preview

```bash
uv run scripts/component.py test testimonial
```

```
Isolated render — test harness
  ✓ en + default      → dist/component-tests/testimonial/testimonial.en.pdf (6458 bytes, 0 wp warnings)
  ✓ ar + default      → dist/component-tests/testimonial/testimonial.ar.pdf (6059 bytes, 0 wp warnings)
  ✓ en + with-avatar  → ...
  ✓ ar + with-avatar  → ...
```

Claude shows you the PDF paths. Open them and look. Zero WeasyPrint
warnings = clean render.

---

## Step 6 — Iterate

You open the PDF and notice the quote marks aren't styled the way you
expected. Tell Claude:

> "Make the opening quote mark a large accent-colored left-double-quote
> character, hanging outside the margin."

Claude edits `styles.css`, re-runs `validate` and `test`, shows the
updated PDF. You approve.

---

## Step 7 — Register

```bash
uv run scripts/component.py register testimonial
```

```
✓ testimonial registered
  capabilities.yaml regenerated
  audit trail: action=register at=2026-04-25T10:23:17+00:00
```

`capabilities.yaml` now includes the testimonial component — the router
knows about it, future recipes can reference it by name.

---

## Step 8 — Use it in a recipe

Scaffold a recipe:

```bash
uv run scripts/recipe.py new my-case-study --namespace user \
    --description "Case study with client testimonial"
```

Edit `~/.katib/recipes/my-case-study.yaml`:

```yaml
name: my-case-study
namespace: user
languages: [en]
sections:
  - component: module
    inputs:
      title: "Case Study: Acme Corp"
      body: "How we helped Acme reduce their deployment times by 40%."

  - component: testimonial
    variant: with-avatar
    inputs:
      quote: "Katib cut our proposal generation from 4 hours to 15 minutes. Every template looks on-brand because we don't have to reassemble it each time."
      author: "Alex Acme"
      role: "VP Engineering, Acme Corp"
      avatar:
        source: user-file
        path: assets/acme-headshot.jpg
```

Render:

```bash
uv run scripts/build.py my-case-study --lang en
```

Your custom testimonial component renders inline alongside the bundled
`module`. The shadow semantics handled it automatically — no config.

---

## What you get for free

- **Audit trail** — every component you create has an audit entry so the
  build gate knows it's not an orphan file.
- **`capabilities.yaml` integration** — the `/katib` router can suggest
  your component when future requests match.
- **Durability** — `~/.katib/components/testimonial/` survives
  `npx @jasemal/katib@alpha install` runs. The skill dir gets replaced;
  your content doesn't.
- **Shareability (Phase 4)** — your component will be packageable into
  a single tarball another Katib user can import with one command.

---

## Troubleshooting

| Symptom | Most likely cause | Fix |
|---|---|---|
| `ERROR: component.yaml schema validation failed` | Input named `description` | Rename to `overview`, `blurb`, `note`, or `intro`. |
| `WeasyPrint warning: Ignored 'inset: 0'` | WeasyPrint CSS subset | Use `top/right/bottom/left: 0` instead. |
| `⚠ token 'X' declared in requires.tokens but not referenced` | Leftover from scaffold | Remove the token from `requires.tokens` — only keep tokens your CSS uses. |
| Component renders but surrounding recipe layout looks off | Missing `page_behavior` | Set `mode: flowing` for inline primitives, `mode: atomic` for full-page components. |
| `/katib` doesn't see your new component | `capabilities.yaml` stale | `scripts/component.py register <name>` regenerates it. The router also regenerates on staleness detection. |

---

## What to build next

- A `hero-banner` section for marketing docs
- A `faq-block` primitive with expand/collapse styling
- A `comparison-table` section for product pitches
- A `contact-card` primitive for business cards

Each one follows the same flow. As the library grows, each new
component has richer exemplars to learn from. The builder gets better
at its job with every new component you add.

---

## Reference

- [COMPONENT-BUILDER.md](COMPONENT-BUILDER.md) — full playbook with
  exemplar picker, schema contract, pitfall cheat sheet
- [SKILL.md](SKILL.md) — how `/katib` invocations route through the
  skill, including component-creation mode
- [CHANGELOG.md](CHANGELOG.md) — phase-by-phase design decisions
