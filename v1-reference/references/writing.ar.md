# Katib — Arabic Writing Rules

MSA grammar, brand voice, anti-slop, and quality-gate workflow for Arabic
content across all domains. **Self-contained** — Katib no longer depends on
the `/arabic` skill for Arabic quality. This file is the authoritative source.

Last revised: 2026-04-22 (v0.19.0). History: originally a snapshot from
`/arabic`; since v0.19.0, independent.

---

## Brand voice (AR)

Three qualities, mirrored from EN:

- **دافئ (Warm)** — Connect before informing. Use `أنت/كم` directly. Speak to a person, not an institution.
- **مهني (Professional)** — Clean MSA grammar, confident tone, structured hierarchy.
- **رؤيوي (Visionary)** — Forward-looking without melodrama. Use `هذا العقد / المرحلة القادمة` sparingly.

**Audience:** GCC (خليج)، with UAE focus. Default dialect mix:
- Formal (proposal, letter, government): pure MSA
- Semi-formal (tutorial, article): MSA with occasional خليجي tone
- Informal (personal message): MSA + خليجي heavy

## Core rules

### 1. Lead with the specific

No filler openers. Cut these:

- `في عالمنا اليوم / في عصرنا هذا`
- `نعيش في زمن / من المعلوم أن`
- `لا شك أن / من الضروري الإشارة إلى`

Start with the subject directly.

### 2. Qualify tech terms that have non-tech meanings

| Arabic term | Default meaning | In tech context, use |
|---|---|---|
| وكيل / وكلاء | business agent, broker | الوكيل الذكي / الوكلاء الأذكياء |
| إطار | picture frame | الإطار التقني |
| نموذج | form to fill | النموذج اللغوي |
| تطبيق | application of a principle | التطبيق (software) — context usually disambiguates; qualify if ambiguous |

**Rule:** after writing or reviewing, mental find-all for each ambiguous term. Qualify every unqualified instance.

### 3. Translate abbreviations on first mention

First mention: Arabic meaning + (English abbreviation).
Subsequent: English abbreviation alone is fine.

> ✓ "بروتوكول سياق النموذج (MCP) يتيح..."
> ✗ "MCP يتيح..." (on first mention)

Applies to **every English abbreviation without exception** — including common ones like `B2B`, `CEO`, `DevSecOps`, `MFA`, `2FA`, `CI/CD`, `PDPL`, `GDPR`, `SOC 2`. Never drop them in raw even if you assume the reader knows them.

### 4. No literal English idioms

Find the Arabic equivalent, not the word-for-word translation:

| English idiom | Bad (literal) | Good (Arabic equivalent) |
|---|---|---|
| "alphabet soup" | حساء الحروف | فوضى الاختصارات |
| "low-hanging fruit" | الثمار الدانية | الحلول السهلة المتاحة |
| "moving the needle" | تحريك الإبرة | إحداث فرق ملموس |

### 5. No English-style compound adjectives

| English pattern | Bad Arabic | Good Arabic |
|---|---|---|
| "enterprise AI" | الذكاء الاصطناعي المؤسسي (reads "institutional") | الذكاء الاصطناعي للمؤسسات |
| "senior engineer" | مهندس كبير (reads "big engineer") | مهندس أول / مهندس رئيسي |
| "agentic AI" | الذكاء الاصطناعي الوكيل | الوكلاء الأذكياء / الذكاء الاصطناعي القائم على الوكلاء |

## MSA grammar checklist

Check every instance of these in professional-register content (formality ≥ 3).

### 1. إذا الشرطية + جملة اسمية

- ✗ "إذا مؤسستك تتعامل..."
- ✓ "إذا **كانت** مؤسستك تتعامل..."

Rule: `إذا` must be followed by a verb. Use `كان / كانت / كانوا` to bridge to nominal predicates.

### 2. بسبب / نتيجة + فعل

- ✗ "بسبب الوكيل نفّذ عملية..."
- ✓ "بسبب الوكيل **الذي** نفّذ عملية..."

Rule: `بسبب / نتيجة` take a noun; use `الذي / التي` to link a verb clause.

### 3. ضمير جمع غير العاقل

- ✗ "الأنظمة... تتضاعف في**هم**"
- ✓ Restructure: "تتضاعف هذه الأنظمة"

Rule: When the pronoun's referent is ambiguous, restructure — don't guess gender/number.

### 4. التوازي في السلاسل

- ✗ "إذا لم تكن بياناتك جاهزة، أو فريقك غير مدرّب" (mixed verbal + nominal)
- ✓ "إذا لم تكن بياناتك جاهزة، أو **لم يكن** فريقك **مدرّباً**"

Rule: All items in a conditional chain or list follow the same grammatical pattern.

### 5. ما التعجبية vs ما الاستفهامية

- ✗ (as question) "ما أكثر سير عمل تكلفةً؟"
- ✓ "**أيّ** سير عمل هو الأكثر تكلفةً؟"

Rule: Use `أيّ` for "which/what". Reserve `ما أفعل` for exclamation.

### 6. العدد والمعدود (3-10) في الجداول

- ✗ "مهندس أو اثنين ذكاء اصطناعي"
- ✓ "مهندس ذكاء اصطناعي واحد أو اثنان"

Rule: Numbers 3-10 take opposite gender of counted noun. Dual (اثنان / اثنتان) must match case.

### 7. الضمائر المعلّقة

- ✗ "أكثرها تكلفةً وأوضح**ه** تحديداً"
- ✓ "**الأكثر** تكلفةً **والأوضح** تحديداً"

Rule: Every pronoun suffix has a clear referent. When in doubt, use the full noun.

---

## Anti-slop catalog (full, self-contained)

The full 50+-pattern catalog. Every Arabic render must pass these checks.

