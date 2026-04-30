# Codex — Claude Code 에이전트용 코딩 위임 표준 가이드

> **에이전트가 codex CLI로 코딩 작업을 위임할 때 실전에서 발견한 요령 + 트러블슈팅 + 모니터링 패턴을 표준화**.
> 이 skill을 따르면 매번 trial-error 없이 일관된 위임 + 자동 stuck 감지 + 결과 회수까지 한 번에.

## 핵심 원칙 (이걸 어기면 시간 낭비)

1. **모든 코딩(구현) 단계는 codex로 위임** — 메인 에이전트는 조정/문서/판단만 (memory: feedback_codex_for_implementation)
2. **default 모델 = `gpt-5.3-codex`** — SWE-Bench Pro 56.8% (state-of-art, OpenAI 공식), Terminal-Bench 77.3%, 1M context, 다파일 refactor 강점 (출시: 2026-02-05)
3. **stdin은 항상 명시적 처리** — 인자만 줘도 stdin 미명시면 codex가 추가 입력 대기로 hang. **모든 호출에 `< /dev/null` 또는 `cat ... | codex exec` 필수** (실험 검증)
4. **`run_in_background: true` 필수** — `nohup ... &` OS background는 Claude Code 시스템 알림 안 옴
5. **AWS EC2 환경**: `--sandbox danger-full-access --skip-git-repo-check` 필수 (bwrap loopback 정책 우회)
6. **Stuck 자동 감지** — `--json` 사용 시 `turn.completed` 이벤트로 종료 판정 (안정). grep 시 "Reading additional input from stdin..." 후 5분 무변동 = hang. 즉시 kill + 재spawn
7. **결과 회수 = `-o output-last-message` + git diff + pytest** — 메인 직접 검증

---

## 코딩 원칙 (위임 시 codex가 지켜야 할 큰 줄기)

> 범용·언어 무관 원칙. 자세한 본문은 **`~/.claude/skills/codex/AGENTS.md`** 참조 (이 skill 디렉토리에 함께 보관).
> codex CLI는 working dir의 `AGENTS.md`를 자동 로드(project root → cwd, 32KB 한도)하므로, 프로젝트 루트에 복사·symlink:
> `ln -s ~/.claude/skills/codex/AGENTS.md ./AGENTS.md` (프로젝트 고유 규칙은 별도 `AGENTS.override.md`에).
> 일부 항목은 CLAUDE.md와 중복되지만 codex 입장에선 별도 컨텍스트라 명시 필요.

1. **Root cause 우선** — 증상만 가리는 band-aid 금지. 원인 모르면 추측 패치하지 말고 멈추고 보고. `try/except`로 에러 삼키기 금지, 안전 체크 우회(`--no-verify` 등) 금지.
2. **Pike 원칙 (데이터·단순 우선)** — 프로파일링 증거 없이 최적화 금지 / 작은 N에 과한 알고리즘 금지 / brute force·직관 loop으로 풀리면 그걸로 / 제어문 늘리기 전에 데이터 구조부터 / 런타임 계산 대신 lookup table.
3. **YAGNI / 변경 최소화** — 요청 범위 밖 리팩토링·추상화·feature flag·shadow 토글 금지. 새 코드는 바로 ON. 미래 확장성 가정 금지.
4. **Simple > Clever** — 직관적 이름, 작은 함수, 의도 명확. 영리한 한 줄보다 읽히는 세 줄.
5. **실 환경 검증** — mock으로 회귀를 가리지 않기. 검증은 실제 파이프라인·실 DB·실 데이터로. 테스트가 통과해도 실측이 아니면 통과 아님.

prompt에서는 한 줄로 참조:
```markdown
== 원칙 ==
{repo}/AGENTS.md 의 "코딩 원칙"(root cause / Pike / YAGNI / Simple>Clever / 실 환경 검증) 준수.
```

---

## Phase 1: spawn (옵션 자동 + stdin 명시 + 알림 활성화)

### 표준 명령 템플릿 (2가지)

