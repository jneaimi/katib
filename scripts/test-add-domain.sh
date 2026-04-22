#!/usr/bin/env bash
# test-add-domain.sh — verify the add_domain.py scaffolder end-to-end.
#
# Mirrors the real skill into a scratch dir so generated files + SKILL.md
# patches don't pollute the live skill. Asserts:
#   - tokens.json + styles.json + 2×N templates land in the right places
#   - build.py --check passes on the scratch skill
#   - a render survives (EN + AR), producing a non-empty PDF
#   - SKILL.md gets exactly one router row + one doc-type row (idempotent on re-run)
#   - --dry-run writes nothing
#   - refuses to overwrite without --force
#
# Exits 0 on success, non-zero on any assertion failure.

set -u

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; exit 1; }

echo "▶ test-add-domain: scaffold + verify a new domain"

# Mirror only what add_domain.py + build.py need.
cp -R "$SKILL_ROOT/domains"     "$TMPDIR/domains"
cp -R "$SKILL_ROOT/scripts"     "$TMPDIR/scripts"
cp -R "$SKILL_ROOT/styles"      "$TMPDIR/styles"
cp -R "$SKILL_ROOT/references"  "$TMPDIR/references"
[ -d "$SKILL_ROOT/brands" ] && cp -R "$SKILL_ROOT/brands" "$TMPDIR/brands"
cp "$SKILL_ROOT/config.example.yaml" "$TMPDIR/config.example.yaml"
cp "$SKILL_ROOT/SKILL.md" "$TMPDIR/SKILL.md"

# Fixture spec: memo domain, slate palette, 2 doc types
SPEC="$TMPDIR/memo-spec.json"
cat > "$SPEC" <<'EOF'
{
  "description_en": "Short internal memos and agendas.",
  "description_ar": "مذكرات وجداول أعمال داخلية",
  "palette": "slate",
  "fonts": "sans-modern",
  "default_cover": "minimalist-typographic",
  "default_layout": "classic",
  "covers_allowed": ["minimalist-typographic"],
  "layouts_allowed": ["classic"],
  "doc_types": [
    {"name": "memo", "page_limit": 3, "target_pages": [1, 2], "rc_prefix": "MEMO-"},
    {"name": "agenda", "page_limit": 2, "target_pages": [1, 2], "rc_prefix": "AGD-"}
  ],
  "router_signals": "memo / agenda / تذكرة / مذكرة داخلية"
}
EOF

# ─── Case 1: --dry-run writes nothing ─────────────────────────────────
echo "▶ Step 1: --dry-run writes nothing"
(cd "$TMPDIR" && python3 scripts/add_domain.py memo --from-json "$SPEC" --dry-run >/dev/null 2>&1)
if [ -d "$TMPDIR/domains/memo" ]; then
  fail "--dry-run created files"
else
  pass "--dry-run left filesystem clean"
fi

# ─── Case 2: scaffold lands all artifacts ─────────────────────────────
echo "▶ Step 2: scaffold writes tokens/styles/templates"
(cd "$TMPDIR" && python3 scripts/add_domain.py memo --from-json "$SPEC" >/dev/null 2>&1) || fail "scaffolder exited non-zero"

for f in \
  "domains/memo/tokens.json" \
  "domains/memo/styles.json" \
  "domains/memo/templates/memo.en.html" \
  "domains/memo/templates/memo.ar.html" \
  "domains/memo/templates/agenda.en.html" \
  "domains/memo/templates/agenda.ar.html"
do
  [ -s "$TMPDIR/$f" ] || fail "missing or empty: $f"
done
pass "all 6 expected files written"

# ─── Case 3: tokens.json structure ────────────────────────────────────
echo "▶ Step 3: tokens.json is well-formed"
python3 -c "
import json, sys
d = json.load(open('$TMPDIR/domains/memo/tokens.json'))
assert d['domain'] == 'memo', f\"domain={d['domain']!r}\"
assert '--accent' in d['semantic_colors'], 'missing --accent'
assert 'en' in d['fonts'] and 'ar' in d['fonts'], 'missing fonts'
assert d['fonts']['en']['primary'] == 'Inter', f\"EN font={d['fonts']['en']['primary']!r}\"
assert d['fonts']['ar']['primary'] == 'Cairo', f\"AR font={d['fonts']['ar']['primary']!r}\"
" || fail "tokens.json malformed"
pass "tokens.json has correct structure + fonts"

# ─── Case 4: styles.json structure ────────────────────────────────────
echo "▶ Step 4: styles.json is well-formed"
python3 -c "
import json
d = json.load(open('$TMPDIR/domains/memo/styles.json'))
assert set(d['doc_types']) == {'memo', 'agenda'}, f\"doc_types={list(d['doc_types'])}\"
assert d['doc_types']['memo']['page_limit'] == 3
assert d['defaults']['layout'] == 'classic'
" || fail "styles.json malformed"
pass "styles.json has correct doc_types + defaults"

