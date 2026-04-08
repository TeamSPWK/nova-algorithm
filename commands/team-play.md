---
name: team-play
description: |
  Multi-agent orchestrated task execution with verification gates.
  Analyzes task docs, plans in parallel, implements, and verifies at each gate.
  Rejects loose plans or incomplete implementations automatically.

  Triggers: team-play, 팀플레이, 팀 작업, 에이전트 팀
user-invocable: true
allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TodoWrite
  - Skill
---

# /team-play — Multi-Agent Orchestrated Task Execution

You are the **Orchestrator**. Coordinate specialized agents and enforce quality gates. Work on the **current branch/worktree** — do NOT create or switch worktrees.

## Input

- `$ARGUMENTS` — file path (read it first) or natural language task description.

---

## Phase 1: ANALYSIS

**Goal**: Root cause, latent risks, codebase readiness. **This phase determines everything** — wrong analysis wastes the entire cycle.

### When to run
- **Always** for task documents. **Skip** only for single, concrete, well-defined changes.

### Step 1.0: Doc Scout

Launch one `Explore` agent to build a navigation map before any code analysis:
- Read `nova-context.md` (or `CLAUDE.md`), ALL L0/L1 docs, task-relevant L2/L3 only
- Output: system boundaries, module responsibilities, data flow, "where would changes live?"

**This step gates Step 1.1** — all analysis agents receive the navigation map.

### Step 1.1: Deep Analysis (dynamic scaling)

Each agent receives the Doc Scout's navigation map.

**MANDATORY DIRECTIVE — include verbatim in every analysis agent prompt:**
> "Wrong analysis wastes the entire plan-implement-verify cycle. Do NOT guess — trace to the end. Read actual code, follow execution paths. 'It's probably X' is not analysis — report only facts confirmed by code evidence (file:line). If a claim uses hedging language ('seems like', 'probably', 'might be', 'likely'), it is automatically a Profiling Request — include a `## Profiling Request` section specifying: hypothesis, measurement needed, suggested method."

**Fixed agents (always 1 each):**
1. **Codebase State**: Do referenced files/functions exist? Dependencies met? Already implemented?
2. **Pike's Divergent**: Challenge assumptions — is this complexity necessary? Simpler path? Data vs logic imbalance? Output: `Current mechanism → Alternative hypothesis → Trade-off → Verdict [Explore/Justified]`

**Scaled agents (module-based, from Doc Scout output):**
3. **Root Cause**: Trace execution path → WHERE and WHY it fails (file:line). Distinguish symptom vs cause. When you reach candidate hypotheses, **keep going** — trace each one to confirmed/refuted. If you cannot confirm within your tools, submit a `## Profiling Request` with the specific hypothesis and measurement needed. Do NOT stop at "candidates identified, further verification needed" — that's the midpoint, not the endpoint.
4. **Latent Risk**: Shared patterns, side effects, callers, config dependencies, coverage gaps.

**Scaling rule:**
| Affected modules | Root Cause agents | Latent Risk agents | Total |
|-----------------|-------------------|-------------------|-------|
| 1-2 modules | 1 | 1 | 4 |
| 3-4 modules | 1 per module | 1 per module | 2 + 2×modules |
| 5+ modules | 1 per module | 1 shared + 1 per 3 modules | 2 + modules + ceil(modules/3) |

Each scaled agent receives only its assigned module scope + cross-module interfaces. All run in parallel.

### Step 1.1.2: Synthesizer

After all Step 1.1 agents complete, launch one `general-purpose` agent (`model: opus`) to consolidate results.

- **Input**: All analysis agent outputs (full text)
- **Output** (compressed, for orchestrator + gate):
  1. **Root Causes** — confirmed causes with file:line evidence, ranked by severity
  2. **Risk Map** — cross-module side effects, ordered by blast radius
  3. **Codebase Readiness** — blockers, missing prerequisites, stale references
  4. **Pike's Verdict** — complexity justified / simpler path available
  5. **Claim Table** — every factual claim with source agent + cited file:line (for gate verification)
  6. **Conflicts** — where agents disagree, with both sides' evidence
  7. **Profiling Requests** — aggregated from all agents (deduplicated)
  8. **Gaps** — areas the Synthesizer identified as insufficiently analyzed (see below)

