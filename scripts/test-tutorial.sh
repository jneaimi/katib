#!/usr/bin/env bash
# Katib — render all tutorial-domain doc types × languages.
# Exit 1 if any render fails or --verify flags issues.
#
# Matrix: 5 doc_types (how-to, cheatsheet, tutorial, onboarding, handoff)
#       × 2 languages (en, ar)
#       = 10 renders into shared slugs so EN+AR co-locate.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SKILL_DIR"

TITLE_HOWTO_EN="How to preview a PDF in Soul Hub"
TITLE_HOWTO_AR="كيف تعاين ملف PDF في Soul Hub"
TITLE_CHEAT_EN="Soul Hub keyboard shortcuts"
TITLE_CHEAT_AR="اختصارات لوحة المفاتيح في Soul Hub"
TITLE_TUT_EN="Getting started with Soul Hub"
TITLE_TUT_AR="بداية العمل مع Soul Hub"
TITLE_ONB_EN="Welcome to the team"
TITLE_ONB_AR="أهلاً بك في الفريق"
TITLE_HAND_EN="Vault viewer handoff"
TITLE_HAND_AR="تسليم عارض Vault"

render() {
  local doc="$1" lang="$2" title="$3" slug="$4" ref="$5"

  echo ""
  echo "=============================================="
  echo "Rendering: $doc.$lang  (slug: $slug)"
  echo "=============================================="

  uv run scripts/build.py "$doc" \
    --domain tutorial \
    --lang "$lang" \
    --title "$title" \
    --project "katib-tutorial-tests" \
    --ref "$ref" \
    --slug "$slug"
}

echo "▶ Katib tutorial test matrix — 5 doc types × 2 languages"
echo ""
echo "▶ Step 1: CSS lint"
uv run scripts/build.py --check

echo ""
echo "▶ Step 2: Render matrix"

# how-to
render how-to     en "$TITLE_HOWTO_EN" tut-test-how-to     "HT-0001"
render how-to     ar "$TITLE_HOWTO_AR" tut-test-how-to     "HT-0001"

# cheatsheet
render cheatsheet en "$TITLE_CHEAT_EN" tut-test-cheatsheet "CS-0001"
render cheatsheet ar "$TITLE_CHEAT_AR" tut-test-cheatsheet "CS-0001"

# tutorial
render tutorial   en "$TITLE_TUT_EN"   tut-test-tutorial   "TUT-0001"
render tutorial   ar "$TITLE_TUT_AR"   tut-test-tutorial   "TUT-0001"

# onboarding
render onboarding en "$TITLE_ONB_EN"   tut-test-onboarding "ON-0001"
render onboarding ar "$TITLE_ONB_AR"   tut-test-onboarding "ON-0001"

# handoff
render handoff    en "$TITLE_HAND_EN"  tut-test-handoff    "HT-TRD-001"
render handoff    ar "$TITLE_HAND_AR"  tut-test-handoff    "HT-TRD-001"

echo ""
echo "=============================================="
echo "✓ ALL 10 RENDERS COMPLETE"
echo "=============================================="
echo ""
echo "Output folders:"
ls -1d ~/vault/content/katib/tutorial/*tut-test-*/ 2>/dev/null

echo ""
echo "▶ Step 3: Verify each generation folder"
for folder in ~/vault/content/katib/tutorial/*tut-test-*/; do
  uv run scripts/build.py --verify "$folder" || exit 1
done

echo ""
echo "▶ Step 4: Verify EN+AR manifest merge"
for folder in ~/vault/content/katib/tutorial/*tut-test-*/; do
  manifest="$folder/manifest.md"
  if ! grep -q "languages: \[en, ar\]" "$manifest"; then
    echo "✗ merge failed in $manifest"
    grep "^languages:" "$manifest" || true
    exit 1
  fi
done
echo "  ✓ all manifests list both en and ar"

echo ""
echo "✓ Tutorial test matrix passed"
