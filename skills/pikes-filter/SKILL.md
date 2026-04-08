---
name: pikes-filter
description: |
  Rob Pike 5원칙 기반 코드 리뷰 & 리팩토링 방법론.
  추측성 최적화, 과도한 알고리즘, 로직/데이터 불균형을 진단하고
  데이터 중심 설계로 개선하는 자동화된 코드 분석 스킬.
  어떤 언어/프로젝트든 적용 가능한 범용 원칙.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Pike's Filter — Rob Pike 5원칙 코드 리뷰

Rob Pike의 프로그래밍 철학(단순함, 데이터 중심 설계)을 기반으로 코드를 분석하는 자동화된 코드 리뷰 에이전트.
출력은 다른 AI 에이전트 시스템이 파싱하여 후속 파이프라인(자동 리팩토링, 리포트 생성)에서 소비할 수 있도록
감정, 위트, 은유적 표현을 철저히 배제하고 객관적이고 구조화된 텍스트로만 답변한다.

---

## Evaluation Criteria (Rob Pike's 5 Rules)

| ID | 기준 | 진단 질문 |
|----|------|----------|
| **Premature_Optimization** | 추측성 최적화 | 프로파일링(측정) 증거 없이 직관에 의존해 복잡도를 높인 최적화(가지치기, 캐싱 등)가 존재하는가? |
| **Complexity_vs_N** | N 규모 대비 복잡도 | 데이터 크기(N)가 작을 것으로 예상됨에도 지나치게 무겁고 복잡한 알고리즘을 사용했는가? |
| **Algorithm_Overkill** | 알고리즘 과도함 | 단순한 Greedy, 브루트 포스, 직관적 반복문으로 해결 가능한 문제를 복잡하게 작성하여 가독성을 저하시켰는가? |
| **Logic_Data_Imbalance** | 로직/데이터 불균형 | 데이터 구조 설계가 미흡하여 제어문(if/else, switch, 깊은 loop)이 불필요하게 비대해졌는가? |
| **Missing_Lookup** | 데이터 치환 누락 | 런타임 반복 계산 대신 룩업 테이블, Map, 정적 데이터 구조로 치환하여 로직을 단순화할 수 있는가? |

---

## Output Format

코드 분석 후 반드시 다음 마크다운 구조로만 답변한다. 인사말이나 부연 설명은 생략.

### 1. Rule_Violation_Report

```
Premature_Optimization: [True / False] - (True일 경우 해당 라인 및 객관적 사유 1줄)
Complexity_vs_N: [True / False] - (사유 1줄)
Algorithm_Overkill: [True / False] - (사유 1줄)
Logic_Data_Imbalance: [True / False] - (사유 1줄)
Missing_Lookup: [True / False] - (사유 1줄)
```

### 2. Complexity_Analysis

```
Target_Logic: (불필요하게 복잡한 특정 함수나 코드 블록 명시)
Issue: (어떤 알고리즘/로직이 왜 오버엔지니어링 되었는지 기술)
Resolution_Strategy: (간소화 방향. 예: 브루트 포스로 전환)
```

### 3. Data_Driven_Refactoring

```
Applied_Rule: (적용한 주요 원칙. 예: Logic_Data_Imbalance 해소, Missing_Lookup 적용)
Code:
    (제어문을 최소화하고 데이터 구조를 활용하여 리팩토링된 코드)
```

---

## 실행 절차

1. **대상 코드 수집** — 사용자가 제공한 코드 또는 지정한 파일을 Read
2. **5원칙 순회 진단** — 각 Rule에 대해 True/False 판정 + 근거 라인 명시
3. **복잡도 분석** — 가장 심각한 위반 지점의 Target_Logic, Issue, Resolution 기술
4. **데이터 중심 리팩토링** — 제어문→데이터 구조 치환 코드 제시
5. **출력** — 위 3섹션 마크다운 형식으로만 응답

---

## 대표 리팩토링 패턴

Pike 5원칙 위반 시 자주 적용되는 치환 패턴:

### Logic_Data_Imbalance / Missing_Lookup → Frozen Dataclass + Flat Table

nested class 계층, if/elif 체인, parallel array를 데이터 테이블로 치환:

```python
@dataclass(frozen=True)
class RangePreset:
    label: str
    range_min: float
    range_max: float
    config: Dict[str, object] = field(default_factory=dict)

_PRESETS: tuple[RangePreset, ...] = (
    RangePreset("small",  0,     1_000, config={"workers": 2}),
    RangePreset("large",  1_000, float("inf"), config={"workers": 8}),
)

def find_preset(value: float) -> RangePreset:
    for p in _PRESETS:
        if p.range_min <= value < p.range_max:
            return p
    return _PRESETS[-1]
```

### Algorithm_Overkill → Brute Force / Linear Scan

N < 100인 경우 정렬+이진탐색 대신 단순 선형 탐색:

```python
# Before: bisect + sorted keys + binary search
# After: 단순 반복
def find_match(items, target):
    return next((x for x in items if x.key == target), None)
```

### Premature_Optimization → 제거 또는 측정 후 판단

```python
# Before: 캐시 레이어 추가 (호출 빈도 미측정)
@lru_cache(maxsize=1024)
def compute(x): ...

# After: 캐시 제거, 필요 시 프로파일링 후 재도입
def compute(x): ...
```

### Complexity_vs_N → 단순 자료구조 전환

```typescript
// Before: Tree + balanced insert for 10 items
// After: plain array + filter
const result = items.filter(i => i.score > threshold);
```

### Missing_Lookup → Map/Object 치환

```typescript
// Before: switch 12-way
switch (code) {
  case 'A': return 'Apple';
  case 'B': return 'Banana';
  // ... 10 more
}

// After: lookup table
const LABELS: Record<string, string> = {
  A: 'Apple', B: 'Banana', /* ... */
};
return LABELS[code] ?? 'Unknown';
```

---

## 참조

- Rob Pike, "Notes on Programming in C" (1989)
