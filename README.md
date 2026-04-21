<p align="center">
  <img src="assets/logo-horizontal.png" alt="Katib — bilingual document generation" width="700">
</p>

<p align="center">
  <b>Bilingual (EN + AR) print-grade PDF document generation for Claude Code.</b><br>
  <a href="https://www.npmjs.com/package/@jasemal/katib"><img alt="npm" src="https://img.shields.io/npm/v/%40jasemal%2Fkatib?color=1B2A4A&label=npm&style=flat-square"></a>
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-1B2A4A?style=flat-square"></a>
  <img alt="platforms" src="https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20WSL2-1B2A4A?style=flat-square">
</p>

One skill, two languages, multiple document domains, pluggable cover + layout
styles, per-project brand profiles. HTML + CSS → WeasyPrint → PDF.

Invoked with `/katib` inside any Claude Code conversation.

> **كاتب** (*kātib*, "the writer") — the one who shapes words onto paper.

---

## What it does

| | |
|---|---|
| **Domains** | `business-proposal`, `tutorial` |
| **Doc types** | Proposal, one-pager, letter · how-to, onboarding, tutorial, handoff, cheatsheet |
| **Languages** | English (LTR) and Arabic (RTL, MSA + خليجي) as peer templates — not machine translation |
| **Output** | Print-grade PDF via WeasyPrint |
| **Covers** | Minimalist CSS (no API key), Gemini neural-cartography, Gemini friendly-illustration |
| **Interiors** | `classic`, `workbook` |
| **Brand profiles** | Per-client YAML — colors, fonts, logo, identity; bilingual fallback baked in |
| **Diagrams** | Inline SVG with brand-color tokenization (no external diagram tools) |
| **Screenshots** | Playwright capture + Pillow annotation + CSS frames — bilingual alt/caption bundles |
| **Fonts** | Katib declares 4 core families (Newsreader, Inter, Amiri, Cairo). Install them once — see [Fonts](#fonts) below. |

---

## Requirements

| | |
|---|---|
| **OS** | macOS · Linux · Windows via WSL2 (native Windows unsupported — see note below) |
| **Python** | 3.11 or newer |
| **uv** | any recent version — installer will install it if missing |
| **System libs** | Pango, Cairo, GDK-Pixbuf (for WeasyPrint) |
| **Gemini API key** | *optional* — only for image-based covers. `minimalist-typographic` works without it. |

### System library install, per OS

| OS | Command |
|---|---|
| macOS | `brew install pango cairo gdk-pixbuf libffi` |
| Debian / Ubuntu | `sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev` |
| Fedora | `sudo dnf install pango cairo gdk-pixbuf2 libffi-devel` |
| Arch | `sudo pacman -S pango cairo gdk-pixbuf2 libffi` |
| Windows | Use [WSL2 with Ubuntu](https://learn.microsoft.com/en-us/windows/wsl/install), then follow the Debian/Ubuntu row |

Why no native Windows? WeasyPrint on native Windows needs the GTK3 runtime and
is historically fragile. WSL2 is the reliable path and it's what most Claude
Code users on Windows already have.

---

## Install

**Recommended** — via npx (no cloning, always latest):

```bash
npx @jasemal/katib
```

That's it. The wrapper runs the installer under the hood — no global install, no lockfiles, re-run any time to update.

**Other installers**:

```bash
# curl + bash (no Node required)
curl -fsSL https://raw.githubusercontent.com/jneaimi/katib/main/install.sh | bash

# or clone and run
git clone https://github.com/jneaimi/katib.git && cd katib && bash install.sh
```

The installer:
1. Checks prereqs (git, Python 3.11+, uv, WeasyPrint libs)
2. Clones to `~/.claude/skills/katib/` — or pulls if already installed
3. Runs `uv run playwright install chromium` for the screenshot module
4. Creates `~/.katib/brands/`, `~/.config/katib/`, `~/.local/share/katib/memory/`
5. Seeds a vault-aware `~/.config/katib/config.yaml`
6. Prompts for an optional Gemini API key and (with your OK) appends it to your shell rc

Re-run any time to update.

### npx commands

```bash
npx @jasemal/katib                    # install (or update if already installed)
npx @jasemal/katib update             # git pull the installed skill
npx @jasemal/katib uninstall          # remove the skill, keep user data
npx @jasemal/katib uninstall --purge  # also wipe ~/.katib, config, memory
npx @jasemal/katib version            # print the CLI version
npx @jasemal/katib help               # full usage
```

---

## First use

After install, restart Claude Code and type `/katib` in any conversation.

Or drive the build directly from the terminal:

```bash
cd ~/.claude/skills/katib

# Business proposal — English, Arabic, co-located via --slug
uv run scripts/build.py proposal --domain business-proposal --lang en --slug my-first-proposal
uv run scripts/build.py proposal --domain business-proposal --lang ar --slug my-first-proposal

# Tutorial — applies a specific brand + bundled layout
uv run scripts/build.py how-to --domain tutorial --lang en --brand example --layout workbook

# With a Gemini cover (needs GEMINI_API_KEY)
uv run scripts/build.py proposal --domain business-proposal --lang en \
  --cover neural-cartography --with-cover

# List installed brands
uv run scripts/build.py --list-brands
```

Generated folders land in:

- `~/vault/content/katib/<domain>/<date>-<slug>/` — if `~/vault/` exists (Obsidian users)
- `~/Documents/katib/<domain>/<date>-<slug>/` — otherwise

Override anywhere with `KATIB_OUTPUT_ROOT=/path/to/elsewhere`.

Each folder contains the PDF(s), a `manifest.md`, a `source/` copy of the rendered HTML, and a `.katib/run.json` with build metadata.

---

## Brand profiles

A brand profile is a single YAML file that overrides colors, fonts, logo, and
author identity per project — without touching templates.

```yaml
# ~/.katib/brands/acme.yaml
name: ACME Corp
name_ar: شركة أكمي
legal_name: ACME Corp LLC

identity:
  author_name: Jane Doe
  email: jane@acme.example

colors:
  accent: "#1B2A4A"
  accent_2: "#C5A44E"
  accent_on: "#FFFFFF"

fonts:
  en: { primary: "Inter", display: "Newsreader" }
  ar: { primary: "IBM Plex Arabic" }

logo: ./logo.svg
```

Then: `--brand acme` on any build. See [`brands/README.md`](brands/README.md)
for the full schema.

---

## Configuration

Edit `~/.config/katib/config.yaml` (the installer creates it from
[`config.example.yaml`](config.example.yaml)). Keys:

- **`output.destination`** — `vault` or `custom`
- **`output.custom_path`** — where generated folders go when destination=custom
- **`identity.*`** — default author, email, company (brand profiles override)
- **`image_model.*`** — Gemini model preferences
- **`memory.location`** — where run logs and feedback are stored

Per-project override: drop `.katib/config.yaml` in any project root — only the keys you want to change.

Precedence: CLI flag → project config → user config → skill defaults.

---

## Diagrams

Katib renders crisp inline SVG diagrams that adopt the active brand's colors.
Write `fill="{{ colors.accent }}"` in any template SVG and the value resolves
at render time to the brand's accent hex.

See [`references/diagrams.md`](references/diagrams.md) for patterns (process
flow, layered architecture, numbered steps, connectors with arrowheads).

WeasyPrint can't resolve CSS `var()` inside SVG attributes — hence the Jinja
context substitution. Everything else (CSS outside SVG, the `:root` token
injection) still uses `var()`.

---

## Screenshots (tutorial domain)

```bash
uv run scripts/shot.py web https://example.com --out assets/screenshots/step-1.png \
  --alt-en "login page" --alt-ar "صفحة الدخول" \
  --caption-en "the login form" --caption-ar "نموذج تسجيل الدخول"

uv run scripts/annotate.py assets/screenshots/step-1.png --arrow 420,180 --label "click here"
uv run scripts/frame.py    assets/screenshots/step-1.png --style browser-safari
```

Results are content-addressed-cached at `~/.katib/cache/screenshots/` — repeat
captures with matching inputs skip Playwright (~50× faster).

---

## Updating

Re-run `install.sh` — it detects an existing checkout and does a `git pull`.

Or manually:

```bash
cd ~/.claude/skills/katib && git pull
```

---

## Uninstalling

```bash
bash ~/.claude/skills/katib/uninstall.sh           # removes the skill
bash ~/.claude/skills/katib/uninstall.sh --purge   # also wipes ~/.katib, ~/.config/katib, ~/.local/share/katib
```

---

## Tests

```bash
cd ~/.claude/skills/katib
bash scripts/test-all.sh          # business-proposal × 3 doc types × 2 langs
bash scripts/test-tutorial.sh     # tutorial × 5 doc types × 2 langs
bash scripts/test-brand.sh        # brand profile loader + end-to-end render
bash scripts/test-alt-bundles.sh  # bilingual alt/caption resolution
bash scripts/test-images.sh       # annotate + frame golden-image regression
```

---

## Troubleshooting

- **"WeasyPrint can't load"** — System libs are missing. Run the command for
  your OS from the [Requirements](#requirements) table.
- **"Arabic text renders as boxes"** — The Arabic font isn't loading. Katib
  bundles Amiri and Cairo, so this usually means the template is asking for a
  font you don't have. Check the domain `tokens.json` and your brand profile.
- **"Gemini cover failed"** — Either `GEMINI_API_KEY` isn't set or the model
  deprecated. Switch to `--cover minimalist-typographic` to unblock.
- **"Playwright missing browser"** — Run `uv run playwright install chromium`.
- **Anything else** — `references/production.md` has a quirk catalog.

---

## Fonts

Katib's templates call four core font families. They are **not bundled** in
v0.1 — install them once on your machine and Katib will pick them up via the
system font stack. All four are free under SIL OFL.

| Family | Used for | Where to get |
|---|---|---|
| **Inter** | English UI / body | [rsms.me/inter](https://rsms.me/inter/) |
| **Newsreader** | English display / covers | [Google Fonts](https://fonts.google.com/specimen/Newsreader) |
| **Amiri** | Arabic body / letters | [Google Fonts](https://fonts.google.com/specimen/Amiri) |
| **Cairo** | Arabic UI / tutorials | [Google Fonts](https://fonts.google.com/specimen/Cairo) |

macOS: double-click each `.ttf` / `.otf` and Font Book handles it.
Linux: drop into `~/.local/share/fonts/` then `fc-cache -fv`.
Missing a font? Katib falls back to the next family in the stack
(`Inter → system-ui`, `Amiri → Cairo → Tahoma`) so nothing crashes.

A future release will optionally bundle the fonts (OFL permits redistribution).

## License

MIT. See [LICENSE](LICENSE). Font families referenced by Katib are SIL OFL —
see the [Fonts](#fonts) section for attribution links.

## Acknowledgments

Built on [WeasyPrint](https://weasyprint.org/),
[Jinja2](https://jinja.palletsprojects.com/),
[Playwright](https://playwright.dev/), and
[Pillow](https://python-pillow.org/).
Typography: [Newsreader](https://fonts.google.com/specimen/Newsreader),
[Inter](https://rsms.me/inter/),
[Amiri](https://www.amirifont.org/),
[Cairo](https://fonts.google.com/specimen/Cairo).

---

## Roadmap

- [ ] `formal` domain — government letters, compliance documents
- [ ] `personal` domain — CVs, cover letters
- [ ] `marketing-pitch` domain — launch decks, investor one-pagers
- [ ] `editorial` domain — articles, white papers, thought leadership
- [ ] `/katib reflect` — replay + learn from captured feedback
- [ ] Mermaid-to-SVG helper (optional, opt-in)
- [ ] Native Windows via GTK3 runtime bundling (community contributions welcome)

Contributions welcome — open an issue first to discuss a new domain.