### 1. Throat-clearing openers (افتتاحيات حشوية)

Cut these. Start with the actual point.

| Pattern (Arabic) | English equivalent | Why it's slop |
|---|---|---|
| في عالمنا اليوم | In today's world | Every AI article starts this way |
| في ظل التطورات المتسارعة | Amid rapid developments | Vague, adds nothing |
| لا يخفى على أحد أن | It's no secret that | If it's not a secret, just say it |
| مما لا شك فيه أن | There's no doubt that | If there's no doubt, the statement doesn't need this prefix |
| من الجدير بالذكر أن | It's worth mentioning that | If it's worth mentioning, just mention it |
| تجدر الإشارة إلى أن | It should be noted that | Same — just note it |
| في هذا السياق | In this context | Filler transition |
| في هذا الإطار | Within this framework | Filler transition |
| على صعيد آخر | On another level | Usually not a genuine contrast |
| من ناحية أخرى | On the other hand | Often filler, not real contrast |
| يمكن القول إن | It can be said that | Hedging — just say it |
| بشكل عام | In general | Vague qualifier |
| في الحقيقة | In reality | If it's reality, just state it |
| كما هو معروف | As is known | If it's known, skip it |
| من المعلوم أن | It is known that | Same |
| لا بد من الإشارة إلى | It must be pointed out that | Just point it out |
| بطبيعة الحال | Naturally | Filler softener |
| في واقع الأمر | As a matter of fact | Throat-clearing |
| دعونا نتفق أن | Let's agree that | Presumptuous filler |
| ليس من المبالغة القول | It's not an exaggeration to say | Then just say it |

**Instead:** start with the claim, the data, or the action. The reader decides if it's worth noting.

### 2. Emphasis crutches (عكازات التأكيد)

These try to make weak statements sound strong. Cut them, write a stronger statement.

| Pattern | Why it fails |
|---|---|
| وهذا ما يجعل الأمر بالغ الأهمية | Tells importance instead of showing it |
| وهنا تكمن المفارقة | Announces the insight instead of letting the reader see it |
| وهذا ليس مبالغة | Defensive — the statement should stand on its own |
| النقطة الجوهرية هنا | Signposting — let the point speak |
| الأمر الأكثر إثارة هو | Hype before substance |
| وهذا بالضبط ما نحتاجه | Tells the reader what to think |
| دعوني أكون صريحاً | If you have to announce honesty, the rest sounds dishonest |
| الحقيقة المُرّة هي | Melodramatic framing |
| وهذا يعني شيئاً واحداً | Dramatic buildup for a plain statement |
| السؤال الحقيقي هو | Implies previous content was fake questions |

### 3. Business/tech jargon inflation (تضخم المصطلحات)

| Inflated Arabic | Plain alternative |
|---|---|
| تحقيق التحول الرقمي الشامل | رقمنة العمليات |
| تعزيز منظومة الابتكار | تحسين طريقة العمل |
| الاستفادة من البيانات الضخمة | استخدام البيانات |
| بناء قدرات مستدامة | تدريب الفريق |
| تمكين المؤسسات من | مساعدة المؤسسات على |
| إعادة هيكلة العمليات التشغيلية | تبسيط العمليات |
| تبني نهج شمولي | النظر للصورة الكاملة |
| رفع مستوى الكفاءة التشغيلية | العمل بشكل أسرع |
| إطلاق العنان لـ | استخدام / تفعيل |
| تسخير قوة | استخدام |
| الارتقاء بتجربة | تحسين تجربة |
| استشراف المستقبل | التخطيط |
| تحقيق قفزة نوعية | تحسين كبير |
| نقلة نوعية | تغيير مهم |

### 4. Structural anti-patterns (أنماط هيكلية متكررة)

**4a. Binary contrast (ليس... بل...)** — AI Arabic loves this. Vary structure.

Patterns to watch:
- `ليس X فحسب، بل Y أيضاً`
- `لا يتعلق الأمر بـ X، بل بـ Y`
- `المسألة ليست X، المسألة Y`
- `X ليس Y. إنه Z.`

**Instead:** state what it IS. Skip what it isn't.

**4b. Rhetorical question stacking** — one rhetorical question per piece, max. Use it to open, not to pad.

Patterns to watch:
- `ماذا لو كان بإمكاننا...؟`
- `هل تساءلت يوماً...؟`
- `ما الذي يمنعنا من...؟`
- `أليس هذا ما نحتاجه...؟`

**4c. False agency (الفاعلية الزائفة)** — inanimate subjects doing human actions.

| Slop | Fix |
|---|---|
| يفرض هذا التحول على المؤسسات | المؤسسات تواجه ضرورة |
| تتيح هذه التقنية فرصة | يمكن للفِرق باستخدام هذه التقنية |
| يبرز الذكاء الاصطناعي كحل | يستخدم المهندسون الذكاء الاصطناعي لـ |
| يعيد تعريف مفهوم | غيّر طريقة تفكيرنا في |
| تفتح البيانات آفاقاً | يستطيع المحللون بالبيانات |
| يقود التحول نحو | الفِرق تنتقل إلى |
| تشهد المنطقة تحولاً | الشركات في المنطقة تتغير |

**Rule:** find the human. Make them the subject.

**4d. List cadence (إيقاع القوائم)**
- Three-item lists are an AI signature. Use two, or four+.
- `أولاً... ثانياً... ثالثاً...` with exactly three points — vary the count.
- Numbered lists where bullets would do. Reserve numbers for sequential steps.

**4e. Paragraph openers** — avoid starting consecutive paragraphs with `ومن / كما أن / بالإضافة إلى / علاوة على ذلك / من جهة أخرى`. These create monotonous additive rhythm. Vary transitions or eliminate them — let logic connect paragraphs.

