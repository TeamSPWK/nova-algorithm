# team-play Templates

정적 참조 데이터. 본문에서 `Read templates/team-play-templates.md § [섹션명]`으로 참조.

---

## T1: Analysis Directive

> "Wrong analysis wastes the entire plan-implement-verify cycle. Do NOT guess — trace to the end. Read actual code, follow execution paths. 'It's probably X' is not analysis — report only facts confirmed by code evidence (file:line). If a claim uses hedging language ('seems like', 'probably', 'might be', 'likely'), it is automatically a Profiling Request — include a `## Profiling Request` section specifying: hypothesis, measurement needed, suggested method."

---

## T2: Gate Verification Table

```markdown
| # | Claim | Cited file:line | 직접 확인 (Read tool) | Match? | Verdict |
|---|-------|----------------|---------------------|--------|---------|
| 1 | [claim text] | [path:line] | [what the code actually says] | ✅/❌ | PASS/REJECT |
```

---

## T3: Direction Draft Format

```markdown
## Governing Principle
Fix the root cause, not the symptom — let the data shape the design.

## Root Causes (from Phase 1, verified)
- [RC1] ... (file:line)
- [RC2] ...

## Data Evidence Inventory
- bench_*.json / profiler 결과 / 로그 수치 (각 항목 경로 + 핵심 수치)
- 없으면: `[DATA GAP]` — 필요한 측정 명시

## Design Principles (이번 작업 한정)
- 데이터 구조 변경이 지배적인가, 알고리즘 변경이 지배적인가 (Pike: Data dominates)
- 유지할 경계(타입·스키마·모듈 계약)와 깨도 되는 경계 구분

## Direction Options (방향 후보 — plan 아님)
| # | 방향 (1-2 문장) | 해결 RC | 근거 데이터 | 임시방편? | 단순성 | 블라스트 |
|---|----------------|--------|-----------|----------|------|--------|
| A | ... | RC1,RC2 | bench:X% | ❌ | data-first | medium |

각 방향은 한두 문장 서술로만 기술. 파일·함수 이름 나열 금지 (그건 Phase 3).

## Pike Alignment
- Pike's Verdict: [Justified/Explore] — 동의/반박 + 근거
- 선택 방향이 "Data dominates" 원칙에 부합하는 이유

## Rejected Band-aids
- [거절한 임시방편 접근법 목록 + 거절 이유]

## Recommended Direction
**선택**: Option [X]
**왜 근본 해결인가**: ...
**왜 단순한가**: ...
**예상 영향 범위 (개략)**: 모듈/영역 수준 (파일 리스트 아님)
**열린 질문**: Phase 3에서 구체화할 판단 포인트
```

---

## T4: LLM Review Fixed Questions

> "다음은 방향성(design direction)에 대한 제안입니다. 구체 plan이 아닙니다. 반드시 답하세요:
> 1. Recommended Direction에 임시방편(band-aid / workaround / symptom patch)이 섞여 있는가?
> 2. 근본 원인(Root Cause)을 우회하지 않고 정면으로 해결하는가?
> 3. Rob Pike의 'Data dominates' 원칙에 비춰, 알고리즘을 복잡하게 만드는 대신 데이터 구조를 단순화하는 더 나은 방향이 있는가?
> 4. 데이터 근거 없이 주장된 성능·정확도 이득이 있는가?
> 5. 고려되지 않은 더 단순한 근본 해결 방향이 있는가?
> 구체 plan 제안은 하지 마세요 — 방향과 원칙 수준에서만 비평해 주세요."

---

## T5: Final Direction Output Format

```markdown
## Final Direction (Locked)
[최종 선택 + 서술 — plan 아님]

## LLM Review Response
- Gemini 지적: [요약] → 수용/반박 + 근거
- GPT 지적: [요약] → 수용/반박 + 근거

## Constraints for Phase 3 (Plan Gate will enforce)
- Plan은 이 방향을 벗어날 수 없음
- Rejected Band-aids 접근법은 plan 포함 금지
- 예상 영향 범위 밖 파일 수정 시 명시적 정당화 필요
```
