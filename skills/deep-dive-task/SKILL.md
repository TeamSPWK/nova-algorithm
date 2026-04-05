---
name: deep-dive-task
description: |
  Multi-AI consultation for structured TASK document creation + Team-based implementation.
  Phase 1-2: Parallel AI consultation + self-review → Implementation-ready document.
  Phase 3: Agent team implementation with Critic + Explorer teammates → Validated code.
allowed-tools: Read, Write, Bash, TaskOutput, Grep, Glob, AskUserQuestion
---

# Deep Dive TASK - Multi-AI Consultation Workflow

Transform user problems into implementation-ready TASK documents through parallel AI consultation and rigorous self-review.

**Output: 1 task = 1 file** (`docs/tasks/active/TASK-{slug}.md`)

---

## Prerequisites

1. **Read context** (first found wins):
   - `cat nova-context.md` (project root, next to CLAUDE.md)
   - If not found: read `CLAUDE.md` instead (project instructions as context)
2. **Check API keys**: `python3 ~/.claude/skills/llm-review/llm_client.py --check-keys`

---

## AI Models (HARDCODED — do NOT change)

| Phase | Gemini | OpenAI |
|-------|--------|--------|
| Consultation | `gemini-3-flash-preview` | `gpt-5.4` |
| Review | `gemini-3.1-pro-preview` | `gpt-5.4` (Responses API, reasoning=high) |

---

## LLM Client

```bash
python3 ~/.claude/skills/llm-review/llm_client.py \
  --provider [gemini|openai] --phase [consultation|review] \
  --prompt "$PROMPT" --output /tmp/result.json

# Parse: jq -r '.success' / jq -r '.response' / jq '.tokens'
```

---

## Phase 1: Consultation

### 1.1 Problem Structuring
Ask user: issue, goal, related files, constraints.
Create initial file: `docs/tasks/active/TASK-{slug}.md` with Problem + Consultation sections.

### 1.2 Parallel AI Consultation (180s timeout)
Run gemini & openai in parallel (`&` + `wait`), `--phase consultation`.

### 1.3 Claude Self-Analysis (parallel)
Explore codebase → root cause → 2-3 approaches → save `/tmp/claude_analysis_*.md`

### 1.4 User Discussion (parallel)
AskUserQuestion for unclear requirements. Timeout 90s → auto-proceed.

### 1.5 Integration & TASK Definition
1. Parse API responses
2. **Critical review** (do NOT blindly accept):
   - Each suggestion: **Accept/Reject/Defer** with reasoning
   - Compare against codebase reality, flag contradictions
3. Update the TASK file: add Implementation Plan section

**Document rules**: DO NOT dump full AI responses. Summarize with decisions. Focus on actionable insights.

### 1.6 User Approval (90s timeout → auto-proceed)

---

## Phase 2: Deep Review

### 2.1 High-Effort Feedback (600s timeout)
Send TASK to both providers (`--phase review`, `--prompt-file`).

### 2.2 Self-Review (parallel)
Line-by-line: technical accuracy, codebase consistency, scalability, maintainability.

### 2.3 Finalize Document
1. Parse feedback, **Accept/Reject/Defer** each suggestion
2. Update the same TASK file: set Status to `ACTIVE`, add Key Decisions + Result (expected)

**Final document = Agent-to-Agent communication**:
- Execution-focused (WHAT + HOW, not discussion)
- Readable by another agent in < 5 minutes
- Structured for immediate execution

### 2.4 Final Confirmation (90s timeout → auto-approve)

---

## Error Recovery

| Scenario | Recovery |
|----------|----------|
| Phase 1 rejection | Revise (max 2 iterations) |
| Partial API fail | Use available responses |
| All APIs fail | Claude-only or retry |
| Phase 2 fail | Self-review only |

---

## Deliverable

**Single file**: `docs/tasks/active/TASK-{slug}.md`

Lifecycle:
- Created in `docs/tasks/active/` during Phase 1
- Stays in `active/` during implementation
- Moved to `docs/tasks/done/YYYY-MM/` when completed

**Note**: For simple tasks, direct implementation may be faster.

**Details**: [templates.md](./templates.md), [reference.md](./reference.md)
