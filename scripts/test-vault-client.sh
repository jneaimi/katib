#!/usr/bin/env bash
# test-vault-client.sh — verify the v0.15.0 vault-API client + routing logic.
#
# Phase 2 of the vault-integration migration (ADR §20). The client must:
#   - POST manifest.md to Soul Hub when reachable (happy path)
#   - Fall back to FS with a `katib-fallback` tag when the API is unreachable
#   - Fail hard in strict mode on network failure
#   - Skip the API entirely in fs mode
#   - Route outputs via --project: katib → content/katib, other → projects/<slug>/outputs/
#   - Surface governance rejections with the server's error message
#
# Live API assertions only fire when Soul Hub is reachable at SOUL_HUB_URL
# (default http://localhost:2400). Offline paths are tested via an intentionally
# unreachable 127.0.0.1:1 URL and don't require Soul Hub.
#
# Exits 0 on success.

set -u

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1" >&2; echo "    detail: $2" >&2; }
step() { echo ""; echo "• $1"; }

# ---------- Soul Hub reachability probe ----------
SOUL_HUB_URL="${SOUL_HUB_URL:-http://localhost:2400}"
if curl -sS --max-time 3 -o /dev/null "$SOUL_HUB_URL/api/vault/notes" -X POST \
    -H "Content-Type: application/json" -d '{}' 2>/dev/null; then
    LIVE_API=1
    echo "[info] Soul Hub reachable at $SOUL_HUB_URL — live API tests will run"
else
    LIVE_API=0
    echo "[info] Soul Hub NOT reachable at $SOUL_HUB_URL — skipping live API tests"
fi

# ---------- Step 1: client module imports cleanly ----------
step "Step 1: vault_client module imports + exports"
if python3 -c "
import sys
sys.path.insert(0, '$SKILL_ROOT/scripts')
from vault_client import (
    create_note, derive_zone_and_filename,
    VaultError, VaultGovernanceError, VaultConflictError, VaultNetworkError,
    VaultWriteResult,
)
print('ok')
" 2>/dev/null | grep -q "^ok$"; then
    pass "module imports + public API present"
else
    fail "import failure" "check vault_client.py syntax"
fi

# ---------- Step 2: fallback mode writes FS with katib-fallback tag ----------
step "Step 2: KATIB_VAULT_MODE=api falls back to FS with marker tag"
export SOUL_HUB_URL="http://127.0.0.1:1"
export KATIB_VAULT_MODE="api"
export KATIB_VAULT_TIMEOUT="2"

FALLBACK_OUT=$(python3 "$SKILL_ROOT/scripts/vault_client.py" \
    --zone "test-fb" --filename "note.md" \
    --meta '{"type":"output","created":"2099-01-01","tags":["katib"]}' \
    --content "hello" \
    --vault-root "$TMPDIR" 2>&1)
FALLBACK_EXIT=$?

if [ $FALLBACK_EXIT -eq 0 ] && echo "$FALLBACK_OUT" | grep -q "^✓ fallback"; then
    pass "fallback path taken on unreachable API"
else
    fail "fallback not taken" "exit=$FALLBACK_EXIT output='$FALLBACK_OUT'"
fi

if [ -f "$TMPDIR/test-fb/note.md" ]; then
    if grep -q "katib-fallback" "$TMPDIR/test-fb/note.md"; then
        pass "katib-fallback tag injected into frontmatter"
    else
        fail "katib-fallback tag missing" "file contents:\n$(cat "$TMPDIR/test-fb/note.md")"
    fi
else
    fail "file not created at fallback path" "ls: $(ls -la "$TMPDIR/test-fb/" 2>&1)"
fi

# ---------- Step 3: strict mode fails hard on network error ----------
step "Step 3: KATIB_VAULT_MODE=strict surfaces VaultNetworkError"
KATIB_VAULT_MODE="strict" python3 "$SKILL_ROOT/scripts/vault_client.py" \
    --zone "test-strict" --filename "note.md" \
    --meta '{"type":"output","created":"2099-01-01","tags":["katib"]}' \
    --content "x" \
    --vault-root "$TMPDIR" >/tmp/katib-strict.out 2>&1
STRICT_EXIT=$?

if [ $STRICT_EXIT -eq 6 ] && grep -q "^✗ network:" /tmp/katib-strict.out; then
    pass "strict mode exits 6 with network error"
else
    fail "strict mode didn't fail as expected" "exit=$STRICT_EXIT out=$(cat /tmp/katib-strict.out)"
fi

if [ -f "$TMPDIR/test-strict/note.md" ]; then
    fail "strict mode wrote file despite error" "should have raised, not fallen back"
