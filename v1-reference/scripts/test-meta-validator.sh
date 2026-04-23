#!/usr/bin/env bash
# test-meta-validator.sh — verify the v0.14.0 metadata contract + vault-schema gate.
#
# Phase 1 of the vault-integration migration (ADR §20). The validator must
# catch every governance breach the vault engine would catch — drift here
# becomes "write succeeds locally, fails when Phase 2 flips on the API path."
#
# Asserts:
#   1. --describe-schema prints GLOBAL_REQUIRED + zone table
#   2. A clean manifest for content/katib/tutorial passes
#   3. Missing required field → error with correct field name
#   4. Tags as scalar (not list) → shape error
#   5. Missing 'auto-generated' tag → error
#   6. Missing 'katib' tag → error
#   7. Domain polluting tags → warning
#   8. Disallowed type (draft in content/katib) → error
#   9. Projects-zone manifest missing 'project' field → error
#   10. Project field mismatched to path → error
#   11. Live skill manifest.py output validates clean for both content/katib
#       and projects/<slug>/outputs zones (integration check)
#
# Exits 0 on success.

set -u

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; exit 1; }

V="$SKILL_ROOT/scripts/meta_validator.py"

echo "▶ test-meta-validator: schema gate (Phase 1 of vault integration)"

# ─── Case 1: --describe-schema output ─────────────────────────────────
echo "▶ Step 1: --describe-schema works offline"
OUT=$(python3 "$V" --describe-schema 2>&1)
echo "$OUT" | grep -q '"global_required"'          || fail "missing global_required"
echo "$OUT" | grep -q '"zones"'                     || fail "missing zones block"
echo "$OUT" | grep -q '"content/katib"'             || fail "missing content/katib zone"
echo "$OUT" | grep -q '"projects"'                  || fail "missing projects zone"
pass "schema dump includes all expected sections"

# Helper: build a manifest and run validator in pure-Python mode
run_validate() {
    local zone="$1" meta_file="$2"
    python3 -c "
import sys, json
sys.path.insert(0, '$SKILL_ROOT/scripts')
from meta_validator import validate
import yaml
meta = yaml.safe_load(open('$meta_file'))
violations = validate(meta, zone='$zone')
errors = [v for v in violations if v.severity == 'error']
warns = [v for v in violations if v.severity == 'warn']
print(json.dumps({
    'errors': [{'rule': v.rule, 'field': v.field, 'message': v.message} for v in errors],
    'warns':  [{'rule': v.rule, 'field': v.field, 'message': v.message} for v in warns],
}, indent=2))
"
}

# ─── Case 2: clean manifest passes ────────────────────────────────────
echo "▶ Step 2: clean manifest passes for content/katib/tutorial"
cat > "$TMPDIR/clean.yml" <<EOF
title: Clean Test Manifest
type: output
created: 2026-04-22
updated: 2026-04-22
tags: [katib, katib, auto-generated]
project: katib
domain: tutorial
doc_type: how-to
languages: [en, ar]
formats: [pdf]
cover_style: minimalist-typographic
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "content/katib/tutorial" "$TMPDIR/clean.yml")
ERR_COUNT=$(echo "$OUT" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['errors']))")
[ "$ERR_COUNT" = "0" ] || fail "clean manifest got $ERR_COUNT errors: $OUT"
pass "clean manifest passes (0 errors)"

# ─── Case 3: missing required field ───────────────────────────────────
echo "▶ Step 3: missing 'type' field is caught"
cat > "$TMPDIR/no-type.yml" <<EOF
created: 2026-04-22
tags: [katib, katib, auto-generated]
project: katib
domain: tutorial
doc_type: how-to
languages: [en]
formats: [pdf]
cover_style: null
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "content/katib/tutorial" "$TMPDIR/no-type.yml")
echo "$OUT" | grep -q "global.required.missing" || fail "expected global.required.missing, got: $OUT"
echo "$OUT" | grep -q '"field": "type"'         || fail "expected field=type, got: $OUT"
pass "missing type → global.required.missing[type]"

