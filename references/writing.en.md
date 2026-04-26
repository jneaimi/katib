# Katib — English Writing Rules

Voice, structure, and anti-slop guidance for EN content. Applies to every
recipe and component; recipe-specific tuning goes in each recipe's
`inputs_by_lang.en` defaults or in the relevant component's exemplar text.

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

## Recipe-specific notes

The notes below are organized by the recipe families that ship in v2 (see
`recipes/*.yaml`). Recipe families are named `<family>-<artifact>` —
e.g. `business-proposal-proposal`, `tutorial-how-to`, `personal-cv`. Apply the
notes for the family that matches the recipe you're authoring.

### Business proposal (proposal, one-pager, letter)

- Open with the client's situation in one paragraph — no corporate preamble
- Front-load outcomes before method (what they get, then how)
- Numbered scope sections for easy reference during negotiation
- Every deliverable tied to a date and a price
- Close with next step (countersign, kickoff meeting, payment terms) — not a generic "we look forward to"

**One-pager variant:**

- Hero number or hero claim in the top third
- Max 7 sections, each with a scannable label
- One call-to-action, visually anchored
- Keep total word count under 400

**Letter variant:**

- Salutation matches formality tier (Dear / To whom / Greetings)
- First paragraph states the reason for writing — no context flourish
- Body: 2-3 short paragraphs max
- Close with a specific next step or request
- Signature block includes title, organization, date, reference code

### Tutorial (how-to, onboarding, cheatsheet, handoff)

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

### Formal (NOC, authority-letter, government-letter, circular)

- **Third person** throughout the body. "The company confirms" — not "We confirm". Signature block is the place for individuals.
- **Date + reference code + subject line** are structural, not optional. Every formal letter carries at minimum: `Ref:`, `Date:`, subject, and "To Whom It May Concern" or addressed recipient.
- **NOC purpose must be specific.** "For visa application" is too vague. Write: "For visa application to [country] through [embassy/consulate], valid for the duration of the trip scheduled [date range]."
- Validity periods are written explicitly: "Valid for 30 days from date of issuance."
- **Authority letters scope must list acts, not verbs alone.** Not "Authorised to sign documents" — instead: "Authorised to sign employment contracts under AED 100,000 with suppliers in Abu Dhabi only."
- Circulars always specify an **effective date** and an **expiry / until-superseded clause.**
- No marketing language. No "we are pleased to" or "we are delighted to." Formal correspondence states.
- **Acronym conventions:** spell out on first use — "No-Objection Certificate (NOC)" — then use the acronym.

### Report (research, progress, annual, audit)

- **Informational register**, not persuasive. A report documents findings; a proposal sells them.
- Third person by default. "The audit team found" — not "we found". Exception: chairman's letter in annual reports is first-person.
- Every numeric claim ties to a source: footnote, table row, or appendix reference. No free-floating figures.
- **Tables for comparisons**, not prose. If the reader needs to compare three or more things, don't bury it in paragraphs.
- Executive summary is the report in 150 words. Treat it as the only thing a busy reader will see.
- Findings in audit reports are **observation → risk → evidence → recommendation** in that order. Never mix.
- Avoid recommending action verbs in research reports ("organizations should…"); reserve recommendations for audit and progress types.
- Arabic peers: keep tables LTR-numeric where numbers appear (use `direction: ltr` on `.num` cells). Don't translate acronyms like `AUD-001` — keep Latin for traceability.

### Academic (syllabus, assignment-brief, lecture-notes, research-proposal)

- **Measurable learning objectives.** Every objective starts with a verb from Bloom's upper tiers where possible — "analyze," "evaluate," "design" — not "understand" or "know." The objective names a behavior an instructor can observe and assess.
- **Syllabus is a contract.** Late policy, grade weights, and attendance expectations must be unambiguous. If a student appeals a grade in week 10, the syllabus is the document you both point at. Vague phrasing loses that appeal.
- **Assignment briefs name the rubric before the task.** Students write to the rubric; if the rubric shows up at the bottom, half the class misses it. Lead with weight and criteria, then the task.
- **Lecture notes are a handout, not a transcript.** Compress the lecture into the 5–7 claims that must survive the week. Margin notes (prerequisite, common mistake, next-lecture teaser) do more work than long body prose.
- **Research proposals commit.** Hedge-language is a tell that the writer does not yet know what they're proposing. Replace "this study aims to explore" with "this study will measure X in Y using Z." Reviewers reward specificity.
- **Gap section is the core of a literature review.** Three or four paragraphs of prior work are prologue; the gap paragraph is why the proposal deserves funding. Don't bury it.
- **Citations carry citation style from start to finish.** Pick APA / MLA / Chicago / IEEE once. Mixed styles look unprofessional and fail some committees.
- **Arabic academic convention:** numbered sections use Eastern-Arabic digits (١ ٢ ٣) in running text but keep equations, DOIs, ISBNs, and years LTR with Western digits via `direction: ltr`. Mixing both is expected — not a bug.

