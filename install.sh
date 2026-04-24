#!/usr/bin/env bash
# Katib installer — drops the skill into ~/.claude/skills/katib/ and wires up config.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/jneaimi/katib/main/install.sh | bash
#   # or, after cloning:
#   bash install.sh
#
# What it does:
#   1. Checks prereqs (git, python3.11+, uv, WeasyPrint system libs)
#   2. Clones this repo to ~/.claude/skills/katib/ (or pulls if already installed)
#   3. Runs `uv run playwright install chromium` (for the screenshot module)
#   4. Seeds ~/.katib/brands/example.yaml and ~/.config/katib/config.yaml
#   5. Prompts for a Gemini API key (optional — only needed for image-based covers)
#
# Re-running is safe: update mode will `git pull` and leave user configs alone.

set -euo pipefail

# ---------- style ----------
BOLD=$'\e[1m'; DIM=$'\e[2m'; RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; CYAN=$'\e[36m'; RESET=$'\e[0m'
say()  { printf "%s\n" "$*"; }
info() { printf "${CYAN}▶${RESET} %s\n" "$*"; }
ok()   { printf "${GREEN}✓${RESET} %s\n" "$*"; }
warn() { printf "${YELLOW}⚠${RESET} %s\n" "$*"; }
fail() { printf "${RED}✗${RESET} %s\n" "$*" >&2; exit 1; }

say ""
say "${BOLD}Katib — bilingual PDF document skill${RESET}"
say "${DIM}Installs to ~/.claude/skills/katib/${RESET}"
say ""

# ---------- 1. Prereq checks ----------
info "Checking prerequisites"

command -v git >/dev/null 2>&1 || fail "git not found. Install it from https://git-scm.com/downloads"

PYTHON_BIN="$(command -v python3 || true)"
[ -n "$PYTHON_BIN" ] || fail "python3 not found. Install Python 3.11+ (https://www.python.org/downloads/)"
PY_VER="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_MAJOR="${PY_VER%%.*}"
PY_MINOR="${PY_VER##*.}"
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
  fail "python3 is $PY_VER — Katib needs 3.11 or newer."
fi

if ! command -v uv >/dev/null 2>&1; then
  warn "uv not found — installing via the official one-liner"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck source=/dev/null
  [ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"
  [ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env"
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  command -v uv >/dev/null 2>&1 || fail "uv install finished but 'uv' isn't on PATH. Restart your shell and re-run."
fi

ok "git, python3 ($PY_VER), uv"

# ---------- 2. WeasyPrint system libs ----------
info "Checking WeasyPrint system libraries (Pango / Cairo)"

if ! uv run --quiet --with "weasyprint>=60" python3 -c "import weasyprint" 2>/dev/null; then
  OS_NAME="$(uname -s)"
  say ""
  warn "WeasyPrint can't load — system libs are missing (Pango / Cairo / GDK-Pixbuf)."
  say ""
  say "Install them, then re-run this installer:"
  case "$OS_NAME" in
    Darwin)
      say "  ${BOLD}brew install pango cairo gdk-pixbuf libffi${RESET}"
      ;;
    Linux)
      if   command -v apt-get >/dev/null 2>&1; then
        say "  ${BOLD}sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev${RESET}"
      elif command -v dnf     >/dev/null 2>&1; then
        say "  ${BOLD}sudo dnf install pango cairo gdk-pixbuf2 libffi-devel${RESET}"
      elif command -v pacman  >/dev/null 2>&1; then
        say "  ${BOLD}sudo pacman -S pango cairo gdk-pixbuf2 libffi${RESET}"
      else
        say "  See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html for your distro"
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*)
      say "  Native Windows isn't supported — use WSL2 (Ubuntu), then run the Linux install from there."
      ;;
    *)
      say "  See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
      ;;
  esac
  say ""
  exit 1
fi

ok "WeasyPrint loads cleanly"

