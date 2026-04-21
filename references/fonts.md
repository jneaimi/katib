# Katib — Font Reference

Four core OFL families are bundled. Domain `tokens.json` specifies which family to use for primary/display per language. Optional families install via `katib install-font <name>` (v0.2).

---

## Core bundle (`assets/fonts/core/`)

All four are SIL Open Font License — safe to bundle and redistribute.

| Family | Use | Script | License | Source |
|---|---|---|---|---|
| **Newsreader** | Editorial serif — headlines + body | Latin | OFL | [Google Fonts](https://fonts.google.com/specimen/Newsreader) |
| **Inter** | Sans — UI, labels, metadata | Latin | OFL | [Google Fonts](https://fonts.google.com/specimen/Inter) |
| **Amiri** | Arabic serif — editorial, formal | Arabic | OFL | [Google Fonts](https://fonts.google.com/specimen/Amiri) |
| **Cairo** | Arabic sans — UI, modern corporate | Arabic | OFL | [Google Fonts](https://fonts.google.com/specimen/Cairo) |

## Per-domain font stacks (v0)

### business-proposal

```
EN primary:  Arial, Helvetica Neue, Inter, system-ui, sans-serif
             ^^^ system Arial by default for broad corporate familiarity — override per brand
AR primary:  IBM Plex Arabic, Cairo, Tahoma, sans-serif
             ^^^ IBM Plex Arabic is the preferred corporate font; falls back to bundled Cairo
```

### tutorial

```
EN body:     Inter, system-ui, sans-serif
EN display:  Inter, system-ui, sans-serif
EN code:     JetBrains Mono, SF Mono, Menlo, Consolas, monospace
AR body:     Cairo, IBM Plex Arabic, Tahoma, sans-serif
AR display:  Cairo, IBM Plex Arabic, Tahoma, sans-serif
AR code:     (stays LTR, uses EN code stack)
```

### editorial (v0.2 — reference)

```
EN primary:  Newsreader, Charter, Georgia, serif
AR primary:  Amiri, Noto Naskh Arabic, serif
```

## Fallback chain strategy

Every stack has three tiers:

1. **Preferred** — the designed-for font (Inter, Cairo, Newsreader, Amiri)
2. **System alternative** — macOS/Windows system font that won't tofu (Helvetica Neue, Tahoma)
3. **Generic** — `sans-serif` / `serif` — browsers' own fallback

Order matters. Arabic fonts MUST come first in `[lang="ar"]` stacks because Latin-first fonts don't have Arabic glyphs and the fallback kicks in too late.

## `@font-face` declaration pattern

Each template's `<style>` block declares `@font-face` for its required families using relative URLs to `assets/fonts/core/`:

```css
@font-face {
  font-family: "Inter";
  src: url("../../assets/fonts/core/Inter-Regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
}

@font-face {
  font-family: "Amiri";
  src: url("../../assets/fonts/core/Amiri-Regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
}
```

WeasyPrint resolves these relative to `HTML(path, base_url=path.parent)` — always pass `base_url` when calling.

## Optional families (v0.2 via `katib install-font`)

When a domain needs a font outside the core bundle:

```bash
katib install-font "IBM Plex Arabic"
katib install-font "JetBrains Mono"
katib install-font "Noto Naskh Arabic"
```

Installs to `~/.local/share/katib/fonts/<family>/` with license notice preserved. Templates reference these via the same `@font-face` pattern with absolute paths (`file://...`) injected by `build.py`.

## License compliance

| Font | License | Redistribution | Commercial use |
|---|---|---|---|
| Newsreader | OFL | ✓ | ✓ |
| Inter | OFL | ✓ | ✓ |
| Amiri | OFL | ✓ | ✓ |
| Cairo | OFL | ✓ | ✓ |
| IBM Plex Arabic | OFL | ✓ | ✓ (install optional, don't bundle in v0) |
| Noto Naskh Arabic | OFL | ✓ | ✓ |
| JetBrains Mono | OFL | ✓ | ✓ |

**Do NOT bundle:**
- TsangerJinKai02 (Tsanger license — commercial restricted; was in Kami but we skip it)
- Helvetica / Helvetica Neue (system font, not redistributable)
- Monotype / Linotype commercial fonts

Katib ships only OFL fonts. License notices are preserved in `assets/fonts/core/LICENSE.<family>.txt`.

## Font size adjustments for Arabic

Arabic typography needs +1pt bump at every scale position vs Latin. Set via `html[lang="ar"]` selectors — see `design.ar.md` §5.

## Adding a new font (for future domain work)

1. Verify it's OFL or a license that permits redistribution
2. Download `.woff2` files (regular + any weights used)
3. Place in `assets/fonts/optional/<family>/`
4. Update the relevant domain's `tokens.json` → `fonts.ar.primary` or similar
5. Add `@font-face` declaration to the template's style block
6. Add a row to this file's tables
