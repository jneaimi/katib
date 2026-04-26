# Katib references — content quality gate

This directory holds katib's **self-contained** content-quality references.
Anyone authoring recipe or component content — especially Arabic — should
read the relevant file here before writing.

## What lives here

- **`writing.ar.md`** — Arabic-content quality gate: brand voice, MSA grammar
  checklist, semantic precision, the full 50+ pattern anti-slop catalog,
  recipe-family-specific conventions (formal, legal, financial, etc.), and
  the 5-dimension quality score (Directness / Rhythm / Trust / Authenticity /
  Density, must total ≥ 35/50). **Read before authoring any Arabic content
  for a recipe or component.**

- **`writing.en.md`** — English-content quality gate: brand voice, anti-slop
  rules (banned phrases, hedge cuts, "make people the subject"), recipe-family
  notes (proposals, tutorials, CV, NOC, invoice, white-paper, MoU, …), and
  the same 5-dimension ≥ 35/50 quality score.

## Relationship to `core/content_lint.py`

Two layers, both required:

| Layer | Lives in | What it catches |
|---|---|---|
| Mechanical | `core/content_lint.py` (run via `uv run scripts/lint.py` or imported into recipe-validation tests) | Banned openers, emphasis crutches, jargon inflation, untranslated English abbreviations, unqualified ambiguous tech terms, واو-chain runaways. Anything regex-detectable. |
| Human-judgement | The `writing.{lang}.md` files in this directory | Voice, rhythm, density, sentence-level specificity, recipe-family conventions, fact-integrity, the 5-dimension anti-slop score. |

The lint runs at recipe-validation time and blocks the obvious mistakes.
The writing references are what an author reads before — and after — drafting,
to catch the slop the regex layer can't see.

## Why these are part of katib v2

In v1 these references shipped inside the skill bundle. In v2 they were
briefly dropped, leaving authors dependent on the external `/arabic` Claude
Code skill — which is unavailable to npm-installed users and not part of
katib's public contract. They are restored here so katib v2 is again
self-sufficient for content quality, regardless of how the user installed it.