### 5. Rhythm rules (قواعد الإيقاع)

- **Sentence length variation:** mix short (5-8 words), medium (12-18), long (20-30). Three consecutive same-length sentences = monotone. After long, follow with short.
- **Conjunction chaining (سلسلة الواو):** max two `واو` per sentence. Replace third `واو` with a period. Use `كما، بينما، لكن، غير أن` for variety.
- **No em-dash abuse:** overuse of `—` or `ـ` as parenthetical insertions. One per paragraph max. Use parentheses or restructure.
- **Paragraph length:** digital content 2-3 sentences, article 3-4. One-sentence paragraphs are powerful — one per section max. If 4+ sentences, split.

### 6. Trust the reader (ثق بالقارئ)

**6a. Cut hedging**

| Hedging | Action |
|---|---|
| قد يكون من المفيد | Delete — just present the useful thing |
| ربما يجدر بنا | Delete — just do it |
| من المحتمل أن | Keep ONLY if genuine uncertainty exists |
| يمكننا القول إن | Delete — just say it |
| في رأيي المتواضع | Delete — own your opinion |

**6b. Cut hand-holding**

| Hand-holding | Action |
|---|---|
| كما ذكرنا سابقاً | Delete — the reader remembers |
| دعونا نستعرض | Delete — just present |
| من المهم أن نفهم أن | Delete — just explain |
| يجب أن نتذكر أن | Delete — just state |
| لنأخذ خطوة إلى الوراء | Delete — reframe directly |

**6c. Cut meta-commentary**

| Meta-commentary | Action |
|---|---|
| في هذا المقال سنتناول | Delete — the reader sees what it covers |
| كما سنرى لاحقاً | Delete — they'll see it when they get there |
| خلاصة القول | Delete or replace with the actual conclusion |
| في الختام | Delete — just close |
| دعونا نلخّص | Delete — the reader doesn't need a warning |

### 7. Vague declaratives (تصريحات مبهمة)

These sound meaningful but say nothing. Replace with specifics.

| Vague | Instead |
|---|---|
| هذا يغير كل شيء | Say WHAT changed and HOW |
| النتائج مذهلة | Give the actual numbers |
| الفرص لا حصر لها | Name three specific opportunities |
| المستقبل واعد | Describe what will happen concretely |
| التأثير كبير | Quantify the impact |
| الإمكانيات هائلة | List what's actually possible |
| العالم يتغير بسرعة | Say what changed, when, by how much |

### 8. Before/after examples (أمثلة: قبل وبعد)

**Example 1 — Throat-clearing + binary contrast**

Before:
> في عالمنا اليوم المتسارع، لا يخفى على أحد أن الذكاء الاصطناعي يغير كل شيء. الأمر لا يتعلق بالتقنية فحسب، بل يتعلق بإعادة تعريف مفهوم العمل بأكمله.

After:
> الذكاء الاصطناعي يختصر عملية مراجعة العقود من ثلاثة أيام إلى ساعتين. فِرق المشتريات في الخليج بدأت تعتمد عليه فعلاً.

**Why:** cut two throat-clearers, replaced vague "changes everything" with specific claim, killed the binary contrast, added real subject (procurement teams).

**Example 2 — False agency + jargon**

Before:
> تتيح هذه التقنية إطلاق العنان لإمكانيات غير مسبوقة في تحقيق التحول الرقمي الشامل، مما يمكّن المؤسسات من الارتقاء بتجربة العملاء.

After:
> فِرق خدمة العملاء تستخدم هذه الأداة للرد على الاستفسارات في دقيقتين بدل عشرين.

**Why:** found the human, replaced jargon with concrete metric, one sentence instead of a clause chain.

**Example 3 — Emphasis crutch + hand-holding**

Before:
> وهنا تكمن المفارقة. من المهم أن نفهم أن الوكلاء الأذكياء ليسوا بديلاً عن البشر. دعونا نكون صريحين: النقطة الجوهرية هنا هي أن التعاون بين الإنسان والآلة هو المستقبل.

After:
> الوكلاء الأذكياء يتولون المهام الروتينية. المهندسون يركزون على القرارات. كلاهما يعمل أفضل مع الآخر.

**Why:** three emphasis crutches + two hand-holding phrases removed. Same idea in three short, concrete sentences.

**Example 4 — Rhetorical stacking + vague declaratives**

Before:
> هل تساءلت يوماً عن مستقبل العمل؟ ماذا لو كان بإمكاننا أتمتة كل شيء؟ الفرص لا حصر لها، والمستقبل واعد، والتأثير سيكون كبيراً.

After:
> شركة أرامكس أتمتت 40% من عمليات التوصيل في 2025. وفّرت 12 مليون دولار. هذا ما تبدو عليه الأتمتة عندما تُنفَّذ.

**Why:** three rhetorical questions replaced with zero. Three vague declaratives replaced with three specifics. The reader sees proof instead of being told to imagine it.

**Example 5 — Conjunction chaining + monotone rhythm**

Before:
> الذكاء الاصطناعي يحلل البيانات ويستخرج الأنماط ويقدم التوصيات ويساعد في اتخاذ القرارات ويوفر الوقت والجهد.

After:
> الذكاء الاصطناعي يحلل البيانات ويستخرج الأنماط. النتيجة: توصيات جاهزة للتنفيذ بدل تقارير تحتاج ساعات لقراءتها.

**Why:** broke the five-item `واو` chain, split into two sentences of different lengths, added concrete outcome.

---

## Fact integrity (إلتزام الدقة)

**Non-negotiable for every Arabic render.** The risk of hallucinated attributions in Arabic is especially high because back-translation from Arabic to verify a quote is slow and easy to skip.

