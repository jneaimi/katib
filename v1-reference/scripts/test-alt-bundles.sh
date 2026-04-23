#!/usr/bin/env bash
# Smoke-test: verify shot.py writes per-language alt/caption bundles and
# build.py's discover_screenshots resolves them correctly per render lang.
#
# No Playwright, no PDF render — constructs a synthetic sidecar + fake PNG
# and calls discover_screenshots directly.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SKILL_DIR"

WORK="$(mktemp -d)"
SHOT_DIR="$WORK/assets/screenshots"
mkdir -p "$SHOT_DIR"

echo "▶ Katib alt-text bundle smoke test"
echo "  workdir: $WORK"
echo ""

# ===== 1. resolve_text_bundle helper =====
echo "▶ Step 1: shot.py resolve_text_bundle"
uv run --quiet python3 -c "
import sys; sys.path.insert(0, 'scripts')
from shot import resolve_text_bundle as r
assert r(None, None, None) is None, 'all-None should be None'
assert r('legacy', None, None) == 'legacy', 'legacy-only stays str'
assert r(None, 'hi', None) == {'en': 'hi'}, 'en-only becomes dict'
assert r(None, None, 'مرحبا') == {'ar': 'مرحبا'}, 'ar-only becomes dict'
assert r(None, 'hi', 'مرحبا') == {'en': 'hi', 'ar': 'مرحبا'}, 'both become dict'
assert r('legacy', 'hi', None) == {'en': 'hi', 'ar': 'legacy'}, 'legacy fills missing ar'
print('  ✓ all 6 cases pass')
"

# ===== 2. _resolve_text_for_lang helper =====
echo ""
echo "▶ Step 2: build.py _resolve_text_for_lang"
uv run --quiet python3 -c "
import sys; sys.path.insert(0, 'scripts')
from build import _resolve_text_for_lang as r
assert r('plain', 'en') == ('plain', False), 'legacy str no fallback'
assert r('plain', 'ar') == ('plain', False), 'legacy str ignores lang'
assert r({'en': 'hi', 'ar': 'مرحبا'}, 'en') == ('hi', False), 'en matches'
assert r({'en': 'hi', 'ar': 'مرحبا'}, 'ar') == ('مرحبا', False), 'ar matches'
assert r({'en': 'hi'}, 'ar') == ('hi', True), 'ar falls back to en flagged'
assert r({'ar': 'مرحبا'}, 'en') == ('', False), 'en missing, no ar-fallback'
assert r({}, 'ar') == ('', False), 'empty dict'
assert r('', 'en') == ('', False), 'empty str'
assert r(None, 'en') == ('', False), 'None'
print('  ✓ all 9 cases pass')
"

# ===== 3. End-to-end: discover_screenshots on a synthetic folder =====
echo ""
echo "▶ Step 3: discover_screenshots with a mixed legacy+bundle folder"

# Write a fake PNG (empty; discover_screenshots doesn't open it)
printf 'fake' > "$SHOT_DIR/step-1.png"
printf 'fake' > "$SHOT_DIR/step-2.png"
printf 'fake' > "$SHOT_DIR/step-3.png"

# step-1: legacy sidecar — single string (should appear identical in both langs)
cat > "$SHOT_DIR/step-1.meta.json" <<'JSON'
{
  "type": "screenshot",
  "url": "https://example.com/step-1",
  "viewport": {"width": 1440, "height": 900},
  "alt": "login page",
  "caption": "the login form"
}
JSON

# step-2: bundle sidecar — EN + AR
cat > "$SHOT_DIR/step-2.meta.json" <<'JSON'
{
  "type": "screenshot",
  "url": "https://example.com/step-2",
  "viewport": {"width": 1440, "height": 900},
  "alt": {"en": "dashboard view", "ar": "لوحة التحكم"},
  "caption": {"en": "your dashboard after login", "ar": "لوحة التحكم بعد تسجيل الدخول"}
}
JSON

# step-3: EN-only bundle — AR render should fall back to EN and emit a warning
cat > "$SHOT_DIR/step-3.meta.json" <<'JSON'
{
  "type": "screenshot",
  "url": "https://example.com/step-3",
  "viewport": {"width": 1440, "height": 900},
  "alt": {"en": "settings panel"},
  "caption": {"en": "click to configure"}
}
JSON

uv run --quiet python3 -c "
import sys, json
sys.path.insert(0, 'scripts')
from pathlib import Path
from build import discover_screenshots

folder = Path('$WORK')

# EN render
en = discover_screenshots(folder, 'en')
assert en['step_1']['caption'] == 'the login form', f'legacy caption: {en[\"step_1\"]}'
assert en['step_2']['caption'] == 'your dashboard after login', f'bundle en caption: {en[\"step_2\"]}'
assert en['step_3']['caption'] == 'click to configure', f'en-only ok: {en[\"step_3\"]}'
print('  ✓ EN render: 3/3 captions resolved')

# AR render
ar = discover_screenshots(folder, 'ar')
assert ar['step_1']['caption'] == 'the login form', f'legacy passes through: {ar[\"step_1\"]}'
assert ar['step_2']['caption'] == 'لوحة التحكم بعد تسجيل الدخول', f'bundle ar caption: {ar[\"step_2\"]}'
assert ar['step_3']['caption'] == 'click to configure', f'ar fallback to en: {ar[\"step_3\"]}'
print('  ✓ AR render: 3/3 captions resolved')
" 2> "$WORK/stderr.log"

# Check fallback warning fired once for AR on step-3
if grep -q "screenshot 'step-3': caption missing for lang='ar'" "$WORK/stderr.log"; then
  echo "  ✓ fallback warning fired for step-3 in AR render"
else
  echo "  ✗ fallback warning NOT fired for step-3"
  echo "    stderr was:"
  cat "$WORK/stderr.log"
  exit 1
fi

echo ""
echo "✓ Alt-text bundle smoke test passed"