### Financial (invoice, quote, statement, summary)

- **UAE VAT tax invoice fields are non-negotiable.** Under Federal Decree-Law No. 8 of 2017, a compliant tax invoice must include the words "Tax Invoice", supplier name / address / TRN, customer name / address / TRN (if registered), sequential invoice number, invoice date, supply date (if different), item description, unit price, VAT rate and amount separately, and the total including VAT. If any field is missing, the invoice is not valid for input-VAT recovery — your client's accountant will reject it.
- **TRN = 15 digits**, always shown in Latin digits with `direction: ltr` even inside Arabic cells. Never render a TRN in Eastern-Arabic numerals — tax authority systems read Latin digits.
- **Currency and amounts are LTR**, regardless of language. `AED 17,600.00` reads the same in both directions. Force with `direction: ltr; unicode-bidi: embed` inside RTL table cells.
- **Amount in words goes below the total, not beside it.** It's a legal cross-check, not decoration. Write the full form ("UAE Dirhams Seventeen Thousand Six Hundred only") — avoid abbreviation.
- **Quote scope names inclusions AND exclusions.** The exclusions list prevents scope creep worth more than the quote itself. Name "travel," "third-party licences," "content not supplied by us." Explicit exclusions beat implicit assumptions.
- **Statements use ageing buckets, not a flat ledger.** Current / 1–30 / 31–60 / 61–90 / 90+ days. Colour buckets: green for current, amber for 30–60, red for 90+. The client's payables clerk needs to see the age at a glance — that's what triggers payment.
- **Financial summary — commit to a number in the commentary.** "Revenue grew" is filler. "Revenue grew 18% to AED 2.4M" is real. Management accounts are unaudited, so mark them clearly as such to avoid audit confusion later.
- **Round intentionally.** For summaries, one decimal place is usually enough. For invoices and statements, two decimal places always — tax authorities and reconciliation systems demand it.
- **Zero-rated vs exempt are different.** A zero-rated item (e.g., international transport, exported services) shows 0% VAT but still appears in VAT returns. An exempt item doesn't. Most UAE B2B invoices don't encounter exempts — when you do, label them so the client's accountant knows.

### Editorial (white-paper, article, op-ed, case-study)

- **Lead with the reader, not the topic.** Editorial documents compete for attention. The first 30 words decide whether someone keeps reading. Open with a scene, an anecdote, a striking number, or a claim — never with "In today's fast-paced world…" or any corporate preamble.
- **White papers commit to a thesis.** A paper that merely surveys a field is a report, not a white paper. Name your thesis in the executive summary, defend it across the body, and acknowledge its limits. Readers trust writers who stake out a position.
- **Articles earn quotes, not decorate with them.** A quote earns its place when it voices something you *cannot* say yourself — a primary source, a lived experience, an expert's precise formulation. Paraphraseable quotes add nothing.
- **Op-eds are opinion, not analysis.** Show your reasoning, but commit to a view. Hedge-language ("it could be argued that…") signals lack of conviction. Pick a position, steel-man the opposition, and defend the position anyway.
- **Case studies lead with outcome, not activity.** "We redesigned their onboarding" is weak. "Onboarding time dropped from 6 weeks to 4, saving AED 340K annually" is strong. The fact-box and result-hero are read before the prose — make them earn their space.
- **Drop caps are an editorial gesture, not a typo.** The large first letter signals "long-form, read slowly." Use them on white paper, article, op-ed; skip on case study (where the fact-box opens instead).
- **Pull quotes are editing, not decoration.** Choose one memorable line per section and float it. The reader scanning the page should be able to reconstruct the article's argument from pull quotes alone.
- **Footnotes carry weight in white papers, not op-eds.** White papers cite sources rigorously — readers check footnotes. Op-eds embed sources in running prose; a bristling footnote column reads as over-armouring.
- **Steel-man the opposition.** Articles and op-eds that only present supporting evidence feel propagandistic. Readers trust writers who engage the strongest counter-argument, not the weakest.

### Marketing-print (sell-sheet, product-brief, capability-statement, slide-deck)