```bash
# 표준: prompt 파일 stdin pipe (default — 길이 무관 안전)
cat /tmp/codex_prompt_{tag}.md | codex exec \
  -m gpt-5.3-codex \
  --sandbox danger-full-access \
  --skip-git-repo-check \
  --json \
  -o /tmp/codex-logs/{tag}_last.md \
  > /tmp/codex-logs/{tag}.log 2>&1

# 인라인 짧은 prompt: stdin 명시 종료 (`< /dev/null`) 필수
codex exec \
  -m gpt-5.3-codex \
  --sandbox danger-full-access \
  --skip-git-repo-check \
  -o /tmp/codex-logs/{tag}_last.md \
  "{짧은 prompt}" \
  < /dev/null \
  > /tmp/codex-logs/{tag}.log 2>&1

# 세션 이어가기 (resume은 subcommand)
codex exec resume {SESSION_ID} \
  -m gpt-5.3-codex \
  --sandbox danger-full-access \
  --skip-git-repo-check \
  -o /tmp/codex-logs/{tag}_resume_last.md \
  "{follow-up prompt}" \
  < /dev/null \
  > /tmp/codex-logs/{tag}_resume.log 2>&1
# (--last 로 가장 최근 세션 자동 선택도 가능)
```

**핵심**: 모든 호출에 stdin이 명시되어야 함 — 파이프(`cat ... |`) 또는 `< /dev/null`. 빠뜨리면 hang.

### Bash 도구 호출

**무조건 `run_in_background: true`** (Claude Code 시스템 알림 받음):

```python
Bash({
  command: "cat /tmp/codex_prompt_{tag}.md | codex exec ...",
  description: "Codex Sprint X.N {짧은 의도}",
  run_in_background: True,
})
```

### Prompt 파일 작성 규칙

prompt를 markdown 파일로 만들어 `/tmp/codex_prompt_{tag}.md`에 저장:

```markdown
# Sprint X.N {의도}

작업 디렉토리: BluePrintCheck (또는 명시 path)

== 정독 ==
1) {필수 파일 1}
2) {필수 파일 2}
...

== 구현 ==
A) {파일 1}: 변경 명세
B) {파일 2}: 변경 명세

== 자체 검증 ==
다음 명령 모두 PASS 확인:
1) python3 -m pytest tests/unit/{path}/ -v
2) {추가 검증}

== 하지 말 것 ==
- 다른 파일 수정 금지
- git commit/push 금지 (메인이 처리)
- {모듈별 금지 영역 명시}
```

### 옵션 별 설명

| 옵션 | 의미 | 필수 여부 |
|---|---|---|
| `-m gpt-5.3-codex` | default 모델 (다파일 refactor 강점) | ✅ |
| `--sandbox danger-full-access` | bwrap sandbox 비활성 (AWS EC2 환경 필수) | ✅ AWS EC2 |
| `--skip-git-repo-check` | trusted directory 거부 회피 | ✅ |
| `--json` | stdout JSONL 스트림 (모니터링·자동화에 강력) | 권장 |
| `-o, --output-last-message <FILE>` | 최종 메시지를 별도 파일에 기록 (결과 회수 자동화) | 권장 |
| `--ephemeral` | 세션 미저장 (1회성 호출 시) | 옵션 |
| `--output-schema <FILE>` | JSON Schema로 응답 강제 (구조화 자동화) | 옵션 |
| `-C, --cd {path}` | 작업 디렉토리 변경 (기본 cwd) | 옵션 |
| `codex exec resume <ID>` (subcommand) | 이전 세션 이어가기. `--last`로 최근 자동 선택 | 옵션 |

---

## Phase 2: 모니터링 (stuck 자동 감지 + 사용자 진행 가시화)

### 🎯 진행 가시화 — 메인 행동 지침 (필수)

**spawn 직후 반드시 Monitor 도구 같이 띄울 것** (skill 첫 spawn 시 누락 위험):