else
    pass "strict mode wrote nothing (no silent fallback)"
fi

# ---------- Step 4: fs mode skips API entirely (fast) ----------
step "Step 4: KATIB_VAULT_MODE=fs skips API even when reachable"
# Point URL at a reachable port — but mode=fs should not hit it
unset SOUL_HUB_URL
FS_START=$(date +%s)
KATIB_VAULT_MODE="fs" python3 "$SKILL_ROOT/scripts/vault_client.py" \
    --zone "test-fs" --filename "note.md" \
    --meta '{"type":"output","created":"2099-01-01","tags":["katib"]}' \
    --content "x" \
    --vault-root "$TMPDIR" >/dev/null 2>&1
FS_EXIT=$?
FS_ELAPSED=$(($(date +%s) - FS_START))

if [ $FS_EXIT -eq 0 ] && [ $FS_ELAPSED -le 2 ]; then
    pass "fs mode writes instantly (${FS_ELAPSED}s) without API call"
else
    fail "fs mode slow or failed" "exit=$FS_EXIT elapsed=${FS_ELAPSED}s"
fi

if [ -f "$TMPDIR/test-fs/note.md" ] && ! grep -q "katib-fallback" "$TMPDIR/test-fs/note.md"; then
    pass "fs mode writes clean frontmatter (no fallback tag)"
else
    fail "fs mode output unexpected" "content: $(cat "$TMPDIR/test-fs/note.md" 2>/dev/null)"
fi

# ---------- Step 5: derive_zone_and_filename happy path ----------
step "Step 5: derive_zone_and_filename splits correctly"
python3 -c "
import sys
sys.path.insert(0, '$SKILL_ROOT/scripts')
from pathlib import Path
from vault_client import derive_zone_and_filename

vault_root = Path('/tmp/fake-vault')
slug_dir = vault_root / 'content' / 'katib' / 'business-proposal' / '2026-04-22-foo'
zone, fn = derive_zone_and_filename(slug_dir, vault_root, 'manifest.md')
assert zone == 'content/katib/business-proposal/2026-04-22-foo', f'zone wrong: {zone}'
assert fn == 'manifest.md'
print('ok')
" 2>/dev/null | grep -q "^ok$" \
    && pass "zone/filename derived from slug_dir relative to vault_root" \
    || fail "derive_zone_and_filename broken" "see script output"

# ---------- Step 6: derive_zone_and_filename rejects out-of-vault path ----------
step "Step 6: derive_zone_and_filename raises on out-of-vault folder"
python3 -c "
import sys
sys.path.insert(0, '$SKILL_ROOT/scripts')
from pathlib import Path
from vault_client import derive_zone_and_filename, VaultError

try:
    derive_zone_and_filename(Path('/tmp/elsewhere'), Path('/tmp/fake-vault'), 'manifest.md')
    print('no-raise')
except VaultError:
    print('raised')
" 2>/dev/null | grep -q "^raised$" \
    && pass "out-of-vault path raises VaultError" \
    || fail "derive_zone_and_filename didn't reject" "should have raised"

# ---------- Step 7: --project routing goes to projects/<slug>/outputs/ ----------
step "Step 7: resolve_project_outputs_root routes by project slug"
python3 -c "
import sys
sys.path.insert(0, '$SKILL_ROOT/scripts')
from pathlib import Path
from config import resolve_project_outputs_root

cfg = {'output': {'destination': 'vault', 'vault_path': '/tmp/fakevault/content/katib'}}

# project=katib → legacy path
katib_path = resolve_project_outputs_root(cfg, 'katib')
assert str(katib_path) == '/tmp/fakevault/content/katib', f'katib wrong: {katib_path}'

# project=<other> → projects/<slug>/outputs/
other_path = resolve_project_outputs_root(cfg, 'ils-offers')
assert str(other_path) == '/tmp/fakevault/projects/ils-offers/outputs', f'other wrong: {other_path}'
print('ok')
" 2>/dev/null | grep -q "^ok$" \
    && pass "routing: project=katib → content/katib, project=<other> → projects/<slug>/outputs/" \
    || fail "routing helper broken" "see script output"

# ---------- Step 8: build.py end-to-end with --project katib (fs mode) ----------
step "Step 8: build.py fs-mode smoke — --project katib → content/katib path"
FS_VAULT=$(mktemp -d)
export KATIB_OUTPUT_ROOT="$FS_VAULT/content/katib"
export KATIB_VAULT_MODE="fs"
mkdir -p "$FS_VAULT/content/katib"

cd "$SKILL_ROOT"
BUILD_OUT=$(uv run scripts/build.py one-pager --lang en \
    --title "Phase 2 Test Build" --project katib 2>&1)
