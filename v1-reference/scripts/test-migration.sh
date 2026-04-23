#!/usr/bin/env bash
# test-migration.sh — verify audit_vault.py, migrate_vault.py, and
# recover_vault.py on a scratch vault with seeded legacy manifests.
#
# Phase 4 of the vault-integration migration (ADR §20). The scripts mutate
# real files, so every assertion runs inside a mktemp dir; nothing leaks
# into the user's vault. The live Soul Hub is not required — migrations
# are FS-only after the v0.17.0 incident (see migrate_vault.execute_plan
# for the full story).
#
# Exits 0 on success.

set -u

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1" >&2; echo "    detail: $2" >&2; }
step() { echo ""; echo "• $1"; }

# ---------- Build scratch vault fixture ----------
TMP_VAULT=$(mktemp -d)
trap 'rm -rf "$TMP_VAULT"' EXIT

# Two legacy manifests that should be rewritten in place (project=katib),
# one that should relocate (project=ils-offers in content/katib → projects),
# one that's already clean (baseline).

mkdir -p "$TMP_VAULT/content/katib/tutorial/2026-04-22-stay-put"
mkdir -p "$TMP_VAULT/content/katib/tutorial/2026-04-22-stay-put/.katib"
mkdir -p "$TMP_VAULT/content/katib/tutorial/2026-04-22-stay-put/source"

cat > "$TMP_VAULT/content/katib/tutorial/2026-04-22-stay-put/manifest.md" <<'EOF'
---
type: output
created: 2026-04-21
updated: 2026-04-21
tags: [katib, tutorial, how-to, en, katib-stay]
project: katib
domain: tutorial
doc_type: how-to
languages: [en]
formats: [pdf]
cover_style: null
layout: classic
katib_version: 0.1.0
source_agent: claude-opus-4-7
---

# Stay Put
body content
EOF

mkdir -p "$TMP_VAULT/content/katib/business-proposal/2026-04-22-to-relocate"
mkdir -p "$TMP_VAULT/content/katib/business-proposal/2026-04-22-to-relocate/.katib"
mkdir -p "$TMP_VAULT/content/katib/business-proposal/2026-04-22-to-relocate/source"

cat > "$TMP_VAULT/content/katib/business-proposal/2026-04-22-to-relocate/manifest.md" <<'EOF'
---
type: output
created: 2026-04-21
updated: 2026-04-21
tags: [katib, business-proposal, proposal, en, ils-offers]
project: ils-offers
domain: business-proposal
doc_type: proposal
languages: [en]
formats: [pdf]
cover_style: neural-cartography
layout: classic
katib_version: 0.1.0
source_agent: claude-opus-4-7
---

# To Relocate
body content
EOF

# The relocate fixture also needs the projects/ scaffolding so the
# governance parent resolves (projects/CLAUDE.md). migrate_vault doesn't
# read it, but recover_vault does when rebuilding manifests.
mkdir -p "$TMP_VAULT/projects/ils-offers"
cat > "$TMP_VAULT/projects/CLAUDE.md" <<'EOF'
## Allowed Types
project, learning, decision, debugging, output, index
## Required Fields
type, created, tags, project
EOF

# ---------- Step 1: audit_vault flags the drift ----------
step "Step 1: audit_vault identifies drift"
AUDIT=$(python3 "$SKILL_ROOT/scripts/audit_vault.py" --vault-root "$TMP_VAULT" 2>&1)
if echo "$AUDIT" | grep -q "With error(s)" && \
   echo "$AUDIT" | grep -q "ils-offers"; then
    pass "audit reports errors and flags ils-offers relocation candidate"
else
    fail "audit didn't flag drift" "output:\n$AUDIT"
fi

# ---------- Step 2: migrate_vault --dry-run shows the plan ----------
step "Step 2: migrate_vault --dry-run shows relocations + rewrites"
PLAN=$(python3 "$SKILL_ROOT/scripts/migrate_vault.py" --vault-root "$TMP_VAULT" 2>&1)
RELOC=$(echo "$PLAN" | grep -oE "relocate \+ rewrite \(move\) : [0-9]+" | grep -oE "[0-9]+$")
REWRITE=$(echo "$PLAN" | grep -oE "rewrite only \(stay put\)   : [0-9]+" | grep -oE "[0-9]+$")

if [ "$RELOC" = "1" ] && [ "$REWRITE" = "1" ]; then
    pass "plan shows 1 relocate + 1 rewrite"
else
    fail "plan counts wrong" "reloc=$RELOC rewrite=$REWRITE\n$PLAN"
fi

# ---------- Step 3: dry-run didn't touch the files ----------
step "Step 3: dry-run leaves fixtures intact"
if [ -f "$TMP_VAULT/content/katib/tutorial/2026-04-22-stay-put/manifest.md" ] && \
   [ -f "$TMP_VAULT/content/katib/business-proposal/2026-04-22-to-relocate/manifest.md" ] && \
   [ ! -d "$TMP_VAULT/projects/ils-offers/outputs" ]; then
    pass "no files moved or rewritten by --dry-run"
else
    fail "dry-run had side effects" "something moved"
fi