# ─── Case 4: tags as scalar ───────────────────────────────────────────
echo "▶ Step 4: tags as scalar string → shape error"
cat > "$TMPDIR/scalar-tags.yml" <<EOF
title: Test Manifest
type: output
created: 2026-04-22
tags: "not-a-list"
project: katib
domain: tutorial
doc_type: how-to
languages: [en]
formats: [pdf]
cover_style: null
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "content/katib/tutorial" "$TMPDIR/scalar-tags.yml")
echo "$OUT" | grep -q "tags.shape" || fail "expected tags.shape error, got: $OUT"
pass "scalar tags → tags.shape error"

# ─── Case 5: missing 'auto-generated' tag ─────────────────────────────
echo "▶ Step 5: source_agent set but no 'auto-generated' tag → error"
cat > "$TMPDIR/no-auto.yml" <<EOF
title: Test Manifest
type: output
created: 2026-04-22
tags: [katib]
project: katib
domain: tutorial
doc_type: how-to
languages: [en]
formats: [pdf]
cover_style: null
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "content/katib/tutorial" "$TMPDIR/no-auto.yml")
echo "$OUT" | grep -q "tags.auto_generated.missing" || fail "expected tags.auto_generated.missing, got: $OUT"
pass "missing auto-generated tag caught"

# ─── Case 6: missing 'katib' tag ──────────────────────────────────────
echo "▶ Step 6: missing 'katib' tag → error"
cat > "$TMPDIR/no-katib.yml" <<EOF
title: Test Manifest
type: output
created: 2026-04-22
tags: [auto-generated]
project: katib
domain: tutorial
doc_type: how-to
languages: [en]
formats: [pdf]
cover_style: null
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "content/katib/tutorial" "$TMPDIR/no-katib.yml")
echo "$OUT" | grep -q "tags.katib.missing" || fail "expected tags.katib.missing, got: $OUT"
pass "missing katib tag caught"

# ─── Case 7: tag pollution → warning ──────────────────────────────────
echo "▶ Step 7: domain/doc_type/lang in tags → warnings"
cat > "$TMPDIR/polluted.yml" <<EOF
title: Test Manifest
type: output
created: 2026-04-22
tags: [katib, tutorial, how-to, en, auto-generated]
project: katib
domain: tutorial
doc_type: how-to
languages: [en]
formats: [pdf]
cover_style: null
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "content/katib/tutorial" "$TMPDIR/polluted.yml")
WARN_COUNT=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for w in d['warns'] if w['rule']=='tags.pollution'))")
[ "$WARN_COUNT" = "3" ] || fail "expected 3 pollution warnings, got $WARN_COUNT: $OUT"
ERR_COUNT=$(echo "$OUT" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['errors']))")
[ "$ERR_COUNT" = "0" ] || fail "pollution should be warning-level only, got $ERR_COUNT errors"
pass "3 pollution warnings for domain/doc_type/lang; no errors"

# ─── Case 8: disallowed type in content/katib ─────────────────────────
echo "▶ Step 8: 'draft' type rejected in content/katib"
cat > "$TMPDIR/wrong-type.yml" <<EOF
title: Test Manifest
type: draft
created: 2026-04-22
tags: [katib, auto-generated]
project: katib
domain: tutorial
doc_type: how-to
languages: [en]
formats: [pdf]
cover_style: null
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "content/katib/tutorial" "$TMPDIR/wrong-type.yml")
echo "$OUT" | grep -q "zone.type.disallowed" || fail "expected zone.type.disallowed for 'draft' in katib zone, got: $OUT"
pass "draft type rejected in content/katib"

