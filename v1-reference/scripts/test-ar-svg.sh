#!/usr/bin/env bash
# test-ar-svg.sh — verify the Arabic-in-SVG CSS lint rule.
#
# Writes a minimal bad AR template (Arabic <text> inside <svg>) to a scratch
# domain directory and confirms `build.py --check` rejects it. Verifies the
# same rule does NOT fire on a good template (Arabic in HTML overlay, not SVG).
#
# Exits 0 on success, non-zero on any assertion failure.

set -u  # unset variables are errors (but not -e; we check exit codes explicitly)

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; exit 1; }

echo "▶ test-ar-svg: Arabic-in-SVG lint rule"

# Mirror the skill into a scratch root so we can inject a bad template without
# touching the real domains dir.
cp -R "$SKILL_ROOT/domains" "$TMPDIR/domains"
cp -R "$SKILL_ROOT/scripts" "$TMPDIR/scripts"
cp -R "$SKILL_ROOT/styles" "$TMPDIR/styles"
cp -R "$SKILL_ROOT/references" "$TMPDIR/references"
[ -d "$SKILL_ROOT/brands" ] && cp -R "$SKILL_ROOT/brands" "$TMPDIR/brands"
cp "$SKILL_ROOT/config.example.yaml" "$TMPDIR/config.example.yaml"

# ─── Case 1: clean skill — lint passes ────────────────────────────────
echo "▶ Step 1: clean skill passes --check"
if (cd "$TMPDIR" && uv run --quiet scripts/build.py --check >/dev/null 2>&1); then
  pass "clean skill passes"
else
  fail "clean skill should pass --check but failed"
fi

# ─── Case 2: inject bad template — lint must reject ───────────────────
echo "▶ Step 2: bad AR template triggers violation"
BAD_TEMPLATE="$TMPDIR/domains/tutorial/templates/__bad-ar-svg.ar.html"
cat > "$BAD_TEMPLATE" <<'EOF'
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>bad</title></head>
<body>
  <svg viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg">
    <text x="50" y="20" text-anchor="middle">كاتب</text>
  </svg>
</body>
</html>
EOF

OUT=$(cd "$TMPDIR" && uv run --quiet scripts/build.py --check 2>&1)
RC=$?
if [ $RC -eq 0 ]; then
  fail "bad template should fail --check but passed: $OUT"
else
  pass "lint rejected bad template (exit $RC)"
fi

if echo "$OUT" | grep -q "Arabic text in SVG"; then
  pass "violation mentions 'Arabic text in SVG'"
else
  fail "violation message missing 'Arabic text in SVG'; got: $OUT"
fi

if echo "$OUT" | grep -q "diagram-stage"; then
  pass "violation points at the overlay pattern"
else
  fail "violation should reference '.diagram-stage' primitive"
fi

if echo "$OUT" | grep -q "__bad-ar-svg.ar.html"; then
  pass "violation names the offending file"
else
  fail "violation should name '__bad-ar-svg.ar.html'"
fi

rm "$BAD_TEMPLATE"

# ─── Case 3: good AR template with overlay — lint passes ──────────────
echo "▶ Step 3: overlay pattern passes --check"
GOOD_TEMPLATE="$TMPDIR/domains/tutorial/templates/__good-ar-svg.ar.html"
cat > "$GOOD_TEMPLATE" <<'EOF'
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>good</title>
<style>
.diagram-stage { position: relative; }
.diagram-label { position: absolute; direction: rtl; }
</style>
</head>
<body>
  <div class="diagram-stage">
    <svg viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="10" width="80" height="20" rx="4" fill="#F59E0B"/>
    </svg>
    <div class="diagram-label" style="left:50%;top:50%;">كاتب</div>
  </div>
</body>
</html>
EOF

if (cd "$TMPDIR" && uv run --quiet scripts/build.py --check >/dev/null 2>&1); then
  pass "good overlay template passes"
else
  OUT=$(cd "$TMPDIR" && uv run --quiet scripts/build.py --check 2>&1)
  fail "good template should pass but failed: $OUT"
fi

rm "$GOOD_TEMPLATE"

# ─── Case 4: English text inside SVG — lint allows ────────────────────
echo "▶ Step 4: English text in SVG passes (no false positive)"
EN_IN_AR_TEMPLATE="$TMPDIR/domains/tutorial/templates/__en-in-svg.ar.html"
cat > "$EN_IN_AR_TEMPLATE" <<'EOF'
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>en in svg</title></head>
<body>
  <svg viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg">
    <text x="50" y="20" text-anchor="middle">build.py</text>
  </svg>
</body>
</html>
EOF

if (cd "$TMPDIR" && uv run --quiet scripts/build.py --check >/dev/null 2>&1); then
  pass "English-only SVG text in AR template is allowed"
else
  OUT=$(cd "$TMPDIR" && uv run --quiet scripts/build.py --check 2>&1)
  fail "English SVG text should pass but lint rejected: $OUT"
fi

rm "$EN_IN_AR_TEMPLATE"

echo ""
echo "✓ test-ar-svg passed"
