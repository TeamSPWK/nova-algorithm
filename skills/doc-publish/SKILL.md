---
name: doc-publish
description: |
  레포의 `docs/` 문서를 swk-doc 디자인 시스템(blue + gray + red 3색)으로 HTML 화해
  `~/public_html/` 에 symlink 로 Tailscale 멤버에게 공유. SoT 룰: docs/ = git tracked 원본,
  ~/public_html/ = symlink only.

  Use proactively when user says "HTML로 만들어줘", "테일스케일로 띄워줘",
  "도식화해서 보여줘", "남에게 보여주게 페이지로", "공유 페이지 만들어줘",
  "doc publish", "/doc-publish", "이거 페이지로 띄워줘".

  Triggers: doc-publish, HTML로 공유, 테일스케일로 공유, 도식화, 시각화 페이지,
  공유 페이지, share as html, publish html, tailnet share.

  Do NOT use for: 일반 markdown 으로 충분한 문서, 코드/룰북(CLAUDE.md, AGENTS.md, .claude/rules/),
  단발 메모, 시크릿/자격증명 포함 가능 문서, 개인 작업물(이미 ~/public_html/ 자유 공간).
---

# doc-publish — Tailscale 멤버에게 공유할 HTML 문서 출간

트리거 / 안 트리거는 위 frontmatter 참조.

## 1. 5 step 절차

### Step 1 — 대상 결정
어떤 markdown / 주제를 HTML로 만들지 합의. 신규 작성 / 기존 HTML 리팩토링 구분.

### Step 2 — 자산 확인
swk-doc 디자인 시스템 자산 (SoT):
```
<repo>/docs/_assets/swk-doc.css   # 3색 토큰 + 박스 + 다크모드
<repo>/docs/_assets/swk-doc.js    # Mermaid CDN init + 코드블록 copy 버튼
```
없으면 `~/workspace/swk-infra/docs/_assets/` 에서 복사 (마스터). 새 레포면 그대로 복사하고 git tracked 적용.

### Step 3 — HTML 골격 (표준)
```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{문서 제목}</title>
<link rel="stylesheet" href="/_assets/swk-doc.css">
</head>
<body>
<main class="doc">

<h1>{제목}</h1>

<div class="doc-meta">
  <span><strong>대상</strong> {누구를 위한 문서}</span>
  <span><strong>작성</strong> YYYY-MM-DD</span>
  <span><strong>최종 갱신</strong> YYYY-MM-DD</span>
  <span><strong>SoT</strong> <code>docs/...</code></span>
  <span><strong>commit</strong> <a href="https://github.com/.../commits/main/...">history</a></span>
</div>

<p class="lead">한 줄 요약 — 이 문서가 뭐 하는 건지, 왜 보면 좋은지.</p>

<!-- 본문: §3 빌딩블록 조합 -->

<div class="doc-footer">SoT: <code>...</code>. 변경 시 그 쪽이 우선.</div>
</main>
<script type="module" src="/_assets/swk-doc.js"></script>
</body>
</html>
```

### Step 4 — Symlink + 검증
```bash
# 원본은 docs/ 안에 (git tracked), ~/public_html/ 에 symlink 만 (절대경로)
ln -sfn <repo>/docs/<path>/<name>.html ~/public_html/<short-name>.html

# 자산도 symlink (이미 있으면 skip)
[ -L ~/public_html/_assets ] || ln -sfn <repo>/docs/_assets ~/public_html/_assets

# 200 OK + Cache-Control 헤더 둘 다 확인
curl -sI http://127.0.0.1:8000/<short-name>.html | grep -iE "HTTP|cache-control"
```
> Cache-Control 헤더 없으면 본 LXC 의 `httpshare.service` 가 옛 버전 — swk-infra `docs/machines/swk-dev.md` §3.1.1 의 wrapper 적용.

### Step 5 — 사용자 안내
```
http://<hostname>:8000/<short-name>.html    # 신규 권장 (MagicDNS)
http://swk-dev:800X/<short-name>.html       # 옛 URL (~2026-06-01 한정)
```
`<hostname>` = 현재 LXC (`hostname` 으로 확인. josh-dev / jay-dev / suri-dev / sue-dev).
서버 단 `no-cache` 로 갱신 즉시 반영 — Ctrl+Shift+R 불필요.
선택: hub `~/public_html/index.html` 에 항목 추가 권유.

## 2. 컬러 (3색 강제)

| 색 | 용도 |
|---|---|
| **Blue** (primary) | 강조·링크·모든 info 박스 (note/case/why/ok), Mermaid 컨테이너 노드 |
| **Gray** (neutral) | 텍스트·배경·경계·보조 (before 박스, Mermaid 호스트/보조 노드) |
| **Red** (danger) | 경고만 — 위험·실패 시에만 (유일한 비-blue) |

