# Katib — Production Quirks & Bug Catalog

WeasyPrint has known rendering landmines. This catalog captures every bug we've seen, its symptom, and the fix. Read this file when `--verify` fails or output looks wrong.

---

## WeasyPrint (PDF pipeline)

### 1.1 Tag `rgba()` double-rectangle

**Symptom:** Inline `.tag` elements with `background: rgba(...)` render as two stacked rectangles — one the intended fill, one a solid underlay.

**Cause:** WeasyPrint bug in alpha-blended inline-box rendering.

**Fix:** Never use `rgba()` for tag/chip backgrounds. Convert to flat hex using the blend table in `design.en.md` §"rgba → hex conversion".

```css
/* WRONG */
.tag { background: rgba(27, 42, 74, 0.18); }

/* RIGHT (navy @ 0.18 over #FAFAF8) */
.tag { background: #D8DEED; }
```

`build.py --check` grep-fails if `rgba(` appears in any template.

### 1.2 Thin border + border-radius → double ring

**Symptom:** Cards with `border: 0.4pt` and `border-radius: > 4pt` show a visible double outline (the border + a second phantom stroke ~0.5px inside).

**Cause:** WeasyPrint's border path rasterization at sub-pixel thickness.

**Fix:** Either border-width ≥ 1pt, OR remove border-radius, OR replace with `box-shadow: 0 0 0 0.5pt var(--border);` (ring shadow).

```css
/* WRONG */
.card { border: 0.4pt solid var(--border); border-radius: 8pt; }

/* RIGHT — thicker border */
.card { border: 0.5pt solid var(--border); border-radius: 8pt; }

/* RIGHT — ring shadow (no border attribute) */
.card { box-shadow: 0 0 0 0.5pt var(--border); border-radius: 8pt; }
```

### 1.3 `height: 100vh` in `@page` context

**Symptom:** Cover section renders at ~88-92% of expected page height; bottom gutter appears.

**Cause:** WeasyPrint doesn't interpret `vh` inside `@page` reliably — especially when mixed with `@page :first { margin: 0 }`.

**Fix:** Use explicit mm dimensions matching the page size.

```css
/* WRONG */
.cover { height: 100vh; }

/* RIGHT — A4 portrait */
.cover { height: 297mm; width: 210mm; }
```

### 1.4 `page-break-inside: avoid` inside flex

**Symptom:** Cards inside a flex row break mid-element across pages despite `page-break-inside: avoid`.

**Cause:** WeasyPrint doesn't honor break rules on flex children.

**Fix:** Wrap the flex children in a `<div class="no-break">` block container.

```html
<!-- WRONG -->
<div style="display: flex; gap: 16pt;">
  <div class="card" style="page-break-inside: avoid;">...</div>
</div>

<!-- RIGHT -->
<div style="display: flex; gap: 16pt;">
  <div class="no-break">
    <div class="card">...</div>
  </div>
</div>
```

Where `.no-break { page-break-inside: avoid; }`.

### 1.5 SVG `marker` with `orient="auto"`

**Symptom:** Arrow markers in inline SVG diagrams point the wrong direction or all the same direction regardless of line angle.

**Cause:** WeasyPrint does not rotate markers based on line orientation.

**Fix:** Create per-orientation marker copies and reference them explicitly, OR hard-code the arrowhead polygon at the line endpoint.

### 1.6 Page counter resets across sections

**Symptom:** `counter(page)` starts from 1 on the signature page instead of "hidden". Or body pages start at 1 instead of 3.

**Cause:** WeasyPrint's `@page` named regions require explicit counter-reset.

**Fix:** Use explicit named pages and counter resets.

```css
@page cover { size: A4; margin: 0; }
@page signature { size: A4; margin: 20mm 22mm; counter-reset: page 0; }
@page body { size: A4; margin: 20mm 22mm; counter-reset: page 2; }  /* next page will be 3 */

.cover { page: cover; }
.signature { page: signature; }
.body { page: body; }
```

### 1.7 `@font-face` not resolved

**Symptom:** Body renders in a fallback font; Arabic renders as tofu squares.

**Cause:** WeasyPrint resolves `@font-face url()` paths relative to the CWD at render time, not the HTML file.

**Fix:** Always pass `base_url=<template_dir>` to `HTML()`:

```python
HTML(str(template_path), base_url=str(template_path.parent)).write_pdf(out_path)
```

Or use absolute paths in `@font-face url()` (fragile — breaks on skill relocation).

### 1.8 Arabic font fallback chain

**Symptom:** Arabic text renders in a thin, spaced-out, incorrect font even though `@font-face` loaded successfully.

**Cause:** Browser-style font fallback kicks in before the Arabic font is matched. First font in stack has no Arabic glyphs.

**Fix:** Arabic fonts must come first in the stack for `[lang="ar"]` elements, not in the primary `body` font.

```css
body { font-family: "Arial", "Helvetica Neue", sans-serif; }

html[lang="ar"] body {
  font-family: "IBM Plex Arabic", "Cairo", "Amiri", "Tahoma", sans-serif;
}
```

### 1.9 Images stretch or crop unexpectedly

**Symptom:** Cover image shows white border or is cropped on one side.

**Cause:** Image aspect ratio doesn't match container; `object-fit` support is partial.

**Fix:** Generate cover images at exactly the target aspect (e.g., 9:16 for A4 portrait) and use `width: 210mm; height: 297mm; object-fit: cover;` — or use `background-image` with `background-size: cover`.

### 1.10 Tables break mid-row

**Symptom:** A table row splits across pages — top half on one page, bottom half on the next.

**Cause:** Default row break behavior.

**Fix:**

```css
tr { page-break-inside: avoid; }
thead { display: table-header-group; }  /* repeat header on each page */
```

---

## Part 2 · Cross-cutting issues

### 3.1 Bidi in mixed EN/AR text

**Symptom:** English technical terms inside Arabic prose render in wrong order (e.g., "MCP" appears reversed).

**Cause:** Bidi algorithm ambiguity when direction isn't explicit.

**Fix:** Wrap English tokens in `<span dir="ltr">`.

```html
يدعم البروتوكول <span dir="ltr">MCP</span> عدة نماذج
```

### 3.2 Number formatting drift

**Symptom:** Page numbers appear in Western digits while body uses Arabic-Indic (or vice versa).

**Cause:** `@page` counter doesn't inherit `font-variant-numeric` from body.

**Fix:**

```css
@page { @bottom-center { content: counter(page); font-variant-numeric: tabular-nums; } }

html[lang="ar"] @page {
  @bottom-center {
    content: counter(page, arabic-indic);
  }
}
```

WeasyPrint supports `counter(page, arabic-indic)` as of 60.0+.

### 3.3 Font size appears smaller in Arabic

**Symptom:** Arabic text at the same `pt` size reads smaller than English.

**Cause:** Arabic characters have a smaller x-height and denser counter spaces.

**Fix:** Bump size +1pt for Arabic at every scale position. See `design.ar.md` §5.

---

## Part 3 · Verification hooks

`build.py --check` (fast, no render) enforces:

- No `rgba(` anywhere in CSS
- No `letter-spacing` on any `[lang="ar"]` selector
- Every `<pre>` or `<code>` has `dir="ltr"`
- No `height: 100vh` inside `@page`
- All `@font-face url(...)` paths resolve

`build.py --verify <target>` (renders, then inspects):

- Page count ≤ doc type's hard limit
- Every artifact in manifest exists on disk
- No unresolved `{{placeholder}}` tokens
- `tokens-snapshot.json` parses as valid JSON
- PDF extractable text contains expected title (sanity)

Failures block the build. Warnings don't.
