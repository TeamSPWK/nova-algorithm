#!/bin/bash
# Nova Algorithm - Uninstaller

set -e

CLAUDE_DIR="$HOME/.claude"

echo "Uninstalling Nova Algorithm skills..."

# Remove command symlinks
for name in team-play.md; do
  rm -f "$CLAUDE_DIR/commands/$name" && echo "  - command: $name"
done

# Remove skill symlinks
for name in deep-dive-task llm-review; do
  rm -f "$CLAUDE_DIR/skills/$name" && echo "  - skill: $name"
done

echo "Done!"
