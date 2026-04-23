# Brand profiles

Brand profiles let you swap the visual identity of a document — colors, fonts,
logo, author identity — per project or per client without editing templates.

## Where they live

```
~/.katib/brands/<name>.yaml     # user brands (created by install.sh)
~/.claude/skills/katib/brands/  # profiles shipped with the skill (example.yaml only)
```

Katib searches both locations. Your personal profiles belong in `~/.katib/brands/`.

## Using a profile

```bash
uv run scripts/build.py proposal --domain business-proposal --lang en --brand acme
uv run scripts/build.py --list-brands        # see what's available
uv run scripts/build.py ... --brand-file /path/to/custom.yaml
```

Precedence (last wins): domain defaults → brand profile → CLI flags.
A profile that omits a field keeps the domain default — partial brands are fine.

## Schema (v1.4)

```yaml
# Required
name: ACME Corp                         # string OR {en: ..., ar: ...}

# Optional — Arabic-specific variants (fall back to `name`, `legal_name`, etc.)
name_ar: شركة أكمي
legal_name: ACME Corp LLC
legal_name_ar: شركة أكمي ذ.م.م

# Author identity (overrides ~/.config/katib/config.yaml identity.*)
identity:
  author_name: Jane Doe
  email: jane@acme.example
  phone: "+1 555 0100"
# Optional Arabic identity block
identity_ar:
  author_name: جين دو

# Colors — all optional; unspecified keys inherit from the domain.
# Values must be valid CSS colors (hex, rgb(), hsl(), or named) — anything
# else is rejected at load time to block CSS injection.
colors:
  accent: "#1B2A4A"
  accent_2: "#C5A44E"
  accent_on: "#FFFFFF"
  page_bg: "#FAFAF8"
  text: "#1A1A1A"
  # ...and any of the other semantic keys — see config.example.yaml

# Fonts — optional per-language overrides
fonts:
  en:
    primary: "Inter"
    display: "Newsreader"
    fallback: "system-ui, sans-serif"
  ar:
    primary: "IBM Plex Arabic"
    display: "IBM Plex Arabic"
    fallback: "Cairo, Tahoma, sans-serif"

# Logo — shown on tutorial covers + business-proposal letterheads.
# Allowed formats: .png .jpg .jpeg .svg
logo: path/to/logo.svg                  # relative to this YAML file

# Or with sizing (max 200 mm):
# logo:
#   primary: path/to/logo.svg
#   max_height_mm: 18
```

Validation fails loudly at load time if:
- `name` is missing or empty
- a color value isn't a recognized CSS color
- `max_height_mm` is out of [1, 200]
- the logo's extension isn't in the whitelist
- `--brand-file` is passed together with `--brand` (warning, file wins)

## Example

See `example.yaml` in this folder for a fully commented template.
`installer` copies it to `~/.katib/brands/example.yaml` on first install.

## Bilingual rendering

- Document language is chosen with `--lang en|ar`.
- On Arabic renders, Katib picks `name_ar` / `legal_name_ar` / `identity_ar.*`
  when present, and falls back to the English field otherwise.
- `fonts.ar.*` activates on Arabic renders.
- Logos are language-neutral; use a single SVG that reads well in both contexts.
