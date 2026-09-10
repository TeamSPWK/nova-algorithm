#!/bin/bash
# Nova Algorithm - Uninstaller

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${NOVA_CLAUDE_DIR:-$HOME/.claude}"

echo "Uninstalling Nova Algorithm skills..."

remove_owned_link() {
  local source_path="$1"
  local destination="$2"
  local label="$3"

  [ -L "$destination" ] || return 0
  [ "$(readlink -f "$destination")" = "$(readlink -f "$source_path")" ] || return 0
  rm -f -- "$destination"
  echo "  - $label"
}

# Remove the same commands install.sh discovers, without touching replacements.
for f in "$SCRIPT_DIR/commands/"*.md; do
  [ -f "$f" ] || continue
  name="$(basename "$f")"
  remove_owned_link "$f" "$CLAUDE_DIR/commands/$name" "command: $name"
done

# Remove the same skills install.sh discovers, without touching replacements.
for d in "$SCRIPT_DIR/skills/"*/; do
  [ -f "$d/SKILL.md" ] || continue
  source_path="${d%/}"
  name="$(basename "$source_path")"
  remove_owned_link "$source_path" "$CLAUDE_DIR/skills/$name" "skill: $name"
done

# Compatibility cleanup for links created before doc-publish was retired.
remove_owned_link "$SCRIPT_DIR/skills/doc-publish" "$CLAUDE_DIR/skills/doc-publish" "skill: doc-publish (retired)"

echo "Done!"