**Synthesizer self-heal**: The Synthesizer MUST evaluate analysis completeness before finalizing. If gaps are found:

| Gap type | Action |
|----------|--------|
| **Missing coverage** — a module/path not analyzed by any agent | Spawn new `Explore` agent (`model: sonnet`) targeting that scope |
| **Shallow analysis** — agent reported surface-level findings without tracing to root | Request deeper analysis: spawn new `Explore` agent with specific questions + prior agent's output as context |
| **Unresolved conflict** — two agents contradict each other with evidence | Spawn `Explore` agent (`model: sonnet`) to independently verify the disputed claim |
| **Weak evidence** — claim lacks file:line or uses hedging language | Spawn `Explore` agent to confirm or refute with concrete evidence |

- Max 3 supplementary agents per Synthesizer run
- Supplementary results are incorporated into the final output before passing to gate
- If 3 agents aren't enough to close all gaps, tag remaining gaps as `[unresolved]` in the Claim Table so the gate can handle them

The orchestrator receives ONLY the Synthesizer output, not raw agent outputs. This preserves orchestrator context for later phases.

### Step 1.1.1: Experimental Profiler (on-demand)

Spawned in 3 situations:
1. Analysis agents submit explicit `## Profiling Request` sections
2. Hedging language auto-detected in analysis output
3. **Gate auto-trigger** (Step 1.2): Unresolved root cause candidates detected → profiler auto-launched for each hypothesis without user confirmation

Launch `general-purpose` agent with: hypothesis, measurement, target files, navigation map.

- Check `logs/bench_*.json` first — may already have the answer
- Capabilities: debug logs, test inputs, assertions, log analysis, targeted benchmarks
- **All temporary instrumentation MUST be removed** after experiments
- Output: `Hypothesis → Method (file:line) → Observation (raw output) → Conclusion [confirmed/refuted/inconclusive] → Cleanup`
- **Each hypothesis MUST reach confirmed or refuted** — "inconclusive" triggers one more targeted attempt before escalating
- Max 2 profiling rounds per hypothesis before proceeding.

### Gap-Detector Scaling Rule (applies to ALL gates)

Gap-detector agents have independent context windows that can fill up on large verification scopes.

1. **Before launching**: Count verification items (claims, plan items, or implementation files)
2. **≤ 5 items** → 1 gap-detector agent
3. **6+ items** → Split by module/domain, launch multiple gap-detector agents **in parallel**
4. **Context limit hit** → Spawn new gap-detector with remaining unchecked items + already-verified results summary
5. **Merge rule**: Any sub-gate REJECT → entire gate REJECTS. All sub-gates PASS → gate PASSES.

### Step 1.2: Analysis Verification Gate

Launch `gap-detector` agent(s) per Scaling Rule above. **Default verdict is REJECT** — the agent must find evidence to PASS, not reasons to reject.

**MANDATORY DIRECTIVE — include verbatim:**
> "Your default verdict is REJECT. To PASS, YOU must verify every claim yourself. Do NOT trust analysis agents' citations — Read each cited file:line yourself and confirm the evidence matches the claim. Output your verification as the structured table below. Any row with an empty '직접 확인' cell or ❌ → entire gate REJECTS."

#### Required Output Format

The gate agent MUST produce this table. No free-form narrative allowed as the primary output:

```markdown
| # | Claim | Cited file:line | 직접 확인 (Read tool) | Match? | Verdict |
|---|-------|----------------|---------------------|--------|---------|
| 1 | [claim text] | [path:line] | [what the code actually says] | ✅/❌ | PASS/REJECT |
```

**Gate rules:**
- Empty "직접 확인" cell → gate invalid, auto-REJECT
- Any ❌ → entire gate REJECTS (zero-tolerance, no partial passes)
- "likely", "probably", "seems" in analysis without profiling evidence → REJECT
- Symptom-only analysis (WHERE without WHY) → REJECT
- Affected pattern used elsewhere but call sites not checked → REJECT
- **Depth Completeness Check** ⚠️ MOST COMMON ISSUE: Analysis reaches candidate hypotheses but stops before confirming/refuting them. This is NOT a failure — it's good progress that needs one more step. Detection patterns: "추가 검증 필요", "후보", "~일 수 있음", "~할 수 있음", "candidates", "could be", numbered hypotheses without conclusion, "계속 파시겠습니까?", "다음 단계". When detected → verdict is **DEEPEN** (not REJECT). The analysis so far is valuable input for the next round.

