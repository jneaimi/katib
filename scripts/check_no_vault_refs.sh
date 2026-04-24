#!/usr/bin/env bash
# Exit criterion: the skill must be standalone — no references to
# vault/obsidian/soul-hub in shipping code or content.
#
# Excluded from the scan:
#   - v1-reference/           historical v1 code (read-only)
#   - recipes/_wip/           scratch/deferred recipes (excluded from
#                             capabilities generation; see recipes/_wip/README.md)
#   - CHANGELOG.md            historical record of the project's evolution
#   - README.md / SKILL.md    user-facing docs (scrubbed separately; legitimate
#                             English prose like "password vault" may appear)
#
# Usage:  bash scripts/check_no_vault_refs.sh

set -euo pipefail

cd "$(dirname "$0")/.."

# Match path-like / code-like references only. The bare English word
# "vault" is legitimate in prose (e.g., "knowledge vault"), so we match
# path prefixes / suffixes + the Obsidian config dir + Soul Hub identifiers.
PATTERN='vault/|/vault|~vault|\.obsidian|soul-hub|soul_hub|SoulHub'

matches="$(
    grep -rnE "${PATTERN}" \
        --include='*.py' --include='*.yaml' --include='*.yml' \
        --include='*.html' --include='*.css' --include='*.md' --include='*.json' \
        --exclude-dir=v1-reference \
        --exclude-dir=_wip \
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
