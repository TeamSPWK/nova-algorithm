---
name: llm-review
description: |
  Multi-LLM consultation wrapper for external AI reviews.
  Supports Gemini and GPT with hardcoded model names to prevent agent modifications.
user-invocable: true
---

# LLM Review - Multi-AI Consultation Skill

Provides a reliable interface for calling external LLMs (Gemini, GPT) with code-owned model configurations.

## Purpose

1. **Prevent model name changes** by agents (hardcoded in Python)
2. **Standardize API protocols** (different APIs handled internally)
3. **Provide consistent JSON output** for easy parsing

---

## Usage

```bash
LLM_CLIENT=
for candidate in \
  "$HOME/.claude/skills/llm-review/llm_client.py" \
  "$HOME/.agents/skills/llm-review/llm_client.py" \
  "$PWD/skills/llm-review/llm_client.py"; do
  [ -f "$candidate" ] && { LLM_CLIENT="$candidate"; break; }
done
[ -n "$LLM_CLIENT" ] || { echo "llm-review is not installed and this is not its source checkout" >&2; exit 1; }

python3 "$LLM_CLIENT" \
  --provider gemini \
  --phase consultation \
  --prompt "Your prompt" \
  --output /tmp/result.json
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--provider` | Yes | `gemini` or `openai` |
| `--phase` | Yes | `consultation` (fast), `review` (thorough), `regulation` (thinking + web search) |
| `--prompt` | Yes* | Prompt text |
| `--prompt-file` | Yes* | Read prompt from file |
| `--include-files` | No | Append source files to prompt (space-separated, supports `file:start-end`) |
| `--max-file-lines` | No | Max lines per included file (0 = unlimited, default: 0) |
| `--output` | No | Output file (default: stdout) |

### --include-files Examples

```bash
# Attach full files
--include-files output.py utils.py complex.py

# Attach specific line ranges
--include-files "complex.py:100-300" "utils.py:1-200"

# Mix full files and ranges
--include-files engine.py "complex.py:100-500" utils.py
```

> **IMPORTANT**: When consulting about code, ALWAYS use `--include-files` to attach
> the relevant source files. Without it, the external LLM only sees file names,
> not the actual code, and can only give generic advice.

---

## Models

`llm_client.py` is the only source of truth for model IDs and reasoning settings. Inspect the live configuration with
`python3 "$LLM_CLIENT" --list-models`; do not copy that output back into this document.

---

## Output Format

```json
{
  "success": true,
  "provider": "gemini",
  "model": "<configured model>",
  "response": "LLM response text...",
  "tokens": {"prompt": 1234, "completion": 567, "total": 1801},
  "elapsed_seconds": 3.2
}
```

Error: `"success": false, "error": "...", "error_type": "..."`

---

## Environment

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google AI Studio API key |
| `OPENAI_API_KEY` | OpenAI API key |

Auto-loads from `.env` in current working directory, then walks up to workspace root.

**Check keys:** `python3 "$LLM_CLIENT" --check-keys`

---

## Error Handling

| Error | Behavior |
|-------|----------|
| API key missing | Returns error JSON |
| Timeout / 429 / 502 / 503 | Retries 3x with backoff (2s, 5s, 10s) |
| 400 / 401 / 404 | Immediate failure, no retry |
| review/regulation without `--include-files` | Prints `[WARN]` to stderr |
