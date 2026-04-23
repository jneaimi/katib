#!/usr/bin/env bash
# Exit criterion for Phase 1: no references to vault/obsidian/soul-hub
# outside v1-reference/ and the CHANGELOG.
#
# Usage:  bash scripts/check_no_vault_refs.sh

set -euo pipefail

cd "$(dirname "$0")/.."

PATTERN='vault|obsidian|soul-hub|soul_hub|SoulHub'

matches="$(
    grep -rnE "${PATTERN}" \
        --include='*.py' --include='*.yaml' --include='*.yml' \
        --include='*.html' --include='*.css' --include='*.md' --include='*.json' \
        --exclude-dir=v1-reference \
        --exclude-dir=.venv \
        --exclude-dir=__pycache__ \
        --exclude-dir=.git \
        --exclude-dir=node_modules \
        --exclude=CHANGELOG.md \
        --exclude=README.md \
        --exclude=SKILL.md \
        . || true
)"

if [ -n "$matches" ]; then
    printf '✗ Found vault/obsidian/soul-hub references outside v1-reference/:\n'
    printf '%s\n' "$matches"
    exit 1
fi

printf '✓ clean — no vault/obsidian/soul-hub refs outside v1-reference/\n'