```python
# spawn 직후 Monitor 도구 호출
Monitor({
  description: "codex {tag} milestones",
  timeout_ms: 600000,  # 10분
  persistent: false,
  command: "tail -F /tmp/codex-logs/{tag}.log 2>/dev/null | grep -E --line-buffered \"tokens used|수정 파일|검증 결과|PASS|FAIL|Traceback|Error|RuntimeError|구현 완료|변경 내용|git diff|stuck|hang\"",
})
```

이걸로 milestone (PASS/FAIL/구현 완료/git diff 등) 도착 시 자동 알림 → 메인이 한국어 1~2줄 요약하여 사용자에 전달.

### 📊 메인 응답 시 progress 부가 (UX 개선)

**사용자가 다른 메시지를 보낼 때마다** 메인이 응답에 codex 진행 상황 한 줄 부가:

```
[codex {tag}] {N} lines, {M}m{S}s elapsed, 마지막: "{last meaningful line cut 100 chars}"
```

생성 명령:
```bash
LOG=/tmp/codex-logs/{tag}.log
LINES=$(wc -l < $LOG)
ETIME=$(ps -o etime= -p $(pgrep -f "codex exec" | head -1) 2>/dev/null | xargs)
LAST=$(tail -3 $LOG | grep -v "^codex" | grep -v "^[+-]" | head -1 | cut -c1-100)
echo "[codex {tag}] $LINES lines, $ETIME elapsed, 마지막: \"$LAST\""
```

이 한 줄을 사용자 응답 끝에 추가 → 사용자가 묻지 않아도 진행 가시. 알림 폭주 X (메인 응답 단위 1회).

### 정상 진행 신호

- `Reading additional input from stdin...` 첫 줄 (정상 — codex가 stdin block 검사 중. 명시적 stdin 처리 됐으면 즉시 다음 단계로)
- `model: gpt-5.3-codex / sandbox: danger-full-access / approval: never` 출력 (호출 정상)
- `--json` 사용 시: `{"type":"thread.started"}` → `turn.started` → `item.completed` → `turn.completed` 흐름 (실측)
- 평문 모드 시: log file 사이즈 점진 증가 (응답 streaming) → 마지막에 `tokens used {N}` 라인

### Stuck 신호 (즉시 대응)

| 신호 | 의미 | 대응 |
|---|---|---|
| `Reading additional input from stdin...`만 출력되고 5분+ 무변동 | **stdin이 명시적 처리 안 됨** (Bash background는 stdin inherits → codex가 추가 input 대기) | **kill + `< /dev/null` 또는 pipe 추가하여 재spawn** |
| `--json` 사용 중 `turn.failed` 이벤트 | 모델/도구 실행 실패 | 이벤트 payload 확인 후 prompt/sandbox 조정 |
| 15분+ log 변화 없음 (stdin 정상인데도) | API timeout | kill + 재spawn |
| `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` | sandbox 옵션 누락 | `--sandbox danger-full-access` 추가 |
| `Not inside a trusted directory` | trusted dir 미등록 | `--skip-git-repo-check` 또는 ~/.codex/config.toml 등록 |
| `failed to record rollout items: thread {id} not found` | 무해한 ERROR (codex 내부 추적 실패) | 무시 — 결과는 정상 |

### 자동 모니터링 명령

```bash
# 진행 체크 (3분 주기)
TASK_ID="{your_tag}"
LOG="/tmp/codex-logs/${TASK_ID}.log"
last_lines=0; stuck=0
while pgrep -f "codex exec" >/dev/null; do
  sleep 180
  lines=$(wc -l < "$LOG" 2>/dev/null || echo 0)
  delta=$((lines - last_lines))
  if [ $delta -eq 0 ]; then
    stuck=$((stuck+1))
    echo "[$(date +%H:%M:%S)] ⚠ STUCK#$stuck — $lines lines"
    [ $stuck -ge 2 ] && {
      echo "STUCK 6분+ — kill 권유"
      pkill -9 -f "codex exec.*${TASK_ID}"
      break
    }
  else
    stuck=0
    echo "[$(date +%H:%M:%S)] OK — $lines lines (+$delta)"
  fi
  last_lines=$lines
done
echo "DONE — final $(wc -l < "$LOG") lines"
```