# ─── Case 9: projects zone requires 'project' field ───────────────────
echo "▶ Step 9: projects zone without 'project' field → error"
cat > "$TMPDIR/proj-no-project.yml" <<EOF
title: Test Manifest
type: output
created: 2026-04-22
tags: [katib, ils-offers, auto-generated]
domain: business-proposal
doc_type: proposal
languages: [en, ar]
formats: [pdf]
cover_style: neural-cartography
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "projects/ils-offers/outputs" "$TMPDIR/proj-no-project.yml")
echo "$OUT" | grep -q '"field": "project"' || fail "expected field=project missing error, got: $OUT"
pass "projects zone enforces project field"

# ─── Case 10: project-path mismatch ───────────────────────────────────
echo "▶ Step 10: project field != path slug → error"
cat > "$TMPDIR/path-mismatch.yml" <<EOF
title: Test Manifest
type: output
created: 2026-04-22
tags: [katib, something-else, auto-generated]
project: something-else
domain: business-proposal
doc_type: proposal
languages: [en]
formats: [pdf]
cover_style: neural-cartography
layout: classic
katib_version: 0.14.0
source_agent: katib-cli
EOF
OUT=$(run_validate "projects/ils-offers/outputs" "$TMPDIR/path-mismatch.yml")
echo "$OUT" | grep -q "project.path_mismatch" || fail "expected project.path_mismatch, got: $OUT"
pass "project field / path slug mismatch caught"

# ─── Case 11: integration — live manifest.py output validates clean ───
echo "▶ Step 11: live skill manifest.py output validates cleanly"
TMPDIR_MANIFEST=$(mktemp -d)
python3 -c "
import sys
sys.path.insert(0, '$SKILL_ROOT/scripts')
from pathlib import Path
from manifest import write_manifest, folder_name, _today_iso
meta = {
    'title': 'Q2 Memo',
    'domain': 'tutorial',
    'doc_type': 'how-to',
    'languages': ['en'],
    'formats': ['pdf'],
    'cover_style': 'minimalist-typographic',
    'layout': 'classic',
    'project': 'katib',
    'source_context': 'abc12345',
}
folder = Path('$TMPDIR_MANIFEST') / folder_name(_today_iso(), meta['title'])
folder.mkdir(parents=True)
write_manifest(folder, meta)
print(folder)
" > "$TMPDIR/folder.txt"
FOLDER=$(cat "$TMPDIR/folder.txt")
[ -s "$FOLDER/manifest.md" ] || fail "manifest.md was not written"

# Now validate the live manifest
OUT=$(python3 "$V" --manifest "$FOLDER/manifest.md" --zone "content/katib/tutorial" 2>&1)
echo "$OUT" | grep -q "✓ clean" || fail "live manifest did not validate clean: $OUT"
pass "live manifest.py output passes schema (content/katib/tutorial)"

# And validate for a projects/ zone (passing project=ils-offers to match path)
python3 -c "
import sys
sys.path.insert(0, '$SKILL_ROOT/scripts')
from pathlib import Path
from manifest import write_manifest, folder_name, _today_iso
meta = {
    'title': 'UAEN Training Program',
    'domain': 'business-proposal',
    'doc_type': 'proposal',
    'languages': ['en'],
    'formats': ['pdf'],
    'cover_style': 'neural-cartography',
    'layout': 'classic',
    'project': 'ils-offers',
    'source_context': 'def45678',
}
folder = Path('$TMPDIR_MANIFEST') / 'proj-render'
folder.mkdir()
write_manifest(folder, meta)
print(folder)
" > "$TMPDIR/folder2.txt"
FOLDER2=$(cat "$TMPDIR/folder2.txt")
OUT=$(python3 "$V" --manifest "$FOLDER2/manifest.md" --zone "projects/ils-offers/outputs" 2>&1)
echo "$OUT" | grep -q "✓ clean" || fail "live manifest failed projects/ validation: $OUT"
pass "live manifest.py output passes schema (projects/ils-offers/outputs)"

rm -rf "$TMPDIR_MANIFEST"

echo ""
echo "✓ test-meta-validator passed (11 steps)"
