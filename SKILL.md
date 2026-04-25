---
name: katib
description: |
  Bilingual print-grade PDF generator. Compose documents from components via
  YAML recipes, render to PDF with WeasyPrint, output to OS-standard user
  paths. Bare /katib enters context-aware mode — reads recent session
  context, matches against capabilities.yaml, proposes a render or fires a
  structured decision gate for ambiguous requests.
---

# Katib — v2 Runtime Flow

## Invocation modes

| Invocation | Behavior |
|---|---|
| `/katib` (bare) | Context-aware. Assemble recent session context as a transcript; let sensor+gate route. |
| `/katib <prose>` | Use the prose as the transcript. |
| `/katib --recipe X --lang Y --brand Z [--slug S]` | Explicit override — skips sensor/gate, renders directly. |
| `/katib --recipe X` (partial flags) | Mix: explicit recipe, other signals inferred from context. |
| `/katib component new [name]` | Enter the AI-assisted component builder — see `COMPONENT-BUILDER.md` for the full playbook. |
| `/katib component list` | Show existing components grouped by tier (read `capabilities.yaml`). |
| `/katib recipe new [name]` | Scaffold a new recipe (`scripts/recipe.py new`). Same shape as `component new` but simpler — just YAML, no Jinja/CSS. |

## The one loop

All routing goes through `scripts/route.py`. The agent is a thin interpreter
on top — read JSON, dispatch on `action`, loop until `render` (or `wait` /
`graduate` terminal).

```
                  ┌──────────────────────┐
                  │ /katib invocation    │
                  └──────────┬───────────┘
                             │
                             v
    (write transcript to temp file, collect explicit flags)
                             │
                             v
          uv run scripts/route.py infer --transcript-file X [flags]
                             │
                             v  JSON
       ┌──────────┬──────────┼───────────────┬──────────┐
       │          │          │               │          │
    render    present_     ask_         ask_intent    error
              candidates  questions
       │          │          │               │          │
       v          v          v               v          v
  build.py   AskUserQ →   AskUserQ →    plain-text    relay
             route.py     route.py       prompt →     message
             infer         resolve       re-infer
             --recipe      --q1 --q2
                           → render/wait/graduate
```

## Step-by-step

### 1. Assemble transcript

- For **bare** `/katib`: from your conversation memory, collect the last
  3–10 user turns related to the current document need. Aim for ~1–4 KB of
  text. Write to a temp file.
- For **prose** `/katib some document ...`: use the prose as transcript.
- For **explicit** `/katib --recipe X`: transcript optional (can be empty);
  `route.py infer` short-circuits the gate.

### 2. Call the router

```bash
uv run scripts/route.py infer \
    --transcript-file /tmp/katib-transcript-XXX.txt \
    [--recipe NAME] [--lang en|ar] [--brand NAME] [--slug S]
```

Parse stdout as JSON. **Always show the user the `summary` field before
acting** (ADR observability requirement). If `capability_notes` is present,
include that too — it means `capabilities.yaml` was regenerated.

### 3. Dispatch on `action`

#### 3a. `action: "render"`

Proceed to rendering. Show the user what's about to happen:

```
Rendering:
  recipe: <recipe>
  lang:   <lang>
  brand:  <brand or "default">

Inferred: <summary>
Reasons: <one or two bullets from reasons[]>
```

Then invoke `build.py` with `--json` so the agent can parse a structured
receipt and decide whether to offer a post-render save:

```bash
uv run scripts/build.py <recipe> --lang <lang> [--brand <brand>] [--slug <slug>] --json
```

The JSON receipt has shape:

```json
{
  "pdf": "/abs/path/out.pdf",
  "bytes": 12345,
  "cover": {
    "rendered": true | false,
    "source": "gemini" | "user-file" | "inline-svg" | "brand-preset" | null,
    "preset_saveable": true | false
  }
}
```

Report the output PDF path on success. If `build.py` exits non-zero, the
receipt will contain an `error` key — show its value verbatim.

#### 3a-post. Post-render save offer (cover presets)

When a render succeeded AND `--brand` was set AND `cover.preset_saveable`
is `true`, offer the user an interactive save via AUQ. This lets the user
capture a freshly-rendered cover (Gemini, user-file) as a reusable preset
on the brand so future recipes can reference it as
`source: brand-preset, name: <name>`.