# ─── Case 5: build.py --check passes ──────────────────────────────────
echo "▶ Step 5: build.py --check passes on scaffolded skill"
if (cd "$TMPDIR" && python3 scripts/build.py --check >/dev/null 2>&1); then
  pass "--check passed"
else
  OUT=$(cd "$TMPDIR" && python3 scripts/build.py --check 2>&1)
  fail "--check failed: $OUT"
fi

# ─── Case 6: EN render produces a non-empty PDF ───────────────────────
echo "▶ Step 6: EN render produces a PDF"
OUT_ROOT="$TMPDIR/out"
mkdir -p "$OUT_ROOT"
if (cd "$TMPDIR" && KATIB_OUTPUT_ROOT="$OUT_ROOT" uv run --quiet scripts/build.py memo --domain memo --lang en --title "Test Memo" >/dev/null 2>&1); then
  PDF=$(find "$OUT_ROOT" -name "memo.en.pdf" | head -1)
  if [ -s "$PDF" ]; then
    pass "EN PDF produced: $(basename "$PDF")"
  else
    fail "EN PDF missing or empty"
  fi
else
  fail "EN build failed"
fi

# ─── Case 7: AR render produces a non-empty PDF ───────────────────────
echo "▶ Step 7: AR render produces a PDF"
if (cd "$TMPDIR" && KATIB_OUTPUT_ROOT="$OUT_ROOT" uv run --quiet scripts/build.py memo --domain memo --lang ar --title "مذكرة" >/dev/null 2>&1); then
  PDF=$(find "$OUT_ROOT" -name "memo.ar.pdf" | head -1)
  if [ -s "$PDF" ]; then
    pass "AR PDF produced: $(basename "$PDF")"
  else
    fail "AR PDF missing or empty"
  fi
else
  fail "AR build failed"
fi

# ─── Case 8: SKILL.md patched correctly ───────────────────────────────
echo "▶ Step 8: SKILL.md has router + doc-type rows"
ROUTER_HITS=$(grep -c '"memo / agenda' "$TMPDIR/SKILL.md" || true)
DOC_HITS=$(grep -c '| `memo` | `memo`, `agenda` |' "$TMPDIR/SKILL.md" || true)
[ "$ROUTER_HITS" = "1" ] || fail "router row count = $ROUTER_HITS (expected 1)"
[ "$DOC_HITS"    = "1" ] || fail "doc-type row count = $DOC_HITS (expected 1)"
pass "SKILL.md has exactly one router row and one doc-type row"

# Router row lives in Step 2 table (before "All planned domains are live.")
# Doc-type row lives in Step 3 table (after legal doc-type row).
ROUTER_LINE=$(grep -n '"memo / agenda' "$TMPDIR/SKILL.md" | head -1 | cut -d: -f1)
ANCHOR_LINE=$(grep -n 'All planned domains are live' "$TMPDIR/SKILL.md" | head -1 | cut -d: -f1)
if [ "$ROUTER_LINE" -lt "$ANCHOR_LINE" ]; then
  pass "router row placed before 'All planned domains' anchor"
else
  fail "router row at L$ROUTER_LINE is AFTER anchor at L$ANCHOR_LINE"
fi

# ─── Case 9: refuses to overwrite without --force ─────────────────────
echo "▶ Step 9: refuses to overwrite without --force"
if (cd "$TMPDIR" && python3 scripts/add_domain.py memo --from-json "$SPEC" >/dev/null 2>&1); then
  fail "scaffolder should refuse to overwrite but exited 0"
else
  pass "scaffolder refused to overwrite existing domain"
fi

# ─── Case 10: --force overwrites and stays idempotent on SKILL.md ─────
echo "▶ Step 10: --force overwrites; SKILL.md stays single-row"
if (cd "$TMPDIR" && python3 scripts/add_domain.py memo --from-json "$SPEC" --force >/dev/null 2>&1); then
  ROUTER_HITS=$(grep -c '"memo / agenda' "$TMPDIR/SKILL.md" || true)
  DOC_HITS=$(grep -c '| `memo` | `memo`, `agenda` |' "$TMPDIR/SKILL.md" || true)
  [ "$ROUTER_HITS" = "1" ] || fail "after --force router count = $ROUTER_HITS (should stay 1)"
  [ "$DOC_HITS"    = "1" ] || fail "after --force doc-type count = $DOC_HITS (should stay 1)"
  pass "--force re-scaffolded and SKILL.md stayed idempotent"
else
  fail "--force should have succeeded"
fi

# ─── Case 11: invalid name rejected ───────────────────────────────────
echo "▶ Step 11: invalid name rejected"
if (cd "$TMPDIR" && python3 scripts/add_domain.py "Bad_Name" --from-json "$SPEC" >/dev/null 2>&1); then
  fail "scaffolder should reject invalid name but exited 0"
else
  pass "invalid name (underscore + capitals) rejected"
fi

echo ""
echo "✓ test-add-domain passed (11 steps)"