# ---------- Step 4: --execute applies the plan (FS-only) ----------
step "Step 4: --execute rewrites in place + relocates"
EXEC_OUT=$(python3 "$SKILL_ROOT/scripts/migrate_vault.py" --vault-root "$TMP_VAULT" --execute --yes 2>&1)
APPLIED=$(echo "$EXEC_OUT" | grep -oE "applied=[0-9]+" | grep -oE "[0-9]+$")
FAILED=$(echo "$EXEC_OUT" | grep -oE "failed=[0-9]+" | grep -oE "[0-9]+$")

if [ "$APPLIED" = "2" ] && [ "$FAILED" = "0" ]; then
    pass "execute applied 2, failed 0"
else
    fail "execute numbers wrong" "applied=$APPLIED failed=$FAILED\n$EXEC_OUT"
fi

# Relocate: old path gone, new path has manifest
if [ ! -d "$TMP_VAULT/content/katib/business-proposal/2026-04-22-to-relocate" ] && \
   [ -f "$TMP_VAULT/projects/ils-offers/outputs/business-proposal/2026-04-22-to-relocate/manifest.md" ]; then
    pass "relocation executed — old gone, new exists"
else
    fail "relocation didn't move cleanly" "see $TMP_VAULT"
fi

# Stay-put: frontmatter has v0.17.0 markers
STAY="$TMP_VAULT/content/katib/tutorial/2026-04-22-stay-put/manifest.md"
if grep -q "katib_version: 0.17.0" "$STAY" && \
   grep -q "source_agent: katib-migration-v0.17.0" "$STAY" && \
   grep -q "source_agent_original: claude-opus-4-7" "$STAY" && \
   grep -q "migrated_at:" "$STAY"; then
    pass "stay-put manifest carries v0.17.0 audit fields"
else
    fail "stay-put manifest missing migration markers" "$(cat "$STAY")"
fi

# Tags are clean (no domain/doc_type/lang pollution)
if grep -q "tags: \[katib, auto-generated\]" "$STAY"; then
    pass "stay-put tags cleaned (project=katib case)"
else
    fail "stay-put tags not cleaned" "$(grep '^tags:' "$STAY")"
fi

# ---------- Step 5: post-migration audit is clean ----------
step "Step 5: post-execute audit shows zero errors"
POST_AUDIT=$(python3 "$SKILL_ROOT/scripts/audit_vault.py" --vault-root "$TMP_VAULT" 2>&1)
if echo "$POST_AUDIT" | grep -qE "With error\(s\)[^0-9]+0\b"; then
    pass "post-migration audit reports 0 errors"
else
    fail "post-migration audit still flags issues" "$POST_AUDIT"
fi

# ---------- Step 6: recover_vault idempotency (nothing orphaned) ----------
step "Step 6: recover_vault sees a healthy vault as noop"
RECOVER=$(python3 "$SKILL_ROOT/scripts/recover_vault.py" --vault-root "$TMP_VAULT" 2>&1)
if echo "$RECOVER" | grep -q "No orphaned manifests found"; then
    pass "recovery is idempotent on a healthy vault"
else
    fail "recovery found phantom orphans" "$RECOVER"
fi

# ---------- Step 7: simulate incident, then recover ----------
step "Step 7: delete a manifest → recover_vault rebuilds it"
cat > "$TMP_VAULT/projects/ils-offers/outputs/business-proposal/2026-04-22-to-relocate/.katib/run.json" <<'EOF'
{
  "katib_version": "0.17.0",
  "generated_at": "2026-04-22T10:00:00Z",
  "domain": "business-proposal",
  "doc_type": "proposal",
  "languages": ["en"],
  "formats": ["pdf"],
  "cover": {"style": "neural-cartography"},
  "layout": "classic",
  "source_agent": "katib-cli"
}
EOF
cat > "$TMP_VAULT/projects/ils-offers/outputs/business-proposal/2026-04-22-to-relocate/source/proposal.en.html" <<'EOF'
<!DOCTYPE html><html><head><title>Recovered Proposal</title></head>
<body><h1>Recovered Proposal</h1><p>body</p></body></html>
EOF

rm "$TMP_VAULT/projects/ils-offers/outputs/business-proposal/2026-04-22-to-relocate/manifest.md"

RECOVERED=$(python3 "$SKILL_ROOT/scripts/recover_vault.py" --vault-root "$TMP_VAULT" --execute --yes 2>&1)
if echo "$RECOVERED" | grep -q "applied=1"; then
    pass "recover_vault reconstructed the deleted manifest"
else
    fail "recovery didn't apply" "$RECOVERED"
fi

if [ -f "$TMP_VAULT/projects/ils-offers/outputs/business-proposal/2026-04-22-to-relocate/manifest.md" ] && \
   grep -q "title: Recovered Proposal" "$TMP_VAULT/projects/ils-offers/outputs/business-proposal/2026-04-22-to-relocate/manifest.md"; then
    pass "recovered manifest exists with title extracted from HTML"
else
    fail "recovery output incorrect" "$(cat "$TMP_VAULT/projects/ils-offers/outputs/business-proposal/2026-04-22-to-relocate/manifest.md" 2>/dev/null)"
fi

# ---------- Summary ----------
echo ""
echo "================================================================"
if [ $FAIL -eq 0 ]; then
    echo "✓ migration harness passed — $PASS assertions"
    exit 0
else
    echo "✗ migration harness failed — $PASS passed, $FAIL failed"
    exit 1
fi