**Bash 도구로 호출 시**: `run_in_background: true` + Monitor 도구 분리도 OK.

---

## Phase 3: 결과 회수 + 검증

### 자동 트리거 (Bash background task `completed` 알림 후)

```bash
# 1. log 마지막 30줄 확인
tail -30 /tmp/codex-logs/${TASK_ID}.log

# 2. git status — 어느 파일 수정됐나
git status --short

# 3. git diff stat
git diff --stat

# 4. 단위 테스트 (codex가 promtp 명령에 포함했어도 메인 검증 필수)
python3 -m pytest tests/unit/{영역}/ -x --tb=short 2>&1 | tail -10

# 5. 의도와 다른 파일 수정 여부 점검
# (codex가 prompt "하지 말 것" 어겨서 다른 파일 건드리는 경우 있음 — 발견 시 revert)
```

### Codex 응답 패턴 인식

정상 완료 응답:
- 마지막에 `tokens used {N}` 출력
- `변경 완료했습니다` 또는 `구현 완료` 언어
- 검증 결과 (pytest PASS 등) 인용
- `git diff` stat 자체 출력

부분 완료 응답:
- "다음 항목은 미구현" 명시
- 또는 prompt 일부 작업만 (메인이 추가 spawn 결정)

실패 응답:
- "환경에서 도구 실행 불가" — sandbox 문제
- pytest 실패 등 자체 검증 fail — 메인 추가 fix 위임

---

## Phase 4: 트러블슈팅 매트릭스

### A. stdin hang (가장 흔한 함정)

**증상**: log 첫 줄 `Reading additional input from stdin...` 후 무변동.

**진짜 원인** (실험 검증 — codex 0.125.0):
codex `exec`는 인자 prompt가 있어도 **stdin이 piped/redirected 됐는지 검사하고 있으면 추가 `<stdin>` block으로 합친다**. Bash 도구의 background 모드에서 stdin은 부모로부터 inherits되어 닫히지 않음 → codex가 stdin 입력을 영원히 대기 (실측 hang).

prompt 길이와 무관 — 짧은 인자도 hang. `$()` shell expansion 깨짐 가설은 부정확.

**해결 (3가지 안전 패턴)**:
```bash
# (1) stdin pipe — prompt 자체를 stdin으로 (default 추천)
cat /tmp/prompt.md | codex exec [opts]

# (2) 인자 prompt + stdin 명시 종료
codex exec [opts] "{짧은 prompt}" < /dev/null

# (3) 명시적 stdin 입력 (`-` sentinel)
cat /tmp/prompt.md | codex exec [opts] -
```

**금지 패턴**:
```bash
codex exec [opts] "{prompt}"          # ❌ 인자만 — stdin hang
codex exec [opts] "$(cat file.md)"    # ❌ shell expansion + stdin hang 이중 위험
```

### B. sandbox 실패 (bwrap loopback)

**증상**: codex 응답에 `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`.

**원인**: AWS EC2 unprivileged userns 정책으로 bwrap이 loopback 네트워크 구성 실패.

**해결**: `--sandbox danger-full-access` 추가. 또는 `--dangerously-bypass-approvals-and-sandbox`.

### C. Trusted directory 거부

**증상**: `Not inside a trusted directory and --skip-git-repo-check was not specified`.

**해결 (영구)**:
```toml
# ~/.codex/config.toml
[projects."/home/ubuntu/b-workspace/BluePrintCheck"]
trust_level = "trusted"
```

**해결 (1회용)**: `--skip-git-repo-check`

### D. nohup background — Claude Code 알림 미수신

**증상**: `nohup codex exec ... &` 실행 후 완료 알림 안 옴 (메인이 직접 status 폴링해야).

**원인**: OS-level backgrounding은 Claude Code task system 외부.

**해결**: Bash 도구의 `run_in_background: true` 사용:
```python
Bash({
  command: "codex exec ...",
  run_in_background: True,  # ← 이게 핵심
})
```

