#!/bin/bash
# Nova Algorithm - Claude Code Skills Installer
# Usage: git clone https://github.com/ChoSungHyeon/nova-algorithm.git && cd nova-algorithm && bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Installing Nova Algorithm skills..."

# Create directories
mkdir -p "$CLAUDE_DIR/commands"
mkdir -p "$CLAUDE_DIR/skills"

# Symlink commands
for f in "$SCRIPT_DIR/commands/"*.md; do
  [ -f "$f" ] || continue
  name="$(basename "$f")"
  ln -sf "$f" "$CLAUDE_DIR/commands/$name"
  echo "  + command: /$name"
done

# Symlink skill directories
for d in "$SCRIPT_DIR/skills/"*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  ln -sf "$d" "$CLAUDE_DIR/skills/$name"
  echo "  + skill: $name"
done

echo ""
echo "Done! Restart Claude Code to activate."
echo ""
echo "Required for /llm-review and /deep-dive-task:"
echo "  export GEMINI_API_KEY=\"your-key\""
echo "  export OPENAI_API_KEY=\"your-key\""
