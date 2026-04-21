# Katib — English Writing Rules

Voice, structure, and anti-slop guidance for EN content. Applies to all domains; domain-specific tuning goes in each template's inline annotations.

---

## Brand voice (EN)

Three qualities, never traded off:

- **Warm** — Connect before informing. Write for a person, not an audience segment.
- **Professional** — Clean grammar, confident claims, earned precision.
- **Visionary** — Forward-looking framing. Name a bigger picture without melodrama.

## Core rules

### 1. Lead with the point

No throat-clearing. No "In today's rapidly evolving landscape." Start with the specific:

> ✗ "In an era of unprecedented technological disruption, enterprises must adapt..."
> ✓ "Your sales team spent 4 hours last week on tasks an AI agent could do in 8 minutes."

### 2. Data over adjectives

Replace vague modifiers with numbers, names, or outcomes:

> ✗ "Significant cost reduction"
> ✓ "32% reduction in onboarding time (6 weeks → 4 weeks)"

> ✗ "Industry-leading platform"
> ✓ "Used by 3 of the UAE's top 5 logistics companies"

### 3. Cut hedges and intensifiers

Delete: `very, really, quite, rather, essentially, basically, actually, literally, frankly`. Every instance weakens the sentence around it.

### 4. Specific nouns beat abstract nouns

| Abstract | Concrete |
|---|---|
| "stakeholders" | "the procurement team" |
| "solutions" | "a document-generation API" |
| "leverage synergies" | delete the sentence |
| "operational efficiency" | "cut 3 manual steps" |

### 5. Vary sentence length

Two consecutive sentences of the same length feel flat. Three is a death march. Break a long sentence. Use a short one. Let the rhythm do some work.

### 6. Make people the subject

AI text defaults to inanimate subjects. Rewrite so humans do the action:

> ✗ "The platform enables teams to collaborate"
> ✓ "Your engineers and project managers work from the same live view"

### 7. No three-item lists as default padding

If three items naturally fit — use three. If you padded to reach three — use two.

### 8. End with momentum, not summary

Last sentence of a section: what's next, what's at stake, what to do. Not a recap.

### 9. Title register

Headlines use confident, elevated wording. No casual verbs in titles of formal documents. No filler nouns ("Overview", "Introduction to") — name the actual subject.

### 10. No AI tells

Banned phrases that signal LLM output:

- "delve into / dive deep into / unpack / explore"
- "it's worth noting that / it is important to note"
- "in conclusion / to summarize / in summary"
- "this isn't just X — it's Y"
- "a paradigm shift / a game-changer / a true revolution"
- "at the intersection of"
- "the beauty of this approach lies in"
- "robust, scalable, dynamic" (as a triple)
- "empower, leverage, unlock, harness" (as verbs — replace with specific actions)

## Doc-type-specific notes

### Proposal

- Open with the client's situation in one paragraph — no corporate preamble
- Front-load outcomes before method (what they get, then how)
- Numbered scope sections for easy reference during negotiation
- Every deliverable tied to a date and a price
- Close with next step (countersign, kickoff meeting, payment terms) — not a generic "we look forward to"

### One-Pager

- Hero number or hero claim in the top third
- Max 7 sections, each with a scannable label
- One call-to-action, visually anchored
- Keep total word count under 400

### Letter

- Salutation matches formality tier (Dear / To whom / Greetings)
- First paragraph states the reason for writing — no context flourish
- Body: 2-3 short paragraphs max
- Close with a specific next step or request
- Signature block includes title, organization, date, reference code

### Tutorial (How-to, Onboarding, Cheatsheet)

- Imperative voice: "Click Settings" not "You should click Settings"
- Numbered steps only (never bulleted for sequence-dependent instructions)
- Code blocks get a language hint (`bash`, `python`, `javascript`)
- Screenshots follow the step they illustrate, not before
- Use callouts for: prerequisites (before the steps), warnings (inline), pro-tips (inline), troubleshooting (end)

## Distillation workflow (when given raw material)

When the user hands over meeting notes, brain dump, or existing doc in a different format:

1. **Extract** every factual claim, number, date, name, action item
2. **Classify** each extract to the target template's sections
3. **Gap-check** — list what the template needs but the raw content doesn't have, as a compact table
4. **Ask once** with the gap table. Do not guess to fill gaps.

Example gap-check:

| Template needs | Found | Missing |
|---|---|---|
| 4 metric cards | "8 years", "50-person team" | 2 more quantifiable results |
| 3-5 core projects | 2 mentioned | at least 1 more with outcome |

Then proceed to filling.

## Anti-slop quality gate

After writing, score the content on 5 dimensions (1-10 each):

| Dimension | What it measures |
|---|---|
| **Directness** | No throat-clearing, no hedging, point-first |
| **Rhythm** | Sentence length variation, no monotone paragraphs |
| **Trust** | No hand-holding, no meta-commentary, no over-explaining |
| **Authenticity** | No banned phrases, no AI structural patterns, human subjects |
| **Density** | Every sentence adds information, specifics over vague claims |

**Threshold:** Total ≥ 35/50. If below, revise before delivering.

Score internally — don't show the user unless asked.
