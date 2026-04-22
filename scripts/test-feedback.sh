#!/usr/bin/env bash
# test-feedback.sh — verify the feedback.py CLI and its wiring into reflect.py.
#
# Writes a scratch project config that redirects memory.location to a temp
# dir, logs 3 identical corrections via `feedback.py add`, then runs
# `reflect.py --json --since all` and asserts the string-swap proposal fires.
# Also smoke-tests list, search, and argument validation.
#
# Exits 0 on success, non-zero on any assertion failure.

set -u

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; exit 1; }

echo "▶ test-feedback: feedback.py + reflect.py wiring"

FB="$SKILL_ROOT/scripts/feedback.py"
REFLECT="$SKILL_ROOT/scripts/reflect.py"

# Scratch project config — isolates memory dir so the live vault stays clean
mkdir -p "$TMPDIR/.katib"
cat > "$TMPDIR/.katib/config.yaml" <<EOF
output:
  destination: custom
  custom_path: $TMPDIR/out
memory:
  location: $TMPDIR/mem
EOF

MEM="$TMPDIR/mem"

# ─── Case 1: add requires all four core flags ─────────────────────────
echo "▶ Step 1: add rejects missing --after"
if (cd "$TMPDIR" && python3 "$FB" add --before "click" --domain tutorial --lang en >/dev/null 2>&1); then
  fail "add should reject missing --after"
else
  pass "add rejects missing --after"
fi

# ─── Case 2: add writes a row ─────────────────────────────────────────
echo "▶ Step 2: add writes to feedback.jsonl"
(cd "$TMPDIR" && python3 "$FB" add --before "click" --after "select" \
   --domain tutorial --lang en --reason "UI consistency" >/dev/null 2>&1) \
   || fail "add exited non-zero"

JSONL="$MEM/feedback.jsonl"
[ -s "$JSONL" ] || fail "feedback.jsonl missing or empty"
LINE_COUNT=$(wc -l < "$JSONL" | tr -d ' ')
[ "$LINE_COUNT" = "1" ] || fail "expected 1 line, got $LINE_COUNT"

# Verify the row has the expected shape
python3 -c "
import json
r = json.loads(open('$JSONL').read().splitlines()[0])
assert r['domain'] == 'tutorial', r
assert r['lang'] == 'en', r
assert r['before'] == 'click', r
assert r['after'] == 'select', r
assert r['reason'] == 'UI consistency', r
assert 'ts' in r, r
" || fail "row shape invalid"
pass "add wrote one well-formed row"

# ─── Case 3: add two more identical rows (total 3) ────────────────────
echo "▶ Step 3: add 2 more identical rows"
for i in 2 3; do
  (cd "$TMPDIR" && python3 "$FB" add --before "click" --after "select" \
     --domain tutorial --lang en --reason "run $i" >/dev/null 2>&1) \
     || fail "add #$i failed"
done
LINE_COUNT=$(wc -l < "$JSONL" | tr -d ' ')
[ "$LINE_COUNT" = "3" ] || fail "expected 3 lines, got $LINE_COUNT"
pass "3 rows present"

# ─── Case 4: list shows recent rows ───────────────────────────────────
echo "▶ Step 4: list shows rows"
OUT=$(cd "$TMPDIR" && python3 "$FB" list 2>&1)
echo "$OUT" | grep -q "'click' → 'select'" || fail "list missing the swap, got: $OUT"
COUNT=$(echo "$OUT" | grep -c "'click' → 'select'" || true)
[ "$COUNT" = "3" ] || fail "list should show 3 rows, got $COUNT"
pass "list showed all 3 rows"

# ─── Case 5: list --domain filter ─────────────────────────────────────
echo "▶ Step 5: list --domain filter"
OUT=$(cd "$TMPDIR" && python3 "$FB" list --domain business-proposal 2>&1)
echo "$OUT" | grep -q "no feedback rows" || fail "empty filter should report no rows, got: $OUT"
pass "domain filter correctly returned no rows"

# ─── Case 6: search finds matching term ───────────────────────────────
echo "▶ Step 6: search matches before OR after field"
OUT=$(cd "$TMPDIR" && python3 "$FB" search "select" 2>&1)
echo "$OUT" | grep -q "3 row(s) matching 'select'" || fail "search didn't find 3 rows, got: $OUT"
pass "search found 3 rows matching 'select'"

OUT=$(cd "$TMPDIR" && python3 "$FB" search "nonexistent-term-xyz" 2>&1)
echo "$OUT" | grep -q "no feedback rows" || fail "search should report empty, got: $OUT"
pass "search reports empty for unknown term"

# ─── Case 7: reflect.py picks up the string-swap proposal ─────────────
echo "▶ Step 7: reflect.py surfaces the string-swap proposal"
OUT=$(cd "$TMPDIR" && python3 "$REFLECT" --json --since all 2>&1)
echo "$OUT" | python3 -c "
import json, sys
data = json.loads(sys.stdin.read())
proposals = data.get('proposals', [])
swaps = [p for p in proposals if p.get('kind') == 'string-swap']
assert len(swaps) == 1, f'expected 1 string-swap proposal, got {len(swaps)}: {proposals}'
p = swaps[0]
assert p['before'] == 'click', p
assert p['after'] == 'select', p
assert p['count'] == 3, p
assert p['domain'] == 'tutorial', p
assert p['lang'] == 'en', p
" || fail "reflect.py did not surface the expected string-swap proposal"
pass "reflect.py surfaced string-swap: 'click' → 'select' (count=3)"

# ─── Case 8: different before/after does NOT trigger proposal (< 3) ───
echo "▶ Step 8: single correction does not trigger a proposal"
(cd "$TMPDIR" && python3 "$FB" add --before "user" --after "customer" \
   --domain tutorial --lang en >/dev/null 2>&1)
OUT=$(cd "$TMPDIR" && python3 "$REFLECT" --json --since all 2>&1)
SINGLE_COUNT=$(echo "$OUT" | python3 -c "
import json, sys
data = json.loads(sys.stdin.read())
swaps = [p for p in data.get('proposals', []) if p.get('kind') == 'string-swap']
single = [p for p in swaps if p['before'] == 'user']
print(len(single))
")
[ "$SINGLE_COUNT" = "0" ] || fail "one-off correction should not trigger proposal, got $SINGLE_COUNT"
pass "one-off correction correctly suppressed (threshold=3)"

echo ""
echo "✓ test-feedback passed (8 steps)"