# ---------- 3. Install / update the skill ----------
SKILL_DIR="$HOME/.claude/skills/katib"
REPO_URL="${KATIB_REPO_URL:-https://github.com/jneaimi/katib.git}"

mkdir -p "$HOME/.claude/skills"

if [ -d "$SKILL_DIR/.git" ]; then
  info "Katib already installed at $SKILL_DIR — updating"
  git -C "$SKILL_DIR" pull --ff-only --quiet
  ok "updated to $(git -C "$SKILL_DIR" rev-parse --short HEAD)"
elif [ -d "$SKILL_DIR" ] && [ -n "$(ls -A "$SKILL_DIR" 2>/dev/null || true)" ]; then
  fail "$SKILL_DIR exists and isn't a katib git checkout. Move it aside and re-run."
else
  info "Cloning to $SKILL_DIR"
  rm -rf "$SKILL_DIR" 2>/dev/null || true
  git clone --depth 1 --quiet "$REPO_URL" "$SKILL_DIR"
  ok "cloned"
fi

# ---------- 4. Playwright (optional — screenshot module) ----------
info "Installing Playwright Chromium (for tutorial screenshots)"
if uv run --quiet --with "playwright>=1.40" playwright install chromium >/dev/null 2>&1; then
  ok "Playwright ready"
else
  warn "Playwright install skipped — screenshot module won't work until you run:"
  say "  ${BOLD}uv run --with playwright playwright install chromium${RESET}"
fi

# ---------- 5. User directories + config ----------
info "Setting up user directories"
mkdir -p "$HOME/.katib/brands" \
         "$HOME/.katib/recipes" \
         "$HOME/.katib/components/primitives" \
         "$HOME/.katib/components/sections" \
         "$HOME/.katib/components/covers" \
         "$HOME/.katib/memory" \
         "$HOME/.config/katib"

# Seed brands/example.yaml if missing
if [ ! -f "$HOME/.katib/brands/example.yaml" ]; then
  cp "$SKILL_DIR/brands/example.yaml" "$HOME/.katib/brands/example.yaml"
  ok "seeded ~/.katib/brands/example.yaml"
else
  ok "~/.katib/brands/example.yaml already exists (left alone)"
fi

# Seed starter recipes on fresh install only.
# "Fresh install" = ~/.katib/recipes/ is empty. Returning users are left
# untouched so their edits, custom recipes, and intentional deletions all
# survive upgrades. Use `uv run scripts/seed.py refresh <name>` to opt back
# into a specific starter after the fact.
if [ -f "$SKILL_DIR/seed-manifest.yaml" ]; then
  if [ -z "$(ls -A "$HOME/.katib/recipes" 2>/dev/null || true)" ]; then
    info "Seeding starter recipes to ~/.katib/recipes/"
    # Run the seed CLI against $HOME/.katib/recipes via the env var.
    # Emit JSON so parsing is robust even if output formatting changes.
    SEED_OUTPUT="$(
      KATIB_RECIPES_DIR="$HOME/.katib/recipes" \
      KATIB_MEMORY_DIR="$HOME/.katib/memory" \
      uv --project "$SKILL_DIR" run --quiet python "$SKILL_DIR/scripts/seed.py" \
        --json refresh --all 2>/dev/null || true
    )"
    if [ -n "$SEED_OUTPUT" ]; then
      SEEDED_COUNT="$(printf '%s' "$SEED_OUTPUT" | \
        python3 -c 'import json,sys; d=json.load(sys.stdin); print(sum(1 for r in d.get("results", []) if r.get("action")=="seeded"))' 2>/dev/null || echo "0")"
      ok "seeded $SEEDED_COUNT starter recipes into ~/.katib/recipes/"
    else
      warn "seed step skipped — scripts/seed.py didn't return output"
    fi
  else
    ok "~/.katib/recipes/ already populated (left alone)"
  fi
fi