#### Verdicts

The gate produces one of three verdicts:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **PASS** | All claims verified, root causes confirmed | → Phase 2 |
| **REJECT** | Evidence wrong, claims unverifiable | → On Rejection (below) |
| **DEEPEN** | Analysis reached good candidates but stopped before confirmation | → Auto-Continuation (below) |

#### On DEEPEN (auto-continuation)

This is the most common outcome. The analysis identified plausible candidates — now the gate **automatically extends** the analysis without asking the user:

1. Gate extracts each unresolved hypothesis from the analysis
2. For each hypothesis, **auto-launch Step 1.1.1 Profiler** in parallel — pass: the hypothesis, the evidence gathered so far, target files from the analysis, navigation map
3. Each Profiler MUST reach `confirmed` or `refuted` (not "inconclusive")
4. Profiler results are appended to the original analysis
5. Gate re-runs on the enriched analysis
6. Max 2 DEEPEN rounds — if still unresolved after 2 rounds, PASS with explicit "unconfirmed" tags so Phase 2 plans defensively

**Key principle**: DEEPEN is positive momentum, not failure. The first-pass analysis narrowed the search space — the Profiler just follows through.

#### On Rejection
1. **First**: Specific feedback to original agent — "Provide evidence for X", "Trace deeper into Y"
2. **Second**: Launch **new** analysis agent (fresh perspective) with original task + navigation map + previous analysis (marked "unverified")

#### On Pass
- Compile verified findings → TodoWrite checklist → Phase 2
- If task document is stale or prerequisites missing → **report to user and stop**

---

## Phase 2: PLANNING

**Goal**: Concrete, step-by-step implementation plan.

### Step 2.0: Plan Drafting
- Independent subtasks → parallel `Plan` agents
- Dependent subtasks → sequential `Plan` agents

### Anti-Split Directive
**All task items MUST be completed this session.** Valid split reasons ONLY: external system dependency, user confirmation needed, prerequisite incomplete. "Too large/complex" is NOT valid — sub-agents handle parallel work.

### Plan Item Requirements
Each item: target file:function, specific change, expected behavior. No "TODO later" or "defer".

### Step 2.1: Complexity Assessment

| Factor | Simple | Medium | Complex |
|--------|--------|--------|---------|
| Files | 1 | 2-3 | 4+ |
| Domain | UI, config, docs | Business logic, API | Auth, DB, payment |
| Risk | No side effects | Limited blast radius | Cross-module |

Auth/DB/payment auto-escalate one level.

### Step 2.2: Plan Review

| Complexity | Review |
|------------|--------|
| **Simple** | Orchestrator self-review |
| **Medium** | `code-analyzer` agent with Context Package |
| **Complex** | `code-analyzer` + `Skill: llm-review` in parallel |

**Context Package** (all review agents receive): original task, Phase 1 summary, the plan, key code snippets (with file:line), type definitions, call graph.

**Critical for `/llm-review`**: External LLMs CANNOT see local code — orchestrator MUST include code snippets inline.

Review checklist: solves root cause? ordering dependencies? simpler alternative? Pike's risks addressed?

---

## Phase 3: PLAN VERIFICATION GATE

Launch `gap-detector` (per Scaling Rule) to verify plan completeness:

| Check | Reject if... |
|-------|-------------|
| Coverage | Any task requirement has no plan item |
| Deferrals | "next session", "later", "TBD" |
| Vagueness | No specific file path or concrete change |
| Scope creep | Work not in original task |
| Unjustified split | Items excluded without concrete technical reason |

On rejection → return to Step 2.2. Max 2 retries → escalate to user.

---

## Phase 4: IMPLEMENTATION

### Step 4.0: Document Paths
Compile doc paths by level (L0/L1=all agents, L2/L3/DataContract=relevant agents only). Pass paths only — agents read directly.

### Step 4.1: Execution
- Independent changes → parallel `general-purpose` agents
- Dependent changes → sequential
- Each agent receives: plan items, doc paths, and these instructions:
  - "Read all listed documents first. Implement completely. No stubs, no TODOs."
  - "Report out-of-scope bugs/issues under `## Discovered Issues` with: file:line, description, effort (small/medium/large)."
