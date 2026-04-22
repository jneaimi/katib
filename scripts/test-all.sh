#!/usr/bin/env bash
# Katib — render all business-proposal doc types × languages.
# Exit 1 if any render fails or --verify flags issues.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SKILL_DIR"

# Render harnesses default to fs mode so they stay offline-friendly and don't
# depend on a running Soul Hub. The API write path has its own end-to-end
# harness (test-vault-client.sh). Override by setting KATIB_VAULT_MODE=api
# in CI if you want to exercise the full vault integration.
export KATIB_VAULT_MODE="${KATIB_VAULT_MODE:-fs}"

REF="TITS-TP-2026-001"
PROJECT="ils-offers"
TITLE_EN="UAEN Full-Stack AI Training Program"
TITLE_AR="برنامج تدريب الذكاء الاصطناعي الشامل لجامعة الإمارات"
PURPOSE_EN="Hybrid Split delivery — 2 groups of 9, 6 weeks, AED 615K"
PURPOSE_AR="تسليم هجين — مجموعتان من ٩، ستة أسابيع، ٦١٥ ألف درهم"

render() {
  local doc="$1" lang="$2"
  local title="$TITLE_EN" purpose="$PURPOSE_EN"
  if [[ "$lang" == "ar" ]]; then
    title="$TITLE_AR"
    purpose="$PURPOSE_AR"
  fi

  # Shared slug per doc type — EN + AR co-locate in one folder
  local slug="uaen-training-$doc"

  echo ""
  echo "=============================================="
  echo "Rendering: $doc.$lang (slug: $slug)"
  echo "=============================================="

  uv run scripts/build.py "$doc" \
    --domain business-proposal \
    --lang "$lang" \
    --title "$title" \
    --project "$PROJECT" \
    --ref "$REF" \
    --purpose "$purpose" \
    --slug "$slug"
}

echo "▶ Katib test matrix — 3 doc types × 2 languages"
echo ""
echo "▶ Step 1: CSS lint"
uv run scripts/build.py --check

echo ""
echo "▶ Step 2: Render matrix"
render one-pager en
render one-pager ar
render letter en
render letter ar
render proposal en
render proposal ar

echo ""
echo "=============================================="
echo "✓ ALL 6 RENDERS COMPLETE"
echo "=============================================="
echo ""
echo "Output folders:"
# Phase 2 routing sends --project ils-offers to projects/ils-offers/outputs/ —
# which is where this test's renders land. Verify folders in that tree.
TODAY=$(date -u +%Y-%m-%d)
OUTPUT_GLOB="$HOME/vault/projects/$PROJECT/outputs/business-proposal/$TODAY-*/"
ls -1d $OUTPUT_GLOB 2>/dev/null | tail -10

echo ""
echo "▶ Step 3: Verify each generation folder"
shopt -s nullglob
FOLDERS=($OUTPUT_GLOB)
shopt -u nullglob
if [ ${#FOLDERS[@]} -eq 0 ]; then
  echo "✗ no output folders matched $OUTPUT_GLOB"
  exit 1
fi
for folder in "${FOLDERS[@]}"; do
  uv run scripts/build.py --verify "$folder" || exit 1
done

echo ""
echo "✓ Test matrix passed"