# Seed ~/.config/katib/config.yaml with a vault-aware default
CONFIG_FILE="$HOME/.config/katib/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
  if [ -d "$HOME/vault" ]; then
    DEFAULT_DEST="vault"
    DEFAULT_OUT="~/vault/content/katib"
  else
    DEFAULT_DEST="custom"
    DEFAULT_OUT="~/Documents/katib"
  fi
  cat > "$CONFIG_FILE" <<EOF
# Katib user config — edit freely.
# Precedence: CLI flag → <project>/.katib/config.yaml → this file → skill default.

output:
  destination: $DEFAULT_DEST
  vault_path: ~/vault/content/katib
  custom_path: $DEFAULT_OUT
  always_create_manifest: true

memory:
  location: ~/.katib/memory
  per_domain_rollup: true

identity:
  author_name: ""
  author_email: ""
  company: ""
  signature_path: ~/.config/katib/signature.png

image_model:
  provider: gemini
  model: nano-banana-2
  fallback: gemini-2.5-flash-image
  api_key_env: GEMINI_API_KEY
EOF
  ok "wrote $CONFIG_FILE (output → $DEFAULT_OUT)"
else
  ok "$CONFIG_FILE already exists (left alone)"
fi

# ---------- 6. Gemini API key ----------
say ""
info "Gemini API key (optional)"
say "${DIM}Used for image-based cover styles (neural-cartography, friendly-illustration).${RESET}"
say "${DIM}The minimalist-typographic cover works without any key — skip this if you're unsure.${RESET}"
say ""

if [ -n "${GEMINI_API_KEY:-}" ]; then
  ok "GEMINI_API_KEY already set in this shell — nothing to do."
else
  # Only prompt if we're running interactively
  if [ -t 0 ]; then
    say "Get a key at: ${BOLD}https://aistudio.google.com/apikey${RESET}"
    say ""
    printf "Paste your key now, or press Enter to skip: "
    read -r GEMINI_KEY_INPUT
    if [ -n "$GEMINI_KEY_INPUT" ]; then
      # Pick shell rc
      SHELL_RC=""
      case "${SHELL:-}" in
        */zsh) SHELL_RC="$HOME/.zshrc" ;;
        */bash)
          if [ -f "$HOME/.bash_profile" ]; then SHELL_RC="$HOME/.bash_profile"; else SHELL_RC="$HOME/.bashrc"; fi
          ;;
        *) SHELL_RC="$HOME/.profile" ;;
      esac
      printf "Append 'export GEMINI_API_KEY=...' to %s? [Y/n] " "$SHELL_RC"
      read -r APPEND_OK
      if [ -z "$APPEND_OK" ] || [ "$APPEND_OK" = "y" ] || [ "$APPEND_OK" = "Y" ]; then
        {
          printf "\n# Katib — Gemini API key (added by install.sh)\n"
          printf "export GEMINI_API_KEY=%q\n" "$GEMINI_KEY_INPUT"
        } >> "$SHELL_RC"
        ok "wrote key to $SHELL_RC — open a new shell or 'source $SHELL_RC' to load"
      else
        warn "Skipped. Set GEMINI_API_KEY yourself before using image-based covers."
      fi
    else
      warn "Skipped. Set GEMINI_API_KEY later if you want image-based covers."
    fi
  else
    warn "Non-interactive install — skipping Gemini prompt. Set GEMINI_API_KEY yourself."
  fi
fi

# ---------- Done ----------
say ""
say "${BOLD}${GREEN}✓ Katib installed${RESET}"
say ""
say "  Skill:      $SKILL_DIR"
say "  Config:     $CONFIG_FILE"
say "  Brands:     $HOME/.katib/brands/"
say "  Recipes:    $HOME/.katib/recipes/          ${DIM}(your custom recipes live here — survive reinstall)${RESET}"
say "  Components: $HOME/.katib/components/       ${DIM}(your custom components — survive reinstall)${RESET}"
say "  Memory:     $HOME/.katib/memory/"
say ""
say "Next: restart Claude Code, then invoke ${BOLD}/katib${RESET} in any conversation."
say ""