### E. 큰 prompt 인자 깨짐 (특수 문자)

**증상**: prompt에 `(?:...)` regex나 `$()` 같은 shell 특수 문자 → bash 해석 시 깨짐.

**해결**: 무조건 stdin pipe. shell expansion 우회.

### F. codex-rescue 서브에이전트 vs 직접 CLI

| 도구 | 옵션 패스스루 | 사용 케이스 |
|---|---|---|
| `codex:codex-rescue` 서브에이전트 (Agent tool) | ❌ `--sandbox`/`--skip-git-repo-check` 안 됨 | 표준 환경, 작은 작업 |
| **codex CLI 직접** (Bash) | ✅ 모든 옵션 가능 | AWS EC2 / 큰 prompt / 복잡 작업 |

→ 우리 환경은 codex CLI 직접 호출이 default.

---

## Phase 5: 모델 선택 가이드

OpenAI는 GPT-5.3-Codex 부터 SWE-Bench **Pro** (다국어/오염 저항) 점수를 공식 기준으로 사용. Verified는 Python-only라 codex 모델군은 Pro 비교가 표준.

| 모델 | SWE-Bench Pro | Terminal-Bench | Context | 속도 | 적합 |
|---|---|---|---|---|---|
| **`gpt-5.3-codex`** (default) | **56.8%** (state-of-art) | 77.3% | 1M | 보통 | 다파일 refactor, dependency graph, long-horizon |
| `gpt-5.3-codex-spark` (spark) | 낮음 (속도 특화) | — | 작음 | **1000+ tok/s** | 빠른 prototyping, 단순 변경 |
| `gpt-5.4` | gpt-5.3-codex와 비슷 | — | 1.05M | 보통 | computer use (브라우저 자동화) |

**default = `gpt-5.3-codex`** — 회귀 위험 큰 코드 변경. 다른 모델은 명시적 케이스만.

> 출처: OpenAI 공식 발표 (2026-02-05), `~/.codex/models_cache.json`에서 모델 등록 확인.

---

## Phase 6: 환경 setup (1회)

### 1. ~/.codex/config.toml 작성

```toml
# 자주 쓰는 프로젝트 trusted 등록
[projects."/home/ubuntu/b-workspace/BluePrintCheck"]
trust_level = "trusted"

[projects."/home/ubuntu/workspace/tektOCR"]
trust_level = "trusted"
```

### 2. codex login 확인

```bash
codex login status
# → "Logged in using ChatGPT" 또는 OpenAI API key 정보
```

### 3. /tmp/codex-logs 디렉토리 (1회)

```bash
mkdir -p /tmp/codex-logs
```

---

## Phase 7: 패턴 별 사용 예시

### A. 작은 단일 파일 변경

```bash
# 짧은 인라인 prompt — stdin 명시 종료 (`< /dev/null`) 필수
codex exec \
  -m gpt-5.3-codex \
  --sandbox danger-full-access \
  --skip-git-repo-check \
  -o /tmp/codex-logs/typo_last.md \
  "src/foo.py:42 의 typo \"recieve\" → \"receive\" 수정만. 다른 파일 수정 금지. git 커밋 금지." \
  < /dev/null \
  > /tmp/codex-logs/typo.log 2>&1
```

### B. 다파일 refactor (큰 작업)

```markdown
# /tmp/codex_prompt_refactor.md

== 정독 ==
1) avac/.../module.py
2) tests/unit/test_module.py
3) docs/architecture/L2-Module.md

== 구현 ==
A) module.py: function_x 시그니처를 (a, b, c) → (a, *, b, c) 변경 + 호출 사이트 9곳 갱신
B) test_module.py: 호출 사이트 갱신 + keyword-only 케이스 추가

== 자체 검증 ==
1) python3 -m pytest tests/unit/test_module.py -v
2) python3 -m pytest tests/ -x --tb=short

== 하지 말 것 ==
- L2 문서 수정 금지 (메인이 처리)
- git commit/push 금지
```

### C. PR 단위 작업 (자체 검증 + diff 출력)

