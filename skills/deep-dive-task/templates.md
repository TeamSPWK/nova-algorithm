# Deep Dive TASK - Document Template

단일 파일 템플릿. 프롬프트/레퍼런스는 [reference.md](./reference.md) 참조.

---

## TASK 파일 템플릿

파일: `docs/tasks/active/TASK-{slug}.md`

Phase 1에서 생성, Phase 2에서 갱신. 완료 시 `docs/tasks/done/YYYY-MM/`로 이동.

```markdown
# TASK: {제목}

Status: ACTIVE
Priority: P0 | P1 | P2
Created: {YYYY-MM-DD}

---

## Problem
{문제 상황 + 증거 (코드, 로그, 데이터)}
**Related Files**: {파일 목록}
**Goal**: {해결 후 기대 상태 + Success Criteria}

## Consultation
### AI Consultation Summary
| Topic | Gemini | GPT | Claude | Decision |
{각 제안별 Accept/Reject/Defer + Reasoning}

### Constraints
{시간, 리소스, 기술적 제약}

## Implementation Plan
### Phase 1: {Name}
**Goal**: {달성 목표}
**Tasks**:
- [ ] 1.1: {File}: {구체적 변경}
**Success Criteria**: {검증 방법}

### Phase 2: {Name}
...

## Validation
### Test Cases (최소 3개)
| Case ID | Scenario | Current | Expected | Priority |

### Pass Criteria
- P0: 100%, Regression: 100%, Overall: 80%+

## Risks & Mitigation
| Risk | Likelihood | Impact | Mitigation |

## Key Decisions (from AI Review)
**Accepted**: {결정 + 이유}
**Rejected**: {결정 + 이유}
**Deferred**: {후속 작업}

## Result
{완료 시 기재: 벤치마크 변화, 커밋 해시, 배포 상태}
Status: DONE ({YYYY-MM-DD})
```

---

## 섹션별 작성 시점

| 섹션 | Phase 1 | Phase 2 | 완료 후 |
|------|---------|---------|--------|
| Problem | O | - | - |
| Consultation | O | 보완 | - |
| Implementation Plan | 초안 | 확정 | - |
| Validation | - | O | - |
| Risks | - | O | - |
| Key Decisions | - | O | - |
| Result | - | - | O |
