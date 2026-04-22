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

### Personal (CV, cover-letter, bio)

- **CV bullets use STAR/CAR structure.** Situation/Context → Action → Result with a number. "Built agent" is weak. "Built bilingual support agent that cut handle time 38% across 12K monthly tickets" is strong.
- **Verbs lead.** Every experience bullet starts with a verb. No "Was responsible for" — say "Owned" or "Led."
- **Numbers > adjectives.** "Significantly improved" is filler. "Reduced 6-week onboarding to 4 weeks" is real.
- **One line per achievement.** If it wraps to three lines, cut words — not content.
- **Cover letters ≤ 3 paragraphs.** Recruiter scan time is under 90 seconds.
- **GCC CV fields** that generic tools skip: nationality, visa status, date of birth, languages with proficiency. Include the photo slot — it's conventional in the region, not optional.
- **Bio variants matter.** Ship three lengths (1-sentence, 2–3 sentence, full paragraph) in the same doc — speakers and conference programs ask for each.

### Formal (NOC, government-letter, circular, authority-letter)

- **Third person** throughout the body. "The company confirms" — not "We confirm". Signature block is the place for individuals.
- **Date + reference code + subject line** are structural, not optional. Every formal letter carries at minimum: `Ref:`, `Date:`, subject, and "To Whom It May Concern" or addressed recipient.
- **NOC purpose must be specific.** "For visa application" is too vague. Write: "For visa application to [country] through [embassy/consulate], valid for the duration of the trip scheduled [date range]."
- Validity periods are written explicitly: "Valid for 30 days from date of issuance."
- **Authority letters scope must list acts, not verbs alone.** Not "Authorised to sign documents" — instead: "Authorised to sign employment contracts under AED 100,000 with suppliers in Abu Dhabi only."
- Circulars always specify an **effective date** and an **expiry / until-superseded clause.**
- No marketing language. No "we are pleased to" or "we are delighted to." Formal correspondence states.
- **Acronym conventions:** spell out on first use — "No-Objection Certificate (NOC)" — then use the acronym.

### Report (Research, Progress, Annual, Audit)

- **Informational register**, not persuasive. A report documents findings; a proposal sells them.
- Third person by default. "The audit team found" — not "we found". Exception: chairman's letter in annual reports is first-person.
- Every numeric claim ties to a source: footnote, table row, or appendix reference. No free-floating figures.
- **Tables for comparisons**, not prose. If the reader needs to compare three or more things, don't bury it in paragraphs.
- Executive summary is the report in 150 words. Treat it as the only thing a busy reader will see.
- Findings in audit reports are **observation → risk → evidence → recommendation** in that order. Never mix.
- Avoid recommending action verbs in research reports ("organizations should…"); reserve recommendations for audit and progress types.
- Arabic peers: keep tables LTR-numeric where numbers appear (use `direction: ltr` on `.num` cells). Don't translate acronyms like `AUD-001` — keep Latin for traceability.

### Academic (Syllabus, Assignment-brief, Lecture-notes, Research-proposal)

- **Measurable learning objectives.** Every objective starts with a verb from Bloom's upper tiers where possible — "analyze," "evaluate," "design" — not "understand" or "know." The objective names a behavior an instructor can observe and assess.
- **Syllabus is a contract.** Late policy, grade weights, and attendance expectations must be unambiguous. If a student appeals a grade in week 10, the syllabus is the document you both point at. Vague phrasing loses that appeal.
- **Assignment briefs name the rubric before the task.** Students write to the rubric; if the rubric shows up at the bottom, half the class misses it. Lead with weight and criteria, then the task.
- **Lecture notes are a handout, not a transcript.** Compress the lecture into the 5–7 claims that must survive the week. Margin notes (prerequisite, common mistake, next-lecture teaser) do more work than long body prose.
- **Research proposals commit.** Hedge-language is a tell that the writer does not yet know what they're proposing. Replace "this study aims to explore" with "this study will measure X in Y using Z." Reviewers reward specificity.
- **Gap section is the core of a literature review.** Three or four paragraphs of prior work are prologue; the gap paragraph is why the proposal deserves funding. Don't bury it.
- **Citations carry citation style from start to finish.** Pick APA / MLA / Chicago / IEEE once. Mixed styles look unprofessional and fail some committees.
- **Arabic academic convention:** numbered sections use Eastern-Arabic digits (١ ٢ ٣) in running text but keep equations, DOIs, ISBNs, and years LTR with Western digits via `direction: ltr`. Mixing both is expected — not a bug.

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