박스 종류 구분은 **색이 아니라 라벨 텍스트** (📝/🎯/💡/✅/⚠️). case 박스 강조는 같은 blue 안에서 농도만 한 단계 진하게(`.case`).

위반 검출 — HTML 에 `style="color: (green|amber|purple|orange|yellow)"` 또는 `--green/--amber/--purple` 변수 사용 시 거부.

## 3. 빌딩블록 카탈로그

| 블록 | 용도 | 클래스 / 태그 |
|---|---|---|
| lead | 한 줄 요약 | `.lead` |
| Mermaid | 다이어그램 | `<pre class="mermaid">` |
| case | 실제 사례 (시간·장소·commit) — **핵심 패턴** | `.case` |
| before / after | 변경 전/후 비교 | `.before-after` |
| why / note / ok / warn | 동기·옵션·완료·경고 | `.why .note .ok .warn` |
| details | 자주 안 보는 참조 (Ctrl+F 안 잡힘) | `<details><summary>` |

### 예시

```html
<p class="lead">본인 LXD 컨테이너의 ~/public_html/ 에 둔 파일을 멤버에게 공유합니다.</p>
```

```html
<pre class="mermaid">
flowchart TB
  pc[멤버 PC] --> mine[&lt;hostname&gt;:8000]
  pc -.옛.-> swkdev[swk-dev:800X]
  swkdev -.proxy.-> mine

  classDef container fill:#dbeafe,stroke:#2563eb,color:#0f172a
  classDef host fill:#f1f5f9,stroke:#64748b,color:#0f172a
  class mine container
  class swkdev host
</pre>
```

```html
<div class="case">
  <span class="label">🎯 실제 사례</span>
  <strong>2026-05-18 — 사무실 IP 변경 사건이 직속 멤버 가입의 트리거.</strong>
  사무실 공인 IP가 .130 → .138 로 바뀌면서 SG 화이트리스트가 깨졌고, ...
  관련: <a href="...">commit 729d188</a>.
</div>
```
*추상 룰 옆에 시간/장소/사람/commit 이 있어야 신뢰도 ↑.*

```html
<div class="before-after">
  <div class="before"><h4>이전 (~2026-05-18)</h4><ul><li>URL: swk-dev:8002</li></ul></div>
  <div class="after"><h4>이후 (현재)</h4><ul><li>URL: jay-dev:8000</li></ul></div>
</div>
```

```html
<div class="why">  <span class="label">💡 WHY</span>   왜 이렇게 결정했나... </div>
<div class="note"> <span class="label">📝 NOTE</span>  옵션·예외·주의... </div>
<div class="ok">   <span class="label">✅ DONE</span>  완료/안전 상태... </div>
<div class="warn"> <span class="label">⚠️ WARN</span>  위험·실패 시나리오... </div>
```

```html
<details>
<summary>(참고) 호스트 측에서 이미 실행된 사항</summary>
<pre><code>...</code></pre>
</details>
```

## 4. SoT 룰 (절대 위반 금지) — CLAUDE.md §8 동일

| 항목 | 룰 |
|---|---|
| HTML 원본 | `<repo>/docs/...` (git tracked) |
| 노출 | `~/public_html/<name>.html` 은 **symlink 만** |
| 자산 | `~/public_html/_assets` → `<repo>/docs/_assets` symlink |
| 새 원본 두는 위치 | ❌ `~/public_html/` 직접 편집 / 새 원본 두지 말 것 |
| 예외 | 개인 작업물(repo 무관, hub index.html 등) 만 `~/public_html/` 원본 OK |

## 5. publish 전 체크

- [ ] 메타 헤더 (`.doc-meta`) — 작성일·갱신일·SoT 필수
- [ ] lead (`.lead`) 한 줄
- [ ] 컬러 위반 없음 (green/amber/purple/orange/yellow 사용 0)
- [ ] 시크릿 grep (`token|password|secret|api[_-]?key|aws_[a-z]+_key|bearer`) 매칭 0
- [ ] symlink 만 만들고 원본 복사 ❌
- [ ] `curl -sI` → 200 OK + `Cache-Control: no-cache` 헤더

## 6. 참조

- 디자인 시스템 SoT: `~/workspace/swk-infra/docs/_assets/swk-doc.{css,js}`
- 첫 데모: `~/workspace/swk-infra/docs/machines/swk-dev-setup-guide-v2.html`
- HTML SoT 룰: `~/workspace/swk-infra/CLAUDE.md` §8
- 노출 셋업: `~/workspace/swk-infra/docs/machines/swk-dev.md` §3.1.1
- 사용자 친화 howto: `~/HOWTO-public-html.md` (각 사용자 home 에 셋업 시 생성됨)