- **Lead with the outcome, not the activity.** Sell-sheets and slide decks live or die on the first 5 seconds. "We help you reduce onboarding time" is weak. "Onboarding drops from 6 weeks to 4" is strong. The customer does not buy your features — they buy the change.
- **One claim per page.** A sell-sheet with three headlines has no headline. A slide with four competing points is a slide with zero memorable points. Pick the one thing; move the rest to supporting material.
- **Big numbers earn their size.** The value stripe, big-figure slide, and metric cards only work when the numbers are real, current, and specific. "Faster" is meaningless; "42% faster within 90 days" is decisive. If you can't name the source, the number is decoration.
- **Capability statements are gov/B2B procurement tools — format matters.** Four quick facts, clear competencies grid, past-performance table with client + scope + year, differentiators with proof, contact + TRN + license. If a procurement officer can't scan it in 30 seconds, it was written wrong.
- **Slide decks read from the back of the room.** If body copy goes below 16pt, rewrite. Six words per bullet, seven bullets per slide, whichever comes first. Slides are speaker aids — detailed arguments belong in the one-pager that precedes or follows them.
- **Section dividers are rest stops, not decoration.** Every 4–6 content slides, insert a coloured divider with part number and section heading. Audience attention resets; the slide count reflects narrative arcs, not just pages.
- **One CTA per artifact.** Whatever you ask the reader to do — book a call, reply to the email, approve the proposal — say it in one line, place it at the end, and repeat the contact details. If you ask for three things, you'll get zero.
- **Testimonials need specifics or they're filler.** "Great team to work with" adds nothing. "Cut our reporting cycle from a week to a day" is worth the column inches. If the quote could apply to any competitor, cut it.
- **Arabic slide-decks mirror everything.** Landscape A4 stays landscape, but section dividers flip (chapter number to the left, text to the right), phone numbers and emails go LTR inside RTL slides, page-counter stays Latin.

### Legal (service-agreement, MOU, NDA, engagement-letter)

- **Templates are not legal advice.** The non-negotiable top rule. Every legal artifact Katib produces carries a disclaimer strip directing parties to qualified counsel. Do not strip the disclaimer; adjust its wording only.
- **Define terms once; capitalise forever.** A term introduced in quotes with capitalisation ("Services", "Confidential Information", "Effective Date") is a defined term. Use the exact capitalised form everywhere else in the document. Mixed case — "services" later — signals sloppy drafting and opens interpretation disputes.
- **Clause numbering is sequential and nested.** `1.`, `1.1`, `1.2.1`. Parties reference clauses by number during negotiation; renumbering after an edit is a discipline, not an inconvenience. Katib's `clause-list` component auto-numbers — let it do the work.
- **Every agreement names a governing law and a forum.** Omitting this is a common mistake that throws disputes into jurisdictional limbo. UAE agreements typically pick: (1) courts of the emirate, (2) DIFC or ADGM Courts (English-law common-law forums), or (3) DIAC arbitration seated in Dubai. Pick one, delete the alternatives.
- **"WHEREAS" is not decoration.** Recitals frame the commercial context — the "Now, therefore" clause transitions from context to operative terms. Courts read recitals for interpretation when clauses are ambiguous. Write them as short, declarative sentences — not stories.
- **MOUs must signal binding versus non-binding clauses clearly.** Parties often treat the whole MOU as non-binding except for three: confidentiality, governing law, and costs. Flag each binding clause inline — Katib's MOU recipe uses `(binding)` annotations next to those headings.
- **Signature blocks earn the page break.** Never split a signature block across pages. Use `page-break-before` when necessary. Both parties sign on the same sheet or on counterpart sheets — never a lone signature on an orphan page.
- **Mutual vs one-way NDAs.** Mutual NDAs use "the Parties", "each Party", "the Receiving Party" and "the Disclosing Party" as interchangeable roles. One-way NDAs name one party as Discloser and one as Recipient; remove the reciprocal phrasing. Choose up front; do not mix.
- **Fees and caps use numbers AND words.** "one hundred twenty thousand (120,000)" survives OCR errors, faxes, and photocopied documents. The same applies to term lengths: "thirty (30) days".
- **Arabic legal phrasing has conventions.** `حيث إنّ` (WHEREAS) opens recitals. `عليه، وبناءً على التعهّدات المتبادلة` (Now, therefore, in consideration of the mutual covenants) bridges to operative clauses. `يُقرّ الطرفان` (the Parties acknowledge) opens formal declarations. Use the full legal Arabic — خطاب تعاقد — not colloquial phrasing.

## Distillation workflow (when given raw material)

When the user hands over meeting notes, brain dump, or existing doc in a different format:

1. **Extract** every factual claim, number, date, name, action item
2. **Classify** each extract to the target recipe's sections
3. **Gap-check** — list what the recipe needs but the raw content doesn't have, as a compact table
4. **Ask once** with the gap table. Do not guess to fill gaps.

Example gap-check:

| Recipe needs | Found | Missing |
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

`core/content_lint.py` (run via `uv run scripts/lint.py` or imported into
recipe-validation tests) catches the mechanical layer of these rules
automatically — banned openers, emphasis crutches, jargon inflation,
untranslated abbreviations. The 5-dimension score above is the human-judgement
layer that lives on top.
