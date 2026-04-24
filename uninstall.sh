#!/usr/bin/env bash
# Katib uninstaller — removes the skill from ~/.claude/skills/katib/.
#
# By default, preserves user data:
#   ~/.katib/brands/              — your brand profiles + cover-preset assets
#   ~/.katib/recipes/             — recipes you authored
#   ~/.katib/components/          — components you authored (primitives, sections, covers)
#   ~/.katib/memory/              — audit + graduation-gate logs for your content
#   ~/.config/katib/              — your user config
#
# Pass --purge to wipe those too.

set -euo pipefail

PURGE=0
if [ "${1:-}" = "--purge" ]; then
  PURGE=1
fi

SKILL_DIR="$HOME/.claude/skills/katib"

if [ ! -d "$SKILL_DIR" ]; then
  echo "Nothing to remove — $SKILL_DIR doesn't exist."
  exit 0
fi

echo "▶ Removing $SKILL_DIR"
rm -rf "$SKILL_DIR"
echo "✓ skill removed"

if [ "$PURGE" -eq 1 ]; then
  for dir in "$HOME/.katib" "$HOME/.config/katib" "$HOME/.local/share/katib"; do
    if [ -d "$dir" ]; then
      echo "▶ Purging $dir"
      rm -rf "$dir"
    fi
  done
  echo "✓ user data purged"
else
  echo ""
  echo "User data preserved:"
  echo "  ~/.katib/brands/              (brand profiles + cover presets)"
  echo "  ~/.katib/recipes/             (your recipes)"
  echo "  ~/.katib/components/          (your components)"
  echo "  ~/.katib/memory/              (user-tier audit logs)"
  echo "  ~/.config/katib/              (config.yaml)"
  echo ""
  echo "Re-run with --purge to wipe these too."
fi