BUILD_EXIT=$?

if [ $BUILD_EXIT -eq 0 ] && echo "$BUILD_OUT" | grep -q "^✓"; then
    pass "render succeeded with fs mode"
else
    fail "render failed" "exit=$BUILD_EXIT\n$BUILD_OUT"
fi

MANIFEST=$(find "$FS_VAULT/content/katib/business-proposal" -name "manifest.md" | head -1)
if [ -n "$MANIFEST" ] && [ -f "$MANIFEST" ]; then
    pass "manifest.md exists in content/katib/business-proposal/..."
else
    fail "manifest not found" "ls: $(find "$FS_VAULT" 2>&1)"
fi

if [ -n "$MANIFEST" ] && ! grep -q "katib-fallback" "$MANIFEST"; then
    pass "fs-mode manifest has no katib-fallback tag (not a fallback)"
else
    fail "unexpected katib-fallback in fs-mode manifest" "content: $(cat "$MANIFEST" 2>/dev/null)"
fi

unset KATIB_OUTPUT_ROOT KATIB_VAULT_MODE SOUL_HUB_URL KATIB_VAULT_TIMEOUT
rm -rf "$FS_VAULT"

# ---------- Step 9: LIVE API — POST succeeds against reachable Soul Hub ----------
if [ $LIVE_API -eq 1 ]; then
    step "Step 9: LIVE — POST to Soul Hub /api/vault/notes succeeds"
    # Unique zone AND unique body — Soul Hub's similarity detector fires when
    # repeat runs write identical content, even to different paths. Appending
    # a UUID-like nonce to the body keeps each test run below the 90% similarity
    # threshold without forcing the caller to manually clean up old zones.
    NONCE=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
    LIVE_ZONE="projects/katib/outputs/_test-$NONCE"
    LIVE_OUT=$(python3 "$SKILL_ROOT/scripts/vault_client.py" \
        --zone "$LIVE_ZONE" --filename "manifest.md" \
        --meta "{\"type\":\"output\",\"created\":\"2099-12-31\",\"updated\":\"2099-12-31\",\"tags\":[\"katib\",\"phase2-test\",\"auto-generated\"],\"project\":\"katib\",\"domain\":\"business-proposal\",\"doc_type\":\"proposal\",\"languages\":[\"en\"],\"formats\":[\"pdf\"],\"cover_style\":\"minimalist-typographic\",\"layout\":\"classic\",\"katib_version\":\"0.15.0-test\",\"source_agent\":\"phase2-test\"}" \
        --content "# Phase 2 vault-client harness · nonce=$NONCE · this file is safe to delete" \
        --vault-root "$HOME/vault" 2>&1)
    LIVE_EXIT=$?

    if [ $LIVE_EXIT -eq 0 ] && echo "$LIVE_OUT" | grep -q "^✓ api:"; then
        pass "live API write returned via api backend"
    else
        fail "live API write failed" "exit=$LIVE_EXIT out=$LIVE_OUT"
    fi

    LIVE_FILE="$HOME/vault/$LIVE_ZONE/manifest.md"
    if [ -f "$LIVE_FILE" ]; then
        pass "manifest.md written to vault at expected path"
        rm -rf "$HOME/vault/$LIVE_ZONE"
    else
        fail "manifest not at expected vault path" "expected: $LIVE_FILE"
    fi

    # ---------- Step 10: LIVE — governance reject surfaces cleanly ----------
    step "Step 10: LIVE — invalid type → VaultGovernanceError (exit 4)"
    REJECT_OUT=$(python3 "$SKILL_ROOT/scripts/vault_client.py" \
        --zone "projects/katib/outputs/_test-reject" --filename "note.md" \
        --meta '{"type":"totally-bogus","created":"2099-01-01","tags":["katib"],"project":"katib"}' \
        --content "body" \
        --vault-root "$HOME/vault" 2>&1)
    REJECT_EXIT=$?

    if [ $REJECT_EXIT -eq 4 ] && echo "$REJECT_OUT" | grep -q "governance:"; then
        pass "governance reject exits 4 with readable error"
    else
        fail "governance reject behaved unexpectedly" "exit=$REJECT_EXIT out=$REJECT_OUT"
    fi
else
    echo ""
    echo "• Steps 9-10 skipped (Soul Hub not reachable at $SOUL_HUB_URL)"
fi

# ---------- Summary ----------
echo ""
echo "================================================================"
if [ $FAIL -eq 0 ]; then
    echo "✓ vault-client harness passed — $PASS assertions"
    exit 0
else
    echo "✗ vault-client harness failed — $PASS passed, $FAIL failed"
    exit 1
fi
