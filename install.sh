#!/bin/bash
# Nova Algorithm - Claude Code Skills Installer
# Usage: git clone https://github.com/TeamSPWK/nova-algorithm.git && cd nova-algorithm && bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${NOVA_CLAUDE_DIR:-$HOME/.claude}"

echo "Installing Nova Algorithm skills..."

# Create directories
mkdir -p "$CLAUDE_DIR/commands"
mkdir -p "$CLAUDE_DIR/skills"

check_destination() {
  local source_path="$1"
  local destination="$2"

  if [ ! -e "$destination" ] && [ ! -L "$destination" ]; then
    return 0
  fi
  if [ -L "$destination" ] && [ "$(readlink -f "$destination")" = "$(readlink -f "$source_path")" ]; then
    return 0
  fi
  echo "ERROR: refusing to replace user-owned path: $destination" >&2
  return 1
}

# Fail before changing anything if any destination belongs to somebody else.
for f in "$SCRIPT_DIR/commands/"*.md; do
  [ -f "$f" ] || continue
  check_destination "$f" "$CLAUDE_DIR/commands/$(basename "$f")"
done
for d in "$SCRIPT_DIR/skills/"*/; do
  [ -f "$d/SKILL.md" ] || continue
  source_path="${d%/}"
  check_destination "$source_path" "$CLAUDE_DIR/skills/$(basename "$source_path")"
done

# Symlink commands
for f in "$SCRIPT_DIR/commands/"*.md; do
  [ -f "$f" ] || continue
  name="$(basename "$f")"
  [ -L "$CLAUDE_DIR/commands/$name" ] || ln -s "$f" "$CLAUDE_DIR/commands/$name"
  echo "  + command: /$name"
done

# Symlink skill directories
for d in "$SCRIPT_DIR/skills/"*/; do
  [ -f "$d/SKILL.md" ] || continue
  source_path="${d%/}"
  name="$(basename "$source_path")"
  [ -L "$CLAUDE_DIR/skills/$name" ] || ln -s "$source_path" "$CLAUDE_DIR/skills/$name"
  echo "  + skill: $name"
done

echo ""
echo "Done! Restart Claude Code to activate."
echo ""
echo "Required for /llm-review and /deep-dive-task:"
echo "  export GEMINI_API_KEY=\"your-key\""
echo "  export OPENAI_API_KEY=\"your-key\""
