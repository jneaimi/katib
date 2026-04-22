# Katib — Arabic Writing Rules

MSA grammar, brand voice, and anti-slop guidance for Arabic content across all domains. Snapshot from `/arabic` skill — sync via `scripts/sync-from-arabic.sh` when upstream improves. Last synced: 2026-04-21.

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

## Anti-slop catalog (AR)

### Banned openers

- `في عالمنا اليوم / في عصرنا هذا / نعيش في زمن`
- `لا شك أن / من البديهي أن / من المعلوم أن`
- `تجدر الإشارة إلى / يجب التأكيد على`
- `في ظل التحولات المتسارعة`

### Banned emphasis crutches

- `وهنا تكمن المفارقة / وهذا بالضبط ما يجعل`
- `في الحقيقة / في الواقع / في الأمر`

### Banned jargon triples

- `التحول الرقمي الشامل والتطور التقني المتسارع والابتكار المستدام`
- `فعّال ومرن وقابل للتطوير` (as a set)

### Banned false-agency sentences

AI text makes technology the subject. Rewrite with humans doing the action:

- ✗ "التقنية تتيح / التحول يفرض"
- ✓ "تستخدم الفرق هذه التقنية لـ..."

### Banned vague declaratives

- `النتائج مذهلة / الفرص لا حصر لها / التأثير هائل`

Replace with specific numbers, names, or outcomes.

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

### Report (research / progress / annual / audit — AR)

- **صيغة معلوماتية**، ليست إقناعية. التقرير يوثّق الاكتشافات؛ العرض يبيعها.
- استخدم الصيغة الموضوعية: `وجد فريق التدقيق` لا `وجدنا`. الاستثناء: كلمة رئيس المجلس في التقرير السنوي بصيغة المتكلّم.
- كل رقم يستند إلى مصدر: حاشية، صف جدول، أو مرجع ملحق. لا أرقام طليقة.
- **الجداول للمقارنات**، لا السرد. إن احتاج القارئ مقارنة ثلاث عناصر فأكثر، لا تدفنها في فقرات.
- الملخّص التنفيذي = التقرير في ١٥٠ كلمة. عامله كأنّه الشيء الوحيد الذي سيقرأه صاحب القرار.
- ملاحظات التدقيق تُرتَّب: **الملاحظة ← الخطر ← الدليل ← التوصية**. لا تخلط.
- احتفظ بالأرقام المرجعية بالأحرف اللاتينية (`AUD-001`) — لا تترجمها، فالتتبّع عبر اللغتين يعتمد عليها.
- الأرقام داخل الجداول تستحق `direction: ltr` على خلية `.num` لقراءة سليمة يميناً إلى يساراً للرقم نفسه.

## Anti-slop scoring (AR)

Same 5-dimension gate as EN, translated:

| Dimension | Arabic |
|---|---|
| Directness | المباشرة |
| Rhythm | الإيقاع |
| Trust | الثقة بالقارئ |
| Authenticity | الأصالة |
| Density | الكثافة |

Threshold: 35/50. Below, revise.

## See also

For the full 50+ anti-slop catalog, regional dialect notes, and extensive writing examples, see upstream `/arabic` skill:

- `~/.claude/skills/arabic/references/brand-voice.md`
- `~/.claude/skills/arabic/references/anti-slop.md`
- `~/.claude/skills/arabic/references/writing-examples.md`

Katib's Arabic references are a **condensed snapshot** — re-sync after any upstream change.
