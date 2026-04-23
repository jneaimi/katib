#!/usr/bin/env bash
# test-install-fonts.sh — verify install_fonts.py end-to-end.
#
# Network tests fetch one small font (JetBrains Mono, ~180 KB) from
# github.com/google/fonts. Skipped automatically if offline.
#
# Asserts:
#   - --list works offline (no network)
#   - --dry-run writes nothing
#   - scratch install fetches the expected file with non-trivial size
#   - re-run is idempotent (skipped count goes up)
#   - --verify distinguishes installed vs missing
#   - unknown --only family is rejected
#
# Exits 0 on success, non-zero on any assertion failure.

set -u

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; exit 1; }

echo "▶ test-install-fonts: scaffolder + installer"

SCRIPT="$SKILL_ROOT/scripts/install_fonts.py"
FONT_DIR="$TMPDIR/fonts"

# ─── Case 1: --list works offline ─────────────────────────────────────
echo "▶ Step 1: --list works without network"
OUT=$(python3 "$SCRIPT" --list 2>&1)
echo "$OUT" | grep -q "Cairo"              || fail "--list missing Cairo"
echo "$OUT" | grep -q "Amiri"              || fail "--list missing Amiri"
echo "$OUT" | grep -q "JetBrains Mono"     || fail "--list missing JetBrains Mono"
echo "$OUT" | grep -q "Total: 7 families"  || fail "--list wrong family count"
pass "--list prints all 7 families"

# ─── Case 2: unknown --only rejected ──────────────────────────────────
echo "▶ Step 2: unknown --only family rejected"
if python3 "$SCRIPT" --list --only "BogusFont" >/dev/null 2>&1; then
  fail "unknown family should be rejected"
else
  pass "unknown family rejected (exit != 0)"
fi

# ─── Probe: can we reach github.com ? ─────────────────────────────────
if ! curl -s --max-time 5 -o /dev/null -w "%{http_code}" https://github.com | grep -qE '^(200|301|302)$'; then
  echo ""
  echo "⚠ No network to github.com — skipping live-fetch tests"
  echo "✓ test-install-fonts passed (2 offline steps)"
  exit 0
fi

# ─── Case 3: --dry-run writes nothing ─────────────────────────────────
echo "▶ Step 3: --dry-run writes nothing"
python3 "$SCRIPT" --only "JetBrains Mono" --target "$FONT_DIR" --dry-run >/dev/null 2>&1
[ -d "$FONT_DIR" ] && fail "--dry-run created install dir"
pass "--dry-run left filesystem clean"

# ─── Case 4: live fetch of JetBrains Mono ─────────────────────────────
echo "▶ Step 4: fetch JetBrains Mono (small variable font)"
OUT=$(python3 "$SCRIPT" --only "JetBrains Mono" --target "$FONT_DIR" 2>&1)
echo "$OUT" | grep -q "fetched=2" || fail "expected fetched=2, got: $OUT"
ROMAN="$FONT_DIR/JetBrainsMono[wght].ttf"
[ -s "$ROMAN" ] || fail "JetBrainsMono[wght].ttf missing or empty"
SIZE=$(wc -c < "$ROMAN")
[ "$SIZE" -gt 100000 ] || fail "font file suspiciously small ($SIZE bytes)"
pass "JetBrainsMono[wght].ttf installed ($SIZE bytes)"

# ─── Case 5: re-run is idempotent (skipped, not re-fetched) ───────────
echo "▶ Step 5: re-run skips existing files"
OUT=$(python3 "$SCRIPT" --only "JetBrains Mono" --target "$FONT_DIR" 2>&1)
echo "$OUT" | grep -q "fetched=0" || fail "expected fetched=0 on re-run, got: $OUT"
echo "$OUT" | grep -q "skipped=2" || fail "expected skipped=2 on re-run, got: $OUT"
pass "re-run skipped both files"

# ─── Case 6: --force re-fetches even when present ─────────────────────
echo "▶ Step 6: --force re-fetches"
MTIME_BEFORE=$(stat -f %m "$ROMAN" 2>/dev/null || stat -c %Y "$ROMAN")
sleep 1  # ensure mtime can change
OUT=$(python3 "$SCRIPT" --only "JetBrains Mono" --target "$FONT_DIR" --force 2>&1)
echo "$OUT" | grep -q "fetched=2" || fail "expected fetched=2 with --force, got: $OUT"
MTIME_AFTER=$(stat -f %m "$ROMAN" 2>/dev/null || stat -c %Y "$ROMAN")
[ "$MTIME_AFTER" -gt "$MTIME_BEFORE" ] || fail "--force did not refresh mtime"
pass "--force re-fetched and updated mtime"

# ─── Case 7: --verify distinguishes installed vs missing ──────────────
echo "▶ Step 7: --verify shows installed + missing correctly"
OUT=$(python3 "$SCRIPT" --verify --target "$FONT_DIR" 2>&1)
# installed: 2 JetBrainsMono files; missing: remaining 16 files across other families
INSTALLED=$(echo "$OUT" | grep -c "✓ " || true)
[ "$INSTALLED" = "2" ] || fail "expected 2 installed, got $INSTALLED"
MISSING_LINE=$(echo "$OUT" | grep "installed=" | tail -1)
echo "$MISSING_LINE" | grep -q "missing=16" || fail "expected missing=16, got: $MISSING_LINE"
pass "--verify correctly reported 2 installed / 16 missing"

# ─── Case 8: --only subset (Amiri, static font) ───────────────────────
echo "▶ Step 8: fetch Amiri-Regular (static, non-bracket filename)"
OUT=$(python3 "$SCRIPT" --only "Amiri" --target "$FONT_DIR" 2>&1)
echo "$OUT" | grep -q "fetched=4" || fail "expected fetched=4 for Amiri, got: $OUT"
[ -s "$FONT_DIR/Amiri-Regular.ttf" ] || fail "Amiri-Regular.ttf missing"
pass "Amiri family (4 static files) fetched"

echo ""
echo "✓ test-install-fonts passed (8 steps, live network)"
