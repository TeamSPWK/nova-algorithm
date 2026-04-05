# Deep Dive TASK - Reference & Prompts

프롬프트 템플릿과 기술 참조. 문서 구조는 [templates.md](./templates.md) 참조.

---

## 1. LLM Client 사용법

```bash
# 기본 호출
python3 ~/.claude/skills/llm-review/llm_client.py \
  --provider [gemini|openai] --phase [consultation|review] \
  --prompt "$PROMPT" --output /tmp/result.json

# 파일 기반 프롬프트 (Phase 2 review용)
python3 ~/.claude/skills/llm-review/llm_client.py \
  --prompt-file "/docs/tasks/task-definition.md" --output /tmp/result.json

# 병렬 실행: & + wait $PID1 $PID2
# 결과 파싱: jq -r '.success' / jq -r '.response' / jq '.tokens'
```

**모델 (HARDCODED — 변경 금지)**:
- Consultation: `gemini-3-flash-preview`, `gpt-5.4`
- Review: `gemini-3.1-pro-preview`, `gpt-5.4` (Responses API, reasoning=high)

---

## 2. Consultation Prompt (Phase 1)

```
You are a senior software architect providing technical consultation.

# PROBLEM CONTEXT
{문제 설명 + 증거 (코드, 로그, 데이터) + 관련 파일 + 제약}

# YOUR TASK
1. Architecture & Design: 현재 접근법 적절한가? 대안?
2. Technical Feasibility: 제안된 해법이 실제로 동작하는가?
3. Trade-offs: 비용/품질/복잡도/유지보수성 트레이드오프
4. Implementation Risks: 엣지 케이스, 확장성, 보안
5. Recommendations: 구체적 다음 단계 (파일명, 라인 번호 수준)

# OUTPUT: 위 5개 섹션별로 구체적·현실적·우선순위화된 답변
```

---

## 3. Review Prompt (Phase 2)

```
You are reviewing a TASK definition document for technical implementation.

# TASK DEFINITION DOCUMENT
{전체 TASK 문서}

# YOUR REVIEW
1. Technical Feasibility: 코드 수정이 실제로 동작하는가? API 호환?
2. Missing Considerations: 에러, 엣지 케이스, 동시성, 성능, 보안, 하위호환
3. Risks: 구현/배포/운영/비즈니스 리스크 (확률+영향도)
4. Improvements: 더 단순하거나 견고한 대안

# OUTPUT: 위 4개 섹션별로 구체적·건설적·우선순위화된 피드백
```

---

## 4. Self-Review 체크리스트

TASK 문서를 코드 리뷰처럼 검토:

1. **Executive Summary**: 메트릭 달성 가능? 30초 이해 가능?
2. **AI Review**: 요약 정확? Accept/Reject 근거 충분? 모순 없음?
3. **Implementation**: 코드가 실제 동작? 경로 정확? 에러 처리?
4. **Validation**: 테스트가 모든 변경 검증? 기준 측정 가능?
5. **Risks**: 현실적 리스크 전부 나열? 완화 전략 실행 가능?
6. **Cross-cutting**: 기존 패턴과 일관? 10x 데이터 스케일? 6개월 후 유지보수?

**결과**: Critical Gaps (블로커) / Edge Cases (처리 필요) / Nice-to-have

---

## 5. AI 응답 처리 원칙

**CRITICAL**: AI 응답을 그대로 수용하지 말 것.

각 제안마다:
- **Accept**: 실현 가능 + 가치 있음
- **Defer**: 좋은 아이디어지만 현재 스코프 밖
- **Reject**: 비현실적, 코드베이스와 모순, 스코프 초과

Implementation-Ready 문서에 AI 원문을 넣지 말 것. 결정과 근거만 기록.