### Rules

1. **No fabricated quotes.** Never attribute a statement to a named person unless you have a verifiable source. If a blockquote would strengthen the piece and you don't have a real one, **delete the blockquote** — don't manufacture a quote "in the style of" someone.
2. **No fabricated statistics.** Every number in the body needs a footnote, a linked source, or the phrase "بحسب تقديرات الفريق" (per team estimate). Generic assertions like "تشير الدراسات" (studies show) with no citation are slop.
3. **No invented institutional affiliations.** "مؤتمر RSA 2023" or "تقرير IBM لعام 2024" are specific claims. If you can't verify the event happened or the report contained the figure, don't cite it.
4. **When in doubt, pull out.** A clean piece with fewer citations beats an authoritative-sounding piece with fabricated ones. The first won't embarrass anyone later.

### Verification tiers

| Need | Acceptable sources |
|---|---|
| Specific quote + attribution | Direct URL to the source (speech transcript, published interview, social post) |
| Industry statistic | Named report + year + page or URL |
| Government/regulatory claim | Official government document URL |
| General claim | Can be unsourced if it's common knowledge at the target audience's level |

**Before committing a render:** grep the content for blockquotes and numeric claims. For each, confirm the source. If any can't be sourced, strip or rephrase.

---

## Semantic precision (الدقّة الدلالية)