**Skip the offer silently when:**
- `cover.preset_saveable` is `false` (no cover, already a preset, or
  inline-svg with no file on disk)
- `--brand` was not on the render (nothing to save against)
- The session is non-interactive (AUQ will fail gracefully; don't retry)

**Ask this AUQ (one question, two options):**

```python
AskUserQuestion(questions=[{
    "header": "Save cover?",                       # ≤12 chars
    "question": (
        "This render used a brand cover image. "
        "Save it as a reusable preset on the '<brand>' profile?"
    ),
    "multiSelect": False,
    "options": [
        {"label": "yes-<suggestion>",
         "description": "Save as '<suggestion>'. You can pick a different name next."},
        {"label": "no",
         "description": "Don't save."},
    ],
}])
```

Where `<suggestion>` is `<recipe-slug>-cover` with any non-`[a-z0-9_-]`
chars stripped. E.g., `legal-mou` → `legal-mou-cover`.

**If the user picks `no`:** done. Do not ask again this turn.

**If the user picks `yes-<suggestion>`:** ask in plain text:

```
Preset name? (press Enter to use "<suggestion>", or type a new name —
must match [a-z0-9][a-z0-9_-]*)
```

Validate the answer against `^[a-z0-9][a-z0-9_-]*$` before invoking the
CLI — if invalid, say so and re-ask. Blank input means use the suggestion.

Then call:

```bash
uv run scripts/build.py <recipe> --lang <lang> --brand <brand> \
    --save-cover-preset <chosen-name> --json
```

This re-invokes `build.py`; the PDF is regenerated but expensive image
work (Gemini calls, screenshots) hits the content-hash cache and is not
repeated. The save itself is a file copy into
`~/.katib/brands/<brand>-assets/covers/` plus a `ruamel.yaml` edit on the
brand profile (comments + ordering preserved).

**If the save JSON reports `preset_saved.error` containing
"already has cover preset":** the name collides. Ask inline:

```
Preset '<chosen-name>' already exists on '<brand>'. Overwrite? [y/N]
```

If `y`: re-run the same command with `--force`. Any other answer: report
"Skipped — keep the existing preset." and end the offer.

**On success** (`preset_saved.name` present): report:

```
Saved cover preset '<name>' → <path>
```

Do NOT loop the offer. One attempt per render.

#### 3b. `action: "present_candidates"` (MEDIUM confidence)

The response contains an AUQ-ready `question` block. Hand it straight to
`AskUserQuestion`:

```python
AskUserQuestion(questions=[ response["question"] ])
```

Take the user's selected label as the recipe name. Re-call `route.py infer`
with `--recipe <picked>` plus any other signals they'd already provided:

```bash
uv run scripts/route.py infer --transcript-file X --recipe <picked> [--lang Y --brand Z]
```

Loop back to step 3.

#### 3c. `action: "ask_questions"` (LOW confidence — gate fired)

The response contains `questions` (array of 2 AUQ payloads), `closest_recipe`,
`intent`, and `answer_map`. Dispatch:

1. Pass all questions in ONE AskUserQuestion call:
   ```python
   AskUserQuestion(questions=response["questions"])
   ```
2. Map the returned answer labels to internal values via `answer_map`:
   - Question text "…fit that shape?" → lookup in `answer_map["fit"]`
   - Question text "Do you expect to produce…" → lookup in `answer_map["frequency"]`
3. Call `route.py resolve`:
   ```bash
   uv run scripts/route.py resolve \
       --q1 <fit-value> --q2 <frequency-value> \
       --closest-recipe <closest> --intent <intent> \
       [--lang X --brand Y]
   ```
4. Parse JSON; dispatch again:
   - `action: "render"` → go to 3a
   - `action: "wait"` (log-and-wait) → show message; done
   - `action: "graduate"` → show message; done; graduation requires running
     the component/recipe CLI (future phase)

#### 3d. `action: "ask_intent"` (no intent or no recipe match)

Show `message` to user. Ask in plain text: "What would you like to render?"
Once they answer, use their response as transcript. Re-call `route.py infer`.

#### 3e. `action: "error"`

Show `message` to the user. Don't retry automatically. Common codes:
- `unknown_recipe` — the --recipe value doesn't exist; list available recipes
- `bad_resolve_args` — Q1/Q2 mismatch or missing justification; shouldn't
  happen if you followed 3c, but bubble up cleanly
- `internal_error` — unexpected exception; include the message verbatim

## Rules (non-negotiable)

- **Always show inferred signals** before rendering. User can say "no, use
  different brand/language" and we re-route.
- **No path bypasses the log.** `route.py resolve` emits `log_entry` dicts
  for every gate decision and writes them to `~/.katib/memory/gate-decisions.jsonl`
  via `core.request_log.log_gate_decision`. Context inferences go to
  `context-inferences.jsonl`; graduated recipe requests go to `recipe-requests.jsonl`.
  The agent does not need to echo anything — persistence is automatic.
- **No hand-edits to `capabilities.yaml`**, `component-audit.jsonl`, or any
  file under `components/` or `recipes/` during `/katib` execution.
  Governance is enforced by the CLI + build-time audit gate.
- **Explicit flags win over inferred signals.** Overrides are recorded in
  `reasons[]` for observability.
- **`/katib` with a fresh session and no prose** → go straight to step 3d
  (`ask_intent`).

## Component creation mode (`/katib component new`)

When the user invokes `/katib component new [name]` — or asks in plain
prose to "build a component", "create a [X] block that shows [Y]", or
describes a visual element not in `capabilities.yaml` — **pivot to the
builder playbook in `COMPONENT-BUILDER.md`**.

Quick summary of that flow (full detail in the guide):

1. **Interview (5 questions)** — name, tier, languages, inputs, closest
   exemplar. Use `AskUserQuestion` with all five in one call when possible.
2. **Scaffold** — `uv run scripts/component.py new <name> --tier <T> --namespace user --languages en,ar --description "..."`.
3. **Generate** — read the exemplar component's 4 files, mirror its
   patterns, fill in `component.yaml`, `en.html`, `ar.html`, `styles.css`,
   `README.md`.
4. **Validate** — `uv run scripts/component.py validate <name>`. Fix
   errors; trim unused tokens from `requires.tokens`.
5. **Preview** — `uv run scripts/component.py test <name>`. Renders
   standalone EN + AR PDFs. Show the user the paths and warning count.
6. **Iterate** — user feedback → edit → re-validate → re-preview.
7. **Register** — on approval, `uv run scripts/component.py register <name>`.
   Updates audit + `capabilities.yaml`.

**The builder is the lowest-risk way for users to extend Katib**.
Components land in `~/.katib/components/` (user tier), survive reinstall,
and can be shared with other users via the `katib pack` CLI (see below).

## Sharing mode (`katib pack export/import`)

Custom recipes / components / brand profiles can be packaged into a
`.katib-pack` tarball and imported into another install. The pack format
is **frozen at `pack_format: 1`** for the v1.x line — the schema is the
public contract.

When the user asks to "export this recipe", "share my component", or
"package this for someone else", run the appropriate `katib pack` command:

| Intent | Command |
|---|---|
| Pack a single component | `uv run scripts/pack.py export --component <name>` |
| Pack a single recipe | `uv run scripts/pack.py export --recipe <name>` |
| Pack a brand profile | `uv run scripts/pack.py export --brand <name>` |
| Pack a recipe + its custom-component deps | `uv run scripts/pack.py export --bundle <recipe>` |
| Bundle + include a brand | `uv run scripts/pack.py export --bundle <recipe> --include-brand <name>` |
| Inspect a `.katib-pack` (read-only) | `uv run scripts/pack.py inspect <pack>` |
| CI-grade verification | `uv run scripts/pack.py verify <pack>` |
| Install a pack into `~/.katib/` | `uv run scripts/pack.py import <pack>` |
| Dry-run an import (plan, no writes) | `uv run scripts/pack.py import <pack> --dry-run` |
| Force-overwrite a collision | `uv run scripts/pack.py import <pack> --force --justification "<why>"` |

**Defaults:**
- Author defaults to `git config user.name/email`. Override via `--author "Name <email>"`.
- Output dir defaults to `./dist/`. Override via `--out <path>`.
- All commands accept `--json` for machine-readable output.

**Refusal classes** (in order — each gates the next):
1. Pack opens cleanly (gzip + tar parseable, `pack.yaml` present)
2. Manifest schema-valid
3. `pack_format` supported by host
4. `content_hash` matches recompute
5. Per-artifact validators pass
6. Bundled-dep gate: `requires.bundled_components` exist on host, `requires.katib_min` ≤ host version
7. No collision (or `--force --justification`)

See `PACK-FORMAT.md` at the repo root for the full spec.

**Phase 6+ marketplace** (future): `katib pack install <author>/<name>`
will resolve against `katib.jneaimi.com` (or the URL in `KATIB_REGISTRY_URL`).
Same `.katib-pack` artifact format — the CLI gains a resolver, not a new
artifact format.

## Fresh-install sanity

On a brand-new install (`npx @jasemal/katib install`), the shipped recipes
are under `recipes/`. Run `/katib tutorial --lang en` to smoke-test. The
router will regenerate `capabilities.yaml` automatically if sources are
newer than the cached index.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ERROR: Component(s) present on disk without an audit entry` | A component was hand-added without going through `katib component new` | Either remove the component or add a bootstrap entry to `memory/component-audit.jsonl`. See `scripts/build.py:check_audit`. |
| `ERROR: required image input 'X' not supplied by recipe` | Recipe section expects an image slot that wasn't filled | Add the image spec under `inputs` with `{source, path}` (or `{source: gemini, prompt}`, etc.) |
| `gemini: GEMINI_API_KEY not set` | Recipe references `source: gemini` but env var missing | Set the key, OR switch the recipe's image to `source: user-file`/`inline-svg`, OR narrow the component's `sources_accepted` to exclude gemini |
| `recipe '<name>' not found. Tried: ...` | Recipe isn't present in either tier | The error names both paths checked — bundled `<skill>/recipes/<name>.yaml` and user `~/.katib/recipes/<name>.yaml`. Scaffold one with `uv run scripts/recipe.py new <name> --namespace user`. |
| `recipe '<name>' already exists in the bundled tier ... cannot shadow bundled recipes without --force` | User tried to scaffold a name that ships with the skill | Pick a different name, OR pass `--force --justification '<why>'` if the intent is to customize a bundled template (audited). |
| `component '<name>' not found. Tried: ...` | Component referenced by a recipe isn't in either tier | The error lists every tier × dir checked. Scaffold with `uv run scripts/component.py new <name> --tier section --namespace user`, or fix the typo in the recipe's `sections[].component`. |
| `component '<name>' already exists in the bundled tier ... User components cannot shadow bundled components without --force` | User tried to scaffold a name that ships with the skill | Pick a different name, OR pass `--force --justification '<why>'` to intentionally override a bundled component (audited). |

## Where user content lives

Katib separates **user content** from **bundled content** so `npx install` never
clobbers your work:

| Tier | Path | Source |
|---|---|---|
| Bundled recipes | `~/.claude/skills/katib/recipes/` | Ships with the skill |
| Bundled components | `~/.claude/skills/katib/components/` | Ships with the skill |
| User recipes | `~/.katib/recipes/` | Created by `katib recipe new` |
| User components | `~/.katib/components/` | Created by `katib component new --namespace user` |
| User brands | `~/.katib/brands/` | Your brand profiles + cover presets |
| Audit + gate logs | `~/.katib/memory/` | Graduation and governance state |

Env var overrides (for testing / isolation): `KATIB_RECIPES_DIR`,
`KATIB_COMPONENTS_DIR`, `KATIB_BRANDS_DIR`, `KATIB_MEMORY_DIR`.

When resolving a recipe or component name, the engine checks the user tier
first, then bundled — so a user override with the same name silently wins.
Scaffolding always writes to the user tier (for `--namespace user`) and
refuses to shadow a bundled name without `--force --justification '<why>'`.

## What this skill does NOT do

- Does not navigate, open, or list output files. PDFs land at
  `~/Documents/katib/<recipe>/<slug>/<name>.<lang>.pdf` (or
  `$KATIB_OUTPUT_ROOT`). Use your OS file explorer to view them.
- Does not depend on any other Claude Code skill. The decision gate,
  content lint, and context sensor are all self-contained Katib-native
  routines.