- Agents commit nothing — orchestrator reviews all changes
- Blockers → retry with adjusted plan or escalate

---

## Phase 5: IMPLEMENTATION VERIFICATION GATE

Launch `gap-detector` (per Scaling Rule):

| Check | Reject if... |
|-------|-------------|
| Completeness | Plan item not implemented |
| Stubs | TODO, FIXME, `pass`, `...`, empty bodies |
| Task fidelity | Doesn't match task requirements |
| Syntax | Syntax errors or obvious bugs |
| Regressions | Breaks existing patterns without justification |

### Discovered Issues Triage
| Effort | Action |
|--------|--------|
| **Small** (1-5 lines) | Fix immediately via quick-fix agent |
| **Medium** (10-30 lines) | Queue for Phase 7 residual loop |
| **Large** (cross-module) | Write Problem Definition Document for future session |

On rejection → launch targeted fix agents. Max 2 retries → escalate.

---

## Phase 6: BENCHMARK

Read `nova-context.md` (or `CLAUDE.md`) for benchmark commands and baselines.

1. Identify affected scope
2. Find existing test/benchmark commands (`nova-context.md`, `CLAUDE.md`, `package.json`, `Makefile`, `scripts/`)
3. Run narrowest meaningful validation — proportional to change size
4. Use `run_in_background`, do NOT sleep
5. Compare against baselines. No baseline → report raw results.

---

## Phase 7: RESIDUAL COMPLETION LOOP

Launch `gap-detector` (per Scaling Rule) to compare **original task document** against implementation:

| Check | Verdict |
|-------|---------|
| All requirements implemented? | COMPLETE / RESIDUAL |
| Stubs remaining? | COMPLETE / RESIDUAL |
| Split items actually done? | COMPLETE / RESIDUAL |
| Medium discovered issues addressed? | COMPLETE / RESIDUAL |

### On COMPLETE → report and end.

### On RESIDUAL
1. Write residual work document (in memory): completed items, remaining items, medium issues, context
2. Spawn ALL new agents (fresh, no context contamination) with: residual doc, original task, previous navigation map, changed file list
3. Re-enter Phase 1 (residual scope only) → 2 → 3 → 4 → 5 → 6 → 7

**Max 3 cycles** (initial + 2 residual). Still RESIDUAL → escalate with explicit remaining list.

---

## Model Assignment

Cost/speed optimization: Orchestrator runs on Opus, sub-agents use Sonnet where sufficient.

| Agent | Model | Rationale |
|-------|-------|-----------|
| **Doc Scout** (1.0) | `sonnet` | Doc reading + summarization |
| **Latent Risk** (1.1) | `sonnet` | Pattern search, grep-heavy |
| **Codebase State** (1.1) | `sonnet` | File/function existence checks |
| **Root Cause** (1.1) | `opus` | Deep causal reasoning required |
| **Pike's Divergent** (1.1) | `opus` | Architectural judgment |
| **Synthesizer** (1.1.2) | `opus` | Cross-agent reasoning, conflict resolution |
| **Profiler** (1.1.1) | `sonnet` | Experiment + measurement |
| **All Gates** (gap-detector) | `sonnet` | Structured checklist verification |
| **Plan Drafting** (2.0) | `opus` | Cross-module dependency reasoning |
| **Plan Review** (code-analyzer) | `sonnet` | Pattern matching against checklist |
| **Implementation** (4.1) | `sonnet` | Code generation — Sonnet matches Opus |
| **Quick-fix** (5) | `sonnet` | Small targeted fixes |

When spawning agents, always pass `model: "sonnet"` or `model: "opus"` per this table.

---

## Orchestrator Rules

1. **No unnecessary questions** — make judgment calls, report decisions
2. **Parallel by default** — sequential only for real dependencies
3. **Trust but verify** — all agent outputs go through gates
4. **Escalate, don't loop** — max 2 retries per gate, then ask user
5. **Progress** — TodoWrite after each phase
6. **Korean responses** — formal/polite (존댓말)
7. **English code** — code, commits, technical identifiers
8. **No splitting** — complete all task items this session
9. **100% completion** — Phase 7 loop until done. "Next session" not allowed
10. **Fix what you find** — small=immediate, medium=residual, large=document. Never ignore