prompt 끝에 추가:
```markdown
== 종료 시 ==
1. 모든 자체 검증 PASS 확인
2. git diff --stat 출력
3. 변경 요약 (3~5 bullet)
4. 발견된 위험/추가 작업 명시
```

---

## Phase 8: Skill 적용 워크플로우 (메인 에이전트용)

```
1. 메인이 작업 분석 → Sprint 분할 결정
2. 메인이 prompt 파일 작성 (/tmp/codex_prompt_{tag}.md)
   - "정독" / "구현" / "자체 검증" / "하지 말 것" 4 섹션 명시
3. 메인이 Bash run_in_background:true로 codex spawn
   - cat prompt.md | codex exec ... > /tmp/codex-logs/{tag}.log
4. 메인이 다른 작업 진행 (대기 중 PLAN 정리, 다음 sprint 준비 등)
5. 완료 알림 도착
   - log tail 확인
   - git status 확인
   - pytest 자체 검증 (codex 결과 신뢰 + 메인 재검증)
6. 회귀/이상 시 추가 fix prompt → codex resume 또는 새 spawn
7. ⭐ **Phase 9 — 코딩 단계 모두 끝나면 review 2종류 자동 spawn** (필수)
8. PR 머지 / push (메인 직접)
```

---

## Phase 9: 코딩 완료 후 자동 review (필수 — 머지 전 게이트)

**원칙**: 위임받은 모든 코딩이 끝나면(여러 sprint/phase 누적), **머지 전에 codex review 2종류 동시 진행**.
다관점 검증 필수: 일반 결함 + 디자인 challenge.

### 9.1 두 review 차이 (둘 다 필요)

| Review | CLI | 자세 | 목적 |
|--------|-----|------|------|
| **표준 review** | `codex exec review --uncommitted` | 객관적 | 결함/회귀/안전성 표준 점검 — 일반 코드 품질 |
| **Adversarial review** | `codex exec` + 적대적 prompt | **Default skepticism — "break confidence"** | 디자인 challenge — migration hazards / schema drift / version skew / rollback / idempotency / race / empty-state / observability gaps |

→ 표준 review는 잘 짜인 코드도 통과시키지만, adversarial은 "design choice가 ship 가능한가"를 묻는다. **둘 다 보자**.

### 9.2 Phase 9 spawn 패턴 (필수)

코딩 누적 끝난 시점에 메인이 다음 두 명령 **병렬** spawn (둘 다 read-only라 충돌 X):

```bash
# spawn 1: 표준 review (codex exec review subcommand — uncommitted 자동 대상)
codex exec review \
  --uncommitted \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check \
  -m gpt-5.3-codex \
  -o /tmp/codex-logs/review_${TAG}_last.md \
  < /dev/null \
  > /tmp/codex-logs/review_${TAG}.log 2>&1

# spawn 2: Adversarial review (codex exec + prompt로 자세 강제)
cat /tmp/codex_adversarial_prompt_${TAG}.md | codex exec \
  --sandbox danger-full-access \
  --skip-git-repo-check \
  -m gpt-5.3-codex \
  -o /tmp/codex-logs/adversarial_${TAG}_last.md \
  > /tmp/codex-logs/adversarial_${TAG}.log 2>&1
```

**Bash 도구 호출**: 둘 다 `run_in_background: true`로 동시 spawn — 자동 알림 받음.

### 9.3 Adversarial prompt 템플릿 (재사용)

`/tmp/codex_adversarial_prompt_{tag}.md`에 작성 (codex CLI에는 adversarial subcommand 없음 → prompt로 자세 강제):

