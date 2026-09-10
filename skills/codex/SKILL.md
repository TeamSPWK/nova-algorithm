---
name: codex
description: >-
  Delegate implementation, review, or technical investigation to the Codex CLI and recover its result reliably.
  Use when the user explicitly asks for Codex or when a long-running coding task is intentionally handed off.
---

# Codex delegation

This skill owns the mechanics of starting, observing, and recovering a Codex CLI run. The caller owns task scope,
model choice, and final verification. Do not copy machine-specific paths, model IDs, or project rules into this file.

## Prepare

Write one bounded prompt containing:

- goal and target paths;
- constraints and files that must not change;
- measurable completion checks;
- an explicit ban on commit, push, and PR work unless the user authorized it.

Use the target repository's own `AGENTS.md`. `AGENTS.template.md` beside this file is an optional starter asset for
a repository that has no guidance; it is not an instruction file for this repository and must not be installed into
a target automatically.

## Run

Use the CLI's configured default model unless the caller explicitly selected one. Keep the model optional so this
skill does not become a stale model registry.

```bash
TAG=unique-task-slug
PROMPT=/tmp/codex-prompt-$TAG.md
LOG_DIR=/tmp/codex-logs
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR/$TAG.last.md" "$LOG_DIR/$TAG.jsonl" "$LOG_DIR/$TAG.thread" "$LOG_DIR/$TAG.pid"

model_args=()
[ -z "${CODEX_MODEL:-}" ] || model_args=(-m "$CODEX_MODEL")

nohup env -u OPENAI_API_KEY codex exec --json "${model_args[@]}" \
  -c sandbox_mode="workspace-write" \
  --skip-git-repo-check \
  -o "$LOG_DIR/$TAG.last.md" \
  - < "$PROMPT" > "$LOG_DIR/$TAG.jsonl" 2>&1 &
pid=$!
printf '%s' "$pid" > "$LOG_DIR/$TAG.pid"

for _ in $(seq 60); do
  thread_id=$(grep -m1 '"thread.started"' "$LOG_DIR/$TAG.jsonl" 2>/dev/null \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["thread_id"])' 2>/dev/null)
  [ -z "$thread_id" ] || { printf '%s' "$thread_id" > "$LOG_DIR/$TAG.thread"; break; }
  kill -0 "$pid" 2>/dev/null || break
  sleep 1
done

wait "$pid"
```

Use `sandbox_mode="read-only"` for review or consultation. Add network or filesystem access only when the task
requires it and the caller is authorized to grant it. `env -u OPENAI_API_KEY` keeps an authenticated CLI session
from silently switching to an ambient metered API key.

The input redirect is mandatory. It prevents background runs from waiting forever for inherited stdin. `nohup`, the
recorded PID, and `wait "$pid"` keep lifecycle and completion attached to one run.

## Observe and recover

Inspect structured events rather than treating a live process or a growing log as success:

```bash
python3 -c 'import json,sys
for line in open(sys.argv[1]):
    event=json.loads(line) if line.startswith("{") else {}
    if event.get("type") == "item.completed":
        item=event.get("item", {})
        print(item.get("type"), str(item.get("text") or item.get("command") or "")[:120])
    elif event.get("type") == "turn.completed":
        print("DONE", event.get("usage"))' "/tmp/codex-logs/$TAG.jsonl" | tail -3

grep -c '"turn.completed"' "/tmp/codex-logs/$TAG.jsonl"
grep -m2 '"invalid_request_error"\|^ERROR:' "/tmp/codex-logs/$TAG.jsonl"
```

No `turn.completed` event means the run did not complete. On a stuck or misdirected run, stop only its recorded PID;
never use a broad process-name kill.

```bash
kill "$(cat "/tmp/codex-logs/$TAG.pid")"
```

Resume by the recorded thread ID, never by "most recent" session on a shared machine:

```bash
env -u OPENAI_API_KEY codex exec --json resume "$(cat "/tmp/codex-logs/$TAG.thread")" \
  - < "/tmp/codex-followup-$TAG.md" > "/tmp/codex-logs/$TAG.resume.jsonl" 2>&1
```

The follow-up must say both what to stop doing and what work to continue.

## Recover and verify

Before trusting the final message, prove that it belongs to this run, then inspect the repository yourself:

```bash
[ "/tmp/codex-logs/$TAG.last.md" -nt "/tmp/codex-logs/$TAG.pid" ]
cat "/tmp/codex-logs/$TAG.last.md"
git status --short
git diff --stat
git diff --name-only
```

Run the target repository's relevant tests, lint, build, or execution probe again. Report partial work and failures
explicitly; a Codex claim is not verification.