### 1. Don't use nouns as adjectives for tech terms
- ✗ "الذكاء الاصطناعي الوكيل" (nouns don't freely become adjectives)
- ✓ "الوكلاء الأذكياء" or "الذكاء الاصطناعي القائم على الوكلاء"

### 2. Watch for false friends / near-synonyms

| Wrong word | Actual meaning | Intended | Correct |
|---|---|---|---|
| متبادلة | mutual/reciprocal | interchangeable | قابلة للتبادل |
| البياني | graphical/chart | data-related | البيانات (use إضافة) |
| المؤسسي | institutional | enterprise | للمؤسسات (use لام الجر) |

### 3. Avoid tautological constructions
- ✗ "تشير **إشارة** الوكيل" (the signal signals — shared root)
- ✓ "يدل **إعلان** الوكيل" (the announcement indicates)

### 4. Modifier attachment ambiguity
- ✗ "بروتوكول سياق النموذج المُدار MCP" (المُدار could modify النموذج or البروتوكول)
- ✓ "بروتوكول سياق النموذج (MCP) بإدارة Google"

### 5. Time expressions — don't mix systems
- ✗ "الـ 18 شهر القادمة" (Western numeral + Arabic grammar)
- ✓ "العام ونصف القادم" or "الثمانية عشر شهراً القادمة"

---

## Doc-type notes

### Formal proposal (AR)

- Open: `السلام عليكم ورحمة الله وبركاته، وبعد،`
- Use Arabic-Indic numerals in body (`٢٦`), Western in tables (for column alignment)
- Reference codes stay in Latin (`TITS-TP-2026-001`)
- Close: `تفضلوا بقبول فائق الاحترام والتقدير.`

### Tutorial / How-to (AR)

- Imperative voice: `اضغط على الإعدادات` not `يجب عليك الضغط`
- Step numbers use Western digits (Arabic-Indic in step bodies is distracting for scannability)
- Technical terms stay Latin inside `<span dir="ltr">`; Arabic translation in parentheses on first mention
- Screenshots don't need captions translated — screenshots are images

### Letter (AR)

- Opening formula: `سعادة/معالي + name + المحترم`
- Body: 2-3 paragraphs, one idea each
- Use `ب/ف` for transitions, not `ثم` repeated
- Close with specific next step: date, action, or reference

### Personal (CV / cover-letter / bio — AR)

- **السيرة الذاتية العربية ليست ترجمة.** هي سجلّ بسجلّ مستقل، قد يختلف في الترتيب والتوكيد عن الإنجليزية.
- **نقاط الخبرة تبدأ بفعل ماضٍ.** «قاد»، «بنى»، «خفّض»، «أطلق». تجنّب المصدر («قيادة فريق...») — الفعل أقوى.
- **الأرقام قبل الصفات.** «خفّض زمن التأهيل من ٦ أسابيع إلى ٤» أقوى من «حسّن كفاءة الفريق».
- **الحقول الخليجية المهمّة:** الجنسية، حالة الإقامة (إقامة عمل / إقامة شخصية / مواطن)، تاريخ الميلاد، اللغات بمستوياتها. الصورة الشخصية جزء من التقليد — لا تحذفها.
- **الأسماء الأجنبية** (شركات، جامعات، تقنيات) تُكتب بالأحرف اللاتينية داخل `<span dir="ltr">` — لا تحرّف «Google» إلى «جوجل» في السيرة الذاتية.
- **التواريخ تبقى بالأحرف اللاتينية** في السيرة الذاتية (2020-01 — 2024-06) لقراءة دقيقة عبر اللغتين.
- **خطاب التغطية**: ٣ فقرات فقط. استعمل «سعادتكم المحترم» في المخاطبة، وانهِ بـ «وتفضّلوا بقبول فائق الاحترام والتقدير،،».
- **النبذة التعريفية**: اكتب ثلاث صيغ في الوثيقة نفسها (قصيرة سطر واحد، متوسّطة جملتان، طويلة فقرة كاملة) — يطلبها منظّمو المؤتمرات بأطوال مختلفة.

### Formal (NOC / government-letter / circular / authority-letter — AR)

- **الافتتاح الإسلامي موجود في السياقات الحكومية:** ابدأ بـ `السلام عليكم ورحمة الله وبركاته` قبل الجملة الأولى في الخطابات الحكومية. شهادات عدم الممانعة والتعاميم أخفّ — `إلى مَن يهمّه الأمر` أو الترويسة كافية.
- **الألقاب الوظيفية إلزامية:** `سعادة/ معالي/ المهندس/ الدكتور/ السيّد/ السيّدة` + الاسم + `المحترم/ المحترمة`. الحذف علامة على عدم الاحتراف.
- **صيغة الغائب (الموضوعية):** `تُفيد الشركة` لا `نُفيدكم`. الاستثناء الوحيد: الصيغة الختامية `ونحن على أتمّ الاستعداد...` (الجمع الرسمي مقبول في الخاتمة).
- **الختام** إلزامي: `وتفضّلوا بقبول فائق الاحترام والتقدير،،`. لا تستبدله بـ `مع تحياتي` أو ما شابه في الخطاب الرسمي.
- **شهادة عدم الممانعة:**
  - العنوان يُكتب: `شهادة عدم ممانعة` (وليس "شهادة بعدم ممانعة" أو "عدم الممانعة")
  - الغرض يجب أن يكون محدَّداً: `لاستخراج تأشيرة لدولة [...] من سفارة/قنصلية [...]` — لا `لغرض السفر` فقط.
- **التعاميم** تحدّد دائماً: `إلى / من / نسخة إلى`، الموضوع، الإجراء المطلوب، وتاريخ السريان.
- **خطاب التفويض** يذكر الأفعال بدقّة، لا الصلاحيات العامّة: `مُفوَّض بالتوقيع على عقود العمل التي تقلّ عن [...] درهم` — وليس `مفوَّض بالتوقيع`.
- **الأرقام واللغات المختلطة:** أرقام الهويّة الإماراتية وجوازات السفر تُكتب بالأحرف اللاتينية (LTR) داخل سياق عربي (RTL) باستخدام `direction: ltr; unicode-bidi: embed;` على الخلية أو العنصر.
- **التاريخ:** استعمل الصيغة الميلادية YYYY-MM-DD في الخطابات الرسمية للجهات الحكومية. الصيغة الهجرية اختيارية كمرجع ثانوي.

### Report (research / progress / annual / audit — AR)

- **صيغة معلوماتية**، ليست إقناعية. التقرير يوثّق الاكتشافات؛ العرض يبيعها.
- استخدم الصيغة الموضوعية: `وجد فريق التدقيق` لا `وجدنا`. الاستثناء: كلمة رئيس المجلس في التقرير السنوي بصيغة المتكلّم.
- كل رقم يستند إلى مصدر: حاشية، صف جدول، أو مرجع ملحق. لا أرقام طليقة.
- **الجداول للمقارنات**، لا السرد. إن احتاج القارئ مقارنة ثلاث عناصر فأكثر، لا تدفنها في فقرات.
- الملخّص التنفيذي = التقرير في ١٥٠ كلمة. عامله كأنّه الشيء الوحيد الذي سيقرأه صاحب القرار.
- ملاحظات التدقيق تُرتَّب: **الملاحظة ← الخطر ← الدليل ← التوصية**. لا تخلط.
- احتفظ بالأرقام المرجعية بالأحرف اللاتينية (`AUD-001`) — لا تترجمها، فالتتبّع عبر اللغتين يعتمد عليها.
- الأرقام داخل الجداول تستحق `direction: ltr` على خلية `.num` لقراءة سليمة يميناً إلى يساراً للرقم نفسه.

### Academic (syllabus / assignment-brief / lecture-notes / research-proposal — AR)

- **مخرجات تعلّم قابلة للقياس.** ابدأ كلّ مخرج بفعل من مستويات بلوم العليا حيث أمكن — «يحلّل»، «يقيّم»، «يصمّم» — لا «يفهم» أو «يعرف». المخرج يسمّي سلوكاً يستطيع المدرّس ملاحظته وتقييمه.
- **خطة المقرر عقد.** سياسة التأخّر، أوزان الدرجات، اشتراطات الحضور يجب أن تكون قاطعة. إن اعترض طالب على درجة في الأسبوع العاشر، فالخطة هي الوثيقة التي تحتكمان إليها. الصياغة المطّاطة تُخسر الاحتكام.
- **وصف الواجب يسبق المعيار المهمّة.** الطلاب يكتبون للمعيار؛ إن ظهر سلم التقييم في الأسفل، يفوته نصف الفصل. ابدأ بالوزن والمعايير ثمّ المهمّة.
- **ملاحظات المحاضرة وثيقة موزَّعة، ليست نسخة حرفية.** اختزل المحاضرة في خمس إلى سبع فكرات يجب أن تصمد أسبوعاً. هوامش الصفحة (متطلّب سابق، خطأ شائع، تمهيد المحاضرة القادمة) تعمل أكثر ممّا يعمل السرد الطويل.
- **المقترح البحثي يلتزم.** لغة التحفّظ دليل على أنّ الباحث لم يعرف بعدُ ما يقترحه. استبدل «تهدف هذه الدراسة إلى استكشاف» بـ «ستقيس هذه الدراسة X في Y باستخدام Z». المحكّمون يكافئون التحديد.
- **فقرة الفجوة هي قلب مراجعة الأدبيات.** ثلاث فقرات أو أربع من الأعمال السابقة هي المقدّمة؛ فقرة الفجوة هي سبب استحقاق التمويل. لا تدفنها.
- **أسلوب التوثيق ثابت من البداية إلى النهاية.** اختر APA أو MLA أو Chicago أو IEEE مرّة واحدة. الخلط بين الأساليب يبدو غير مهني ويُسقط الرسالة في بعض اللجان.
- **العرف الأكاديمي العربي:** الأقسام المرقّمة تستخدم الأرقام العربية الشرقية (١ ٢ ٣) داخل النصّ الجاري، لكن المعادلات وأرقام DOI وISBN والسنوات تبقى لاتينية عبر `direction: ltr`. الخلط متوقَّع — لا عيب فيه.

### Financial (invoice / quote / statement / financial-summary — AR)

- **حقول الفاتورة الضريبية الإماراتية إلزامية.** وفق المرسوم بقانون اتحادي رقم (8) لسنة 2017، تشترط الفاتورة الضريبية صراحةً: عبارة «فاتورة ضريبية»، اسم وعنوان ورقم ضريبي للمورّد، اسم وعنوان ورقم ضريبي للعميل (إن كان مسجّلاً)، رقم تسلسلي للفاتورة، تاريخ الإصدار، تاريخ التوريد (إن اختلف)، وصف البنود، سعر الوحدة، نسبة ومبلغ ضريبة القيمة المضافة بشكل منفصل، والإجمالي شاملاً الضريبة. أيّ حقل مفقود يجعل الفاتورة غير صالحة لاسترداد ضريبة المدخلات — سيرفضها محاسب العميل.
- **الرقم الضريبي = 15 رقماً**، يُعرض دائماً بالأرقام اللاتينية مع `direction: ltr` حتى داخل الخلايا العربية. لا تعرضه بالأرقام العربية الشرقية أبداً — أنظمة الهيئة تقرأ اللاتينية.
- **العملة والمبالغ تظلّ LTR** بغضّ النظر عن لغة الوثيقة. `AED 17,600.00` تُقرأ بالاتّجاه نفسه في الحالتين. افرضها داخل الخلايا العربية بـ `direction: ltr; unicode-bidi: embed`.
- **المبلغ كتابةً يأتي تحت الإجمالي، لا بجانبه.** هو تحقّق قانوني، لا زخرف. اكتب الصيغة الكاملة («فقط سبعة عشر ألفاً وستمئة درهم إماراتي لا غير») — تجنّب الاختصارات.
- **النطاق في عرض السعر يسمّي المشمولات وغير المشمول معاً.** قائمة «غير المشمول» تمنع تمدّداً في النطاق بقيمة تفوق العرض نفسه. سمِّ «السفر»، «تراخيص الجهات الخارجية»، «المحتوى غير المُقدَّم منّا». الاستثناء الصريح يتفوّق على الافتراض الضمني.
- **كشف الحساب يستخدم شرائح الأعمار، لا دفتراً مسطّحاً.** جارٍ / 1–30 / 31–60 / 61–90 / +90 يوم. لوّن الشرائح: أخضر للجاري، كهرماني للـ 30–60، أحمر للـ +90. موظّف الحسابات الدائنة لدى العميل يحتاج إلى رؤية العمر بلمحة — هذه هي الرؤية التي تُطلق الدفع.
- **الملخّص المالي — التزم برقم في التعليق.** «نمت الإيرادات» حشو. «نمت الإيرادات 18٪ إلى 2.4 مليون درهم» حقيقة. الحسابات الإدارية غير مدقّقة، لذا أشر إلى ذلك صراحةً لتفادي اللبس بعد التدقيق.
- **دقّق في التقريب.** للملخّصات يكفي منزلة عشرية واحدة. للفواتير وكشوف الحسابات: منزلتان دائماً — الهيئة الضريبية وأنظمة المطابقة تشترطانها.
- **المعدّل الصفري يختلف عن المعفى.** البند بالمعدّل الصفري (كالنقل الدولي أو الخدمات المُصدَّرة) يُدرَج في إقرار ضريبة القيمة المضافة وإن كانت نسبته صفراً؛ البند المعفى لا يُدرَج. معظم فواتير B2B في الإمارات لا تواجه معفيات — عند وجودها، ضع عليها علامة ليعرفها محاسب العميل.

### Editorial (white-paper / article / op-ed / case-study — AR)

- **ابدأ بالقارئ، لا بالموضوع.** الوثائق التحريرية تتنافس على الانتباه. الثلاثون كلمة الأولى تحدّد من يواصل القراءة. افتتح بمشهد أو حكاية أو رقم مُدهش أو ادّعاء — لا بـ «في عالم اليوم المتسارع…» أو أيّ تمهيد شركاتي.
- **الورقة البيضاء تلتزم بأطروحة.** الورقة التي تكتفي باستعراض حقل ما هي تقرير لا ورقة بيضاء. سمِّ أطروحتك في الملخّص التنفيذي، ودافع عنها عبر الجسم، واعترف بحدودها. القرّاء يثقون بالكاتب الذي يتّخذ موقفاً.
- **المقال يكسب اقتباساته، لا يتزيّن بها.** الاقتباس يستحقّ مكانه حين يقول ما لا تستطيع *أنت* قوله — مصدر أوّلي، تجربة معيشة، صياغة دقيقة لخبير. الاقتباسات القابلة لإعادة الصياغة لا تضيف شيئاً. **لا تفتعل اقتباسات.** انظر قسم «إلتزام الدقة» أعلاه.
- **مقالات الرأي موقف لا تحليل.** أرِ القارئ تفكيرك لكن التزم برأي. لغة التحفّظ («يمكن القول بأنّ…») تشير إلى ضعف القناعة. اختر موقفاً، واصنع للمعارضة أمتن صياغة، ثمّ دافع عن موقفك على أيّ حال.
- **دراسة الحالة تبدأ بالنتيجة، لا بالنشاط.** «أعدنا تصميم تجربة الانضمام» ضعيف. «انخفض زمن الانضمام من ٦ أسابيع إلى ٤، بتوفير ٣٤٠ ألف درهم سنوياً» قوي. صندوق الحقائق والبطل الرقمي يُقرآن قبل النصّ — اجعلهما يستحقّان مكانهما.
- **الحرف الاستهلالي الكبير إشارة تحريرية لا خطأ طباعي.** الحرف الأوّل المكبَّر يشير إلى «شكل طويل، اقرأ بتمهّل». استخدمه في الورقة البيضاء والمقال والرأي؛ تخطَّه في دراسة الحالة (صندوق الحقائق يفتح بدلاً منه).
- **الاقتباسات البارزة تحرير، لا زخرفة.** اختر سطراً واحداً لا يُنسى لكلّ قسم وأبرزه. ينبغي أن يتمكّن القارئ الماسح للصفحة من إعادة بناء الحجّة من الاقتباسات البارزة وحدها.
- **الحواشي تحمل ثقلاً في الأوراق البيضاء لا في مقالات الرأي.** الأوراق البيضاء توثّق بصرامة — القرّاء يراجعون الحواشي. مقالات الرأي تدمج المصادر في النصّ الجاري؛ عمود حواشٍ متراصّ يوحي بتدرُّع زائد.
- **اصطنع للمعارضة أمتن صياغة.** المقالات ومقالات الرأي التي تكتفي بالأدلّة المؤيّدة تبدو دعائية. القرّاء يثقون بالكاتب الذي يتعامل مع أقوى الحجج المضادّة لا مع أضعفها.

### Marketing-print (sell-sheet / product-brief / capability-statement / slide-deck — AR)

- **ابدأ بالنتيجة، لا بالنشاط.** أوراق البيع والعروض التقديمية تعيش أو تموت في الخمس ثواني الأولى. «نُساعدك على تقليص زمن التمكين» ضعيفة. «زمن التمكين ينخفض من ٦ أسابيع إلى ٤» قوية. العميل لا يشتري ميزاتك — يشتري التغيير.
- **ادّعاء واحد لكلّ صفحة.** ورقة بيع بثلاثة عناوين لا عنوان لها. شريحة بأربع نقاط متنافسة شريحة بصفر نقاط لا تُنسى. اختر الشيء الواحد؛ انقل الباقي إلى مواد داعمة.
- **الأرقام الكبيرة تستحقّ حجمها.** شريط القيمة والشريحة ذات الرقم الكبير وبطاقات المقاييس تعمل فقط حين تكون الأرقام حقيقية وحالية ومحدّدة. «أسرع» بلا معنى؛ «أسرع بنسبة ٤٢٪ خلال ٩٠ يوماً» حاسمة. إن لم تستطع تسمية المصدر، فالرقم زخرف.
- **بيان القدرات أداة مشتريات حكومية / B2B — الشكل مهمّ.** أربع حقائق سريعة، شبكة كفاءات واضحة، جدول سجلّ أداء مع العميل والنطاق والسنة، عناصر تمييز مع الإثبات، ثمّ التواصل والرقم الضريبي والترخيص. إن لم يستطع موظّف المشتريات تصفّحه في ٣٠ ثانية، فقد كُتب خطأً.
- **العروض التقديمية تُقرأ من آخر القاعة.** إن نزل نصّ الجسم دون ١٦ نقطة، أعد الصياغة. ستّ كلمات لكلّ نقطة، سبع نقاط لكلّ شريحة، أيّهما أسبق. الشرائح معينات للمتحدّث — الحجج المفصّلة مكانها الورقة الواحدة قبل أو بعد.
- **الفواصل الأقسام محطّات استراحة لا زخرفة.** كلّ ٤–٦ شرائح محتوى، أدرج فاصلاً ملوّناً برقم الجزء وعنوان القسم. انتباه الجمهور يُعاد ضبطه؛ عدد الشرائح يعكس الأقواس السردية لا الصفحات فحسب.
- **دعوة واحدة للحركة لكلّ مادّة.** أيّاً كان ما تطلبه من القارئ — حجز مكالمة، الردّ على البريد، اعتماد العرض — قله في سطر واحد، ضعه في النهاية، وكرّر تفاصيل التواصل. إن طلبت ثلاثة أشياء، فستحصل على صفر.
- **الشهادات تحتاج محدّدات وإلا فهي حشو.** «فريق رائع للعمل معه» لا تُضيف. «قلّص دورة التقارير من أسبوع إلى يوم» تستحقّ المساحة. إن كانت الشهادة تنطبق على أيّ منافس، فاحذفها.
- **العروض العربية تعكس كلّ شيء.** A4 أفقي يبقى أفقياً، لكنّ فواصل الأقسام تنعكس (رقم الفصل إلى اليسار، النصّ إلى اليمين)، أرقام الهاتف والبريد LTR داخل الشرائح RTL، وعدّاد الصفحات يبقى بأرقام لاتينية.

### Legal (service-agreement / mou / nda / engagement-letter — AR)

- **النماذج ليست استشارة قانونية.** القاعدة الأولى غير القابلة للتفاوض. كلّ وثيقة قانونية ينتجها «كاتب» تحمل شريط إخلاء مسؤولية يُحيل الأطراف إلى مستشار قانوني مؤهّل. لا تحذف الشريط؛ عدّل صياغته فقط.
- **عرّف المصطلحات مرّة واحدة، ثمّ استخدمها بتعريفها الدائم.** المصطلح الذي يُقدَّم بين علامتَي اقتباس مع صفته («الخدمات»، «المعلومات السرّية»، «تاريخ النفاذ») يصبح مصطلحاً معرَّفاً. استخدم الصيغة نفسها في كلّ موضع آخر من الوثيقة. التنويع في الصياغة يفتح باب النزاع التفسيري.
- **ترقيم البنود متسلسل ومتدرّج.** `١.`، `١٫١`، `١٫٢٫١`. يشير الأطراف إلى البنود بأرقامها خلال التفاوض؛ إعادة الترقيم بعد التعديل انضباط لا إزعاج. بدائية `ol.clauses` في «كاتب» تُرقّم تلقائياً — دعها تعمل.
- **كلّ اتفاقية تسمّي قانوناً حاكماً ومحكمة.** إغفال هذا خطأ شائع يُسقط النزاعات في متاهة الاختصاص. الاتفاقيات الإماراتية تختار عادةً بين: (١) محاكم الإمارة، (٢) محاكم مركز دبي المالي العالمي أو سوق أبوظبي العالمي (محاكم القانون العامّ الإنجليزي)، (٣) تحكيم مركز دبي للتحكيم الدولي ومقرّه دبي. اختر واحداً واحذف البدائل.
- **«حيث إنّ» ليست زخرفاً.** التمهيد يُؤطّر السياق التجاري — وبند «عليه، وبناءً على التعهّدات المتبادلة» ينقل من السياق إلى البنود العاملة. تقرأ المحاكم التمهيد لتفسير البنود عند غموضها. اكتبه بجمل خبرية قصيرة — لا سرداً.
- **مذكّرات التفاهم تُشير بوضوح إلى البنود المُلزِمة وغير المُلزِمة.** يعامل الأطراف عادةً المذكّرة كاملةً غير مُلزِمة باستثناء ثلاثة: السرّية، القانون الحاكم، النفقات. علّم كلّ بند مُلزِم بشكل صريح — نموذج «كاتب» يستخدم علامة `(مُلزِم)` بجانب تلك العناوين.
- **صناديق التوقيع تستحقّ فاصل صفحة.** لا تُقسَم أبداً عبر صفحتَين. استخدم `page-break-before` عند الحاجة. يوقّع الطرفان على الصفحة نفسها أو على نسخ متقابلة — لا توقيعاً يتيماً على صفحة مفردة.
- **NDAs المتبادلة مقابل الأحادية.** تستخدم المتبادلة «الطرفَين»، «كلّ طرف»، «الطرف المُتلقّي» و«الطرف المُفصِح» بأدوار متبادلة. الأحادية تسمّي طرفاً مُفصِحاً وطرفاً مُتلقّياً فقط؛ احذف الصياغة المتبادلة. اختر مسبقاً؛ لا تخلط.
- **الأتعاب والسقوف بالأرقام والكلمات.** «مئة وعشرون ألفاً (١٢٠٬٠٠٠)» تصمد أمام أخطاء المسح والفاكس والنسخ. ينطبق الأمر على مدد السريان: «ثلاثون (٣٠) يوماً».
- **الصياغة القانونية العربية لها أعرافها.** `حيث إنّ` يفتتح التمهيد. `عليه، وبناءً على التعهّدات المتبادلة` يجسر نحو البنود العاملة. `يُقرّ الطرفان` يفتتح التصريحات الرسمية. استخدم العربية القانونية الكاملة — «خطاب تعاقد» — لا الصياغة الدارجة.

---

## Quality-gate workflow (self-gate for every Arabic render)

Katib is self-sufficient. Before any Arabic content leaves the skill, apply this gate **explicitly**. It replaces the implicit dependency on the `/arabic` skill.

### Step 1 · Pre-write (before first character)

1. **Read the doc-type notes section above** for the target domain + doc_type. Each has non-negotiable conventions.
2. **Confirm audience register.** Doc-type default is formality 3-4 unless the domain table says otherwise. Match it.
3. **Plan sources.** What external facts (stats, quotes, citations) will appear? Have the sources before writing, not during.

### Step 2 · Write (while drafting)

1. **Lead with the specific.** No throat-clearing openers.
2. **Apply the MSA grammar checklist** for every إذا, every بسبب, every جمع غير عاقل pronoun.
3. **Qualify every ambiguous term** on first appearance (وكيل→الوكيل الذكي, إطار→الإطار التقني).
4. **Translate every English abbreviation** on first appearance.
5. **Never fabricate quotes or stats.** See "Fact integrity" above. When in doubt, cut.

### Step 3 · Post-write (before commit / render)

Run the 5-dimension anti-slop score mentally on the full content. Each dimension scored 1-10:

| Dimension | Arabic | What to check |
|---|---|---|
| Directness | المباشرة | No throat-clearing openers (§1). No hedging (§6a). Points land early. |
| Rhythm | الإيقاع | Sentence length varies (§5). Max 2 واو per sentence. No 3-item list monotony (§4d). |
| Trust | الثقة بالقارئ | No hand-holding (§6b). No meta-commentary (§6c). No "as we noted earlier". |
| Authenticity | الأصالة | No banned emphasis crutches (§2). No false agency (§4c). No jargon inflation (§3). |
| Density | الكثافة | No vague declaratives (§7). Every sentence adds information. Numbers over adjectives. |

**Scoring guide:**
- 1-3: multiple violations per paragraph — rewrite
- 4-6: occasional slips, mostly clean
- 7-8: strong, only minor issues
- 9-10: no detectable AI patterns

**Threshold: 35/50.** Below, revise.

### Step 4 · Fact integrity sweep

1. Grep the content for blockquotes (`<blockquote>`, `>`). For each, confirm the source exists and the quote is real. **If any can't be sourced, delete the blockquote.**
2. Grep for numeric claims (digits, percentages). For each, confirm the source.
3. Grep for named institutions / events / reports. For each, confirm the reference is factual.

Done. Proceed to render.

---

## See also

- `references/design.ar.md` — Arabic typography + RTL design
- `references/production.md` — WeasyPrint quirks for Arabic
- `domains/<domain>/templates/*.ar.html` — per-doc-type templates

The `/arabic` skill (upstream) may still be used when producing **free-form**
content (LinkedIn, email, articles outside of Katib). For Katib renders, the
rules above are the complete contract.