```markdown
# Adversarial Review — {Sprint/Task 이름}

<role>
You are Codex performing an **adversarial software review**.
Your job is to **break confidence in this change**, not to validate it.
</role>

<task>
Review the current uncommitted changes (Phase 1+2+...+N of {task}).

Working tree: {N} files, {+P/-Q} lines.

Target: {한 줄 요약}
- {핵심 변경 1}
- {핵심 변경 2}
- ...

기준 문서: `{FROZEN_SPEC.md 또는 디자인 문서 경로}`
</task>

<operating_stance>
Default to skepticism.
Assume this change can fail in subtle, high-cost, or user-visible ways until evidence says otherwise.
Do not give credit for good intent, partial fixes, or likely follow-up work.
If something only works on the happy path, treat that as a real weakness.
</operating_stance>

<attack_surface>
Prioritize failures specific to this change:
- Migration hazards (data 변환 손실/왜곡)
- Schema drift (옛 enum/필드 잔재)
- Version skew (옛/신 동시 입력)
- Rollback safety (revert 시 깨지는 데이터)
- Idempotency (compat loader 두 번 호출 결과 동일?)
- Race conditions (동시 분류/마이그)
- Empty-state (빈 set/None)
- Invariant 우회 (validator 우회 가능?)
- Observability gaps (분포 변경 모니터링)
- {도메인 특화 attack surface 추가}
</attack_surface>

<review_method>
Actively try to disprove this change.
Look for violated invariants, missing guards, unhandled failure paths, assumptions that stop being true under stress.
Trace bad inputs / retries / concurrent actions through the changed code.
Read the actual diffs (uncommitted) — do NOT trust the documentation.

Specific deep-dives recommended:
1. {파일 1} — {challenge 질문}
2. {파일 2} — {challenge 질문}
...
</review_method>

<finding_bar>
Report only material findings.
A finding should answer:
1. What can go wrong?
2. Why is this code path vulnerable?
3. What is the likely impact?
4. What concrete change would reduce the risk?

Do not include style feedback, naming feedback, or speculative concerns without evidence.
</finding_bar>

<output_format>
Markdown report:
- ## Critical (must fix before ship)
- ## High (should fix)
- ## Medium (consider)
- ## Pass (no findings in this area)

각 finding마다 파일 경로 + 라인 번호 + 4-question 답변.
</output_format>
```

### 9.4 결과 통합 — 메인이 종합 (필수)

두 review 모두 끝나면 메인이 통합 보고:

```
## 🔀 Review 결과 종합 (Phase 9)

### ⛔ Critical (둘 다 지적 / 만장일치)
{만장일치 critical findings — 머지 전 fix 필수}

### 🚨 Critical 단독 (한 review만 지적)
- 표준 review (`codex exec review`):  {일반 review 단독}
- Adversarial review:                  {adversarial 단독}

### 🟡 High / Medium
{우선순위별 요약}

### ✅ Pass
{문제 없는 영역}

→ Critical fix 후 머지. High는 후속 task로.
```

### 9.5 Critical fix → 추가 codex spawn

만장일치 Critical 있으면 fix prompt 작성 → codex spawn → 재 review.

```bash
# fix → 재 adversarial review (regression 검증)
cat /tmp/codex_fix_prompt_${TAG}.md | codex exec ...
# 후 9.2의 adversarial review 명령으로 다시 검증
```

### 9.6 Phase 9 생략 케이스 (예외)

- 단일 파일 typo 수정 같은 trivial 변경 (사용자 명시)
- 문서만 변경
- 사용자가 명시적으로 review skip 지시

→ 그 외엔 **Phase 9 필수**. 큰 코드 변경 후 머지 전 게이트.

### 9.7 Phase 9 적용 cue (메인 행동)

다음 신호 중 하나라도 발생 시 자동 Phase 9 진입:
- 위임 모든 sprint/phase 끝남 (사용자 "끝났다" 인정 또는 phase 완료 알림 누적)
- 사용자가 "리뷰" / "검증" / "review" 언급
- PR 작성 직전
- 머지 직전

→ 메인이 alarm 받자마자 Phase 9 spawn 실행 + 사용자에 진행 보고.

---

## 자주 쓰는 명령 한 줄 요약

```bash
# 큰 prompt 작업 (background + 알림)
cat /tmp/codex_prompt_${TAG}.md | codex exec -m gpt-5.3-codex --sandbox danger-full-access --skip-git-repo-check -o /tmp/codex-logs/${TAG}_last.md > /tmp/codex-logs/${TAG}.log 2>&1

# 짧은 인라인 prompt (stdin 명시 종료 필수)
codex exec -m gpt-5.3-codex --sandbox danger-full-access --skip-git-repo-check -o /tmp/codex-logs/${TAG}_last.md "{prompt}" < /dev/null > /tmp/codex-logs/${TAG}.log 2>&1

# Phase 9 — 코딩 끝난 후 review 2종류 동시 (필수)
codex exec review --uncommitted --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -m gpt-5.3-codex -o /tmp/codex-logs/review_${TAG}_last.md < /dev/null > /tmp/codex-logs/review_${TAG}.log 2>&1
cat /tmp/codex_adversarial_prompt_${TAG}.md | codex exec --sandbox danger-full-access --skip-git-repo-check -m gpt-5.3-codex -o /tmp/codex-logs/adversarial_${TAG}_last.md > /tmp/codex-logs/adversarial_${TAG}.log 2>&1

# stuck 발생 시 kill (다른 작업 영향 없도록 TAG로 한정)
pkill -9 -f "codex exec.*${TAG}"

# session resume (subcommand)
codex exec resume ${SESSION_ID} -m gpt-5.3-codex --sandbox danger-full-access --skip-git-repo-check "{follow-up}" < /dev/null
# 또는 가장 최근 자동 선택
codex exec resume --last -m gpt-5.3-codex --sandbox danger-full-access --skip-git-repo-check "{follow-up}" < /dev/null

# 모델 가용 확인
codex --version
python3 -c "import json,re; print(sorted(set(re.findall(r'\"(gpt-5[^\"]*)\"', json.dumps(json.load(open('/home/ubuntu/.codex/models_cache.json')))))))"

# trusted 확인
cat ~/.codex/config.toml
```

---

## 메모리 정합

- `feedback_codex_for_implementation`: 코딩=codex (gpt-5.3-codex default)
- `feedback_no_sequential_multiproject`: 다중 프로젝트 LLM은 ThreadPool/병렬
- `feedback_pr_merge_preferred`: 코드 변경 PR squash, 문서 직접 push
- `feedback_no_external_uploads`: STG/PROD 영향 작업은 사용자 명시 지시 필수

---

## 변경 이력

| 날짜 | 변경 | 출처 |
|---|---|---|
| 2026-04-28 | 최초 작성 | Sprint X.0 codex spawn 시 발견된 stdin hang 등 요령 정리 |
| 2026-04-29 | **Phase 9 — 코딩 완료 후 자동 review 2종류 추가** (`/codex:review` + `/codex:adversarial-review`) + adversarial prompt 템플릿 + 자동 trigger cue + Phase 8 워크플로우에 Phase 9 단계 추가 | Step3 메타축 재설계 작업 (워크트리 step3-meta-axis-redesign) — 사용자 요청: "코딩 끝나면 두 review 자동 진행" |
| 2026-04-29 | **검증·정정 패스** — (1) stdin hang 진짜 원인 정정: prompt 길이가 아니라 **stdin 미명시**가 원인 (codex 0.125.0 실험 검증). 모든 명령에 `< /dev/null` 또는 stdin pipe 의무화. (2) `--resume` flag 문법 정정: 실제는 `codex exec resume <ID>` subcommand. (3) `--json`(JSONL) / `-o output-last-message` / `--output-schema` / `--ephemeral` 옵션 추가. (4) SWE-Bench 점수 정정: codex 모델군은 **SWE-Bench Pro 56.8%**가 공식 (Verified ~80%은 검증 불가). (5) Phase 9 표기 통일: `/codex:review` slash 표기 → `codex exec review` subcommand 정확 표기. (6) `pkill`을 TAG 한정으로 다른 작업 영향 차단. | 사용자 요청 "스킬 검증·실험·간결화" — 웹검색(OpenAI Codex docs) + 실험(작은 codex exec 호출 hang 재현/해결) + codex CLI 0.125.0 helptext 비교 |
