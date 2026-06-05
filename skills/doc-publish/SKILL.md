---
name: doc-publish
description: |
  레포의 `docs/` 문서를 HTML 페이지로 출간 — md 만으로는 어려운 이해를 다이어그램·탭·TOC·박스 같은
  HTML 시각화로 돕고, `~/public_html/` 에 symlink 로 Tailscale 멤버에게 공유.
  본문 톤은 `josh-dev:9999/markwand/` 와 1:1 정렬 (베이지/teal/Inter/GFM Alert).
  오류·문제 분석(버그 RCA·이슈·장애·정합성)은 항상 최상단 sticky 2탭(🙂 쉬운 분석 먼저 / 🔬 상세 분석)+ 실물 이미지로 만들고, 상세 분석엔 file:line·코드 인용·로그·diff 까지 담는다.

  Use proactively when user says "HTML 로 만들어줘", "테일스케일로 띄워줘",
  "도식화해서 보여줘", "남에게 보여주게 페이지로", "공유 페이지 만들어줘",
  "doc publish", "/doc-publish", "이거 페이지로 띄워줘".

  Triggers: doc-publish, HTML 공유, 도식화, 시각화 페이지, share as html, publish html, tailnet share.

  Do NOT use for: 일반 markdown 으로 충분한 문서, 코드/룰북(CLAUDE.md, AGENTS.md, .claude/rules/),
  단발 메모, 시크릿/자격증명 포함 가능 문서, 개인 작업물(이미 ~/public_html/ 자유 공간).
---

# doc-publish

## 본질

**HTML 시각화 도구.** md viewer 가 아니다 — md 를 그대로 옮기려면 markwand(`josh-dev:9999/markwand/`) 가 이미 있다. doc-publish 의 가치는 md 만으로는 어려운 것 — **다이어그램·탭 전환·sticky TOC·before/after·GFM Alert·카드 그리드·인터랙션** — 으로 한 페이지에 담아 *남에게* 보여주는 데 있다.

본문 텍스트의 톤(색감·폰트·표·코드)은 markwand 와 1:1 정렬한다 — 그래야 시각화 요소가 "톤이 깨진 추가물" 이 아니라 "원래 그 페이지의 일부" 처럼 자연스럽게 보인다. 톤 정렬은 *수단*, 시각화가 *목적*.

## 5 step

### 1. 대상 결정
어떤 md / 주제를 페이지로 만들지 합의. 신규 작성인지 기존 HTML 리팩토링인지 구분. 단순 md 만으로 충분하면 doc-publish 안 씀.

### 2. 자산 확인
```
<repo>/docs/_assets/swk-doc.css   # v4 — markwand 톤 + GFM Alert 5색 + 빌딩블록
<repo>/docs/_assets/swk-doc.js    # Mermaid init + 코드블록 copy 버튼
```
없으면 `~/workspace/swk-infra/docs/_assets/` 에서 복사 (마스터). swk-doc.css 는 `/etc/nginx/markwand-tokens.css` (markwand v3.5, MIT) 토큰을 그대로 매핑.

### 3. HTML 골격
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
  <span><strong>SoT</strong> <code>docs/...</code></span>
</div>

<p class="lead">한 줄 요약.</p>

<!-- 본문 — §3 빌딩블록 적극 활용 -->

<div class="doc-footer">SoT: <code>...</code></div>
</main>
<script type="module" src="/_assets/swk-doc.js"></script>
</body>
</html>
```

### 4. Symlink + 검증
```bash
# 원본 = docs/ (git tracked), ~/public_html/ = symlink only
ln -sfn <repo>/docs/<path>/<name>.html ~/public_html/<short-name>.html
[ -L ~/public_html/_assets ] || ln -sfn <repo>/docs/_assets ~/public_html/_assets

# HTTP 200 + Cache-Control 확인
curl -sI http://127.0.0.1:8000/<short-name>.html | grep -iE "HTTP|cache-control"
```

### 5. 사용자 안내
```
http://<hostname>:8000/<short-name>.html    # MagicDNS (hostname = josh-dev 등)
```
서버 단 `no-cache` 적용 — Ctrl+Shift+R 불필요.

## 디자인 시스템 — 자산이 모두 들고 있음

본문 텍스트의 색·폰트·크기·자간·표·코드 톤은 **`swk-doc.css` 가 자동 적용**. HTML 안에서 inline `style="font-size/color/font-family/letter-spacing/..."` 를 직접 지정하지 말 것 — 깨진다.

기준 톤 (markwand v3.5):
- 배경 `#fbf7ef` (베이지 크림), 본문 `#20231f`, accent `#0f766e` (teal)
- 폰트 Inter / Pretendard / Apple SD Gothic Neo / Noto Sans KR
- 16px / line-height 1.7 / letter-spacing -0.003em
- h1 30px, h2 24px (둘 다 border-bottom), h3 20px, h4 18px
- 표 — zebra 없음. 상하 굵은 line + row hairline
- code — `#f4efe6` 베이지 톤

박스 (markwand GFM Alert 5색 매핑):
- `.note` blue (info) · `.why` green (tip) · `.ok` green (success)
- `.case` purple (important, 강조용) · `.warn` red (danger)

## 빌딩블록 (이게 doc-publish 의 본질)

markwand 가 못 하는 것들. 적극 활용.

| 블록 | 용도 | 마크업 |
|---|---|---|
| Mermaid | flowchart / sequence 등 — **렌더 후 반드시 Playwright 로 깨짐 검증** | `<pre class="mermaid">` |
| ASCII 박스 | 단순 도식 — **한국어 라벨이 많거나 의심스러우면 1순위** | `<pre><code>` |
| hero-diagram | 페이지 상단 통합도 (1회) | `.hero-diagram` |
| case / why / note / ok / warn | 의미 박스 (라벨 + 5색) | `.case` 등 |
| before / after | 변경 전후 2칸 | `.before-after` |
| landing-cards | 멀티-탭 진입 카드 | `.landing-cards` + `.landing-card` |
| details | 자주 안 보는 참조 | `<details><summary>` |
| tabs + TOC | 멀티 essay 통합 + sticky 목차 | 페이지별 정의 (modern-infra-essays.html 참조) |
| **error-2탭** | **버그/이슈/장애/정합성 분석 — 최상단 sticky 2탭(🙂 쉬운 분석 먼저 / 🔬 상세 분석), 필수** | §"오류·문제 분석" 참조 |
| **figure (이미지)** | **실물 증거(도면/스크린샷/로그/그래프) 크롭 삽입 — 글 100줄보다 강함** | `.fig` + `<figcaption>` (§"오류·문제 분석") |
| **decision-form + md-copy** | **사용자 입력 받기 (라디오/textarea) + 결과 markdown 일괄 클립보드 복사** | §"사용자 입력 받기" 참조 |

## 사용자 입력 받기 (의사결정 페이지 패턴)

doc-publish 가 단순 "보여주기" 를 넘어 **에이전트 ↔ 사람 의사결정 핸드오프** 도구가 될 때의 표준 패턴.
백엔드 없음 — 사용자가 페이지에서 입력 → **markdown 클립보드 복사** → 채팅에 paste → 에이전트가 받아 후처리. 가장 가볍고 마찰 없음.

### 5 원칙

1. **잘 보이는 곳에 "Markdown 복사" 버튼** — 페이지 하단 sticky bar 표준. 페이지가 길어도 항상 노출.
2. **자동 localStorage 저장** — 새로고침/탭 닫아도 입력 유지. 명시 저장 버튼 강요 X.
3. **라디오 default = 권고안** — 에이전트가 추천하는 안을 default checked. 사용자는 동의하면 그대로, 다르면 "다른 안" 라디오 + 텍스트.
4. **메모/사유 textarea 옵션** — 결정 사유 자유 입력. 후처리 시 컨텍스트.
5. **MD 복사가 메인, JSON 다운로드는 부수** — 클립보드 → 채팅 paste 가 사용자 마찰 최소. JSON 은 대량/구조화 필요할 때만.

### 구조

```
[페이지 본문 — 결정 항목별 설명 + 권고]
[각 항목 끝에 .decision-form 박스 — 라디오 + 텍스트 + textarea]
[페이지 하단 .commit-bar (position: sticky; bottom: 0) — 📋 MD 복사 / 📥 JSON 다운로드 / 🗑 클리어]
```

### 핵심 JS 패턴

```javascript
// 1) h3 텍스트 패턴 (예: "① 항목명") 으로 결정 항목 식별 → form 자동 주입
// 2) input/textarea change → localStorage 자동 저장
// 3) 페이지 로드 시 localStorage 복원
// 4) "MD 복사" 버튼 → navigator.clipboard.writeText(generatedMd)
//    실패 시 prompt() fallback (clipboard 권한 거부 가능)
// 5) JSON 다운로드는 Blob + a.download
```

생성되는 markdown 형식 (사용자가 채팅에 paste 하면 에이전트가 즉시 후처리 가능):

```markdown
# {task} 결정안 ({ISO timestamp})

## ① 비교 scope
- **결정**: (권고대로) 1차: landuse / districts / PNU 부터
- **메모**: 면적은 ±1㎡ 허용

## ② 정규화 규칙
- **결정**: (다른 안) 동의어 사전 + LLM normalization fallback
- **메모**: ...
```

### 참조 구현

`BluePrintCheck/docs/tasks/active/site-context-validation-20260528.html` — 11개 결정 항목 form 자동 주입 + sticky commit bar + localStorage + md/json export 풀구현 예시.

### 적용 기준

- ✅ **의사결정 항목 3개 이상** 모아서 받을 때
- ✅ 에이전트 권고안 제시 + 사용자 동의/수정 검토 흐름
- ✅ 결과를 task.md / PR description 등에 반영해야 할 때
- ❌ 단순 "보여주기" 페이지 (입력 0개) — 패턴 불필요
- ❌ 1~2개 짧은 결정 — 채팅에서 직접 묻는 게 빠름
- ❌ 다수 협업자 공유 의사결정 — localStorage 는 브라우저 종속, 백엔드 필요

### 클립보드 복사 — HTTP context 주의 ⚠️

`navigator.clipboard.writeText()` 는 **secure context (HTTPS / localhost) 에서만 동작.**
Tailscale `http://josh-dev:8000` 같은 평문 HTTP 에서는 권한 거부 → 사용자가 수동 복사로 떠밀림.

표준 패턴: **`<textarea>` 에 markdown 을 미리 렌더 + select() + `execCommand('copy')` fallback**.
복사 버튼 누르면 textarea 가 자동 보이고 selected 상태가 되어 Ctrl+C 가 즉시 동작.

```javascript
function copyMarkdown(md) {
  const ta = document.getElementById('md-output');
  ta.value = md;
  ta.style.display = 'block';
  ta.select();
  try {
    document.execCommand('copy');
    showToast('✅ 복사됨');
  } catch (e) {
    showToast('⚠️ Ctrl+C 로 직접 복사하세요 (textarea 선택됨)');
  }
}
```

`document.execCommand('copy')` 는 deprecated 이지만 HTTP context 에서 가장 안정적. secure context 면 modern API 가 우선이지만 fallback 으로 유지.

## 오류·문제 분석 — 최상단 sticky 2탭 (🙂 쉬운 분석 / 🔬 상세 분석) + 이미지

**버그 RCA·이슈 분석·장애 회고·정합성 문제를 publish 할 때는 항상 2탭으로 만든다.** 같은 사건을 두 독자가 본다:

- **🙂 쉬운 분석** — 비전문가용(기획·PM·고객·타팀). 전문용어 제거, 비유, 그림 우선, "무슨 일 → 왜 → 영향 → 어떻게 고치나" 흐름. **기본 활성 탭(먼저 보이는 탭).**
- **🔬 상세 분석** — 엔지니어용. file:line + **실제 코드 인용**, 로그·스택트레이스·diff 원문, 데이터 표, 호출 경로, 확정/추론/미확정 분류.

**탭은 페이지 최상단(sticky)에 둔다** — `<body>` 직속, `<main>` 위 (modern-infra-essays.html 의 `essay-tabs` 패턴). 스크롤해도 탭이 따라와 어디서든 깊이를 바꾼다. 제목·메타·한 줄 요약은 탭 아래 공통 헤더로 항상 보이게 두고, 탭은 그 아래 본문만 바꾼다. **쉬운 분석을 default(먼저)로** — 독자 다수가 비전문가이고, 엔지니어는 한 번 더 누르면 된다.

기술 탭만 있으면 비전문가가 못 읽고, 쉬운 탭만 있으면 엔지니어가 근거를 못 본다. **둘 다 만든다.**

### 골격 — 탭을 body 최상단에

```html
<body>

<!-- ① 최상단 sticky 탭 — body 직속, main 위. 쉬운 분석이 먼저(default active) -->
<nav class="rca-tabs" role="tablist" aria-label="분석 깊이">
  <button role="tab" data-tab="easy" aria-selected="true">🙂 쉬운 분석</button>
  <button role="tab" data-tab="tech" aria-selected="false">🔬 상세 분석</button>
</nav>

<main class="doc">

  <!-- ② 공통 헤더 — 탭과 무관하게 항상 보임 -->
  <h1>{사건 제목}</h1>
  <div class="doc-meta">
    <span><strong>대상</strong> {누구}</span>
    <span><strong>작성</strong> YYYY-MM-DD</span>
    <span><strong>SoT</strong> <code>docs/...</code></span>
  </div>
  <p class="lead">한 줄 요약 — 무슨 일이 있었나.</p>

  <!-- ③ 두 깊이의 본문 — 탭으로 전환. 쉬운 분석이 default-active -->
  <section class="rca-pane" id="pane-easy" data-active role="tabpanel"> ...쉬운 분석 본문... </section>
  <section class="rca-pane" id="pane-tech" role="tabpanel"> ...상세 분석 본문... </section>

  <div class="doc-footer">SoT: <code>...</code></div>
</main>
```

### 탭 CSS — swk-doc.css 에 탭 클래스가 없으므로 페이지 `<style>` 에 추가

> inline `style=` 금지 룰은 본문 톤(색·폰트) 얘기다. swk-doc.css 에 없는 신규 UI(탭/figure)는 페이지 `<style>` 블록에 클래스로 정의해도 된다. 단 색은 markwand 토큰(accent `#0f766e`, 베이지 `#fbf7ef`/`#e3dccb`/`#f1ead9`/`#897f6a`)과 맞춰 톤이 깨지지 않게.

```html
<style>
/* 최상단 sticky 탭 — modern-infra-essays.html 의 essay-tabs 패턴 */
body > .rca-tabs{position:sticky;top:0;z-index:50;background:#fbf7ef;border-bottom:1px solid #e3dccb;display:flex;gap:0;flex-wrap:wrap;padding:6px max(16px,calc((100vw - 880px)/2))}
.rca-tabs button{background:transparent;border:none;padding:10px 16px;font:inherit;font-weight:600;color:#897f6a;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;border-radius:6px 6px 0 0;letter-spacing:-0.003em;transition:all .15s}
.rca-tabs button:hover{color:#20231f;background:#f1ead9}
.rca-tabs button[aria-selected="true"]{color:#0f766e;border-bottom-color:#0f766e;background:#fff}
.rca-pane{display:none}
.rca-pane[data-active]{display:block}
.fig{margin:1.6rem 0}
.fig img{width:100%;border:1px solid #e3dccb;border-radius:6px;background:#fff}
.fig figcaption{font-size:.9rem;color:#897f6a;margin-top:.55rem;line-height:1.5}
.fig-narrow{max-width:760px}
</style>
```

### 탭 JS — 평범한 `<script>` 하나

```html
<script>
  const rcaTabs = document.querySelectorAll('.rca-tabs button');
  const rcaPanes = document.querySelectorAll('.rca-pane');
  rcaTabs.forEach(function(btn){
    btn.addEventListener('click', function(){
      rcaTabs.forEach(function(t){ t.setAttribute('aria-selected', t === btn ? 'true' : 'false'); });
      rcaPanes.forEach(function(p){
        if (p.id === 'pane-' + btn.dataset.tab) p.setAttribute('data-active','');
        else p.removeAttribute('data-active');
      });
      window.scrollTo({top:0,behavior:'smooth'});
    });
  });
</script>
```

`pane-{data-tab}` id 규칙. swk-doc.js 의 `type="module"` 스크립트와 별개로 이 `<script>` 하나면 동작.

### 두 탭 작성 원칙

**🙂 쉬운 분석 (먼저, default)** — "한 줄 요약"(`.case`) → "무슨 일이" → "그림으로 보기"(이미지) → "왜 그런가"(비유) → "다행인 점"(`.ok`) → "어떻게 고치나"(표) → "한 장 정리"(`.case`). 숫자·메커니즘은 비유로 풀고, `before/after` 로 정상 vs 오류를 대비. `.case/.note/.warn/.ok` 박스로 핵심만, 표는 최소. **코드·file:line 금지** — 그건 상세 탭 몫.

**🔬 상세 분석 — 코드 증거를 *매우 상세히***. 비전문가 배려한다고 뭉개지 말고, 엔지니어가 그대로 재현·검증할 수 있을 만큼 근거를 다 깐다. 다음 순서로:

1. **TL;DR**(`.case`) — 한 문장 결론 + 근본 원인 위치(`file:line`).
2. **증상** — 관측된 에러 메시지·스택트레이스·실패 로그를 **원문 그대로** `<pre><code>` 로. 요약하지 말고 실제 출력을 붙인다.
3. **데이터 흐름 / 호출 경로** — ASCII 박스로 입력→처리→출력, 어느 단계에서 깨졌는지 표시.
4. **근본 원인 — file:line + 실제 코드 인용 (핵심)**. 문제 라인마다 한 줄 설명이 아니라 해당 함수/블록을 `<pre><code>` 로 떠서, 어느 줄이 왜 틀렸는지 주석·화살표로 짚는다:
   ```html
   <p><code>engine/site_context.py:142</code> — PNU 정규화 누락:</p>
   <pre><code>def normalize_pnu(raw):
       # ⛔ 앞자리 0 이 int 변환에서 사라짐 — "0114..." → 114...
       return str(int(raw))        # ← 여기. zfill 보존 안 함
   </code></pre>
   ```
5. **before / after** — 깨진 코드 vs 고친 코드(또는 정상 입력 vs 오류 입력)를 `before-after` 2칸으로.
6. **재현 절차** — 실제 명령·입력값으로 재현 스텝. 가능하면 복붙 가능한 `curl`/스크립트.
7. **영향 범위** — 어떤 케이스·데이터·기간이 영향받았는지 표(실제 값).
8. **수정 위치** — 증상만 막는 곳 vs 근본 고치는 곳을 분리 명시.
9. **확정 / 추론 / 미확정** — 정직하게 분류. 확신도를 숨기지 말 것. 추론엔 "추정 근거", 미확정엔 "확인 방법" 을 적는다.

근거는 항상 **file:line + 실제 값/코드**. "아마 여기일 것" 으로 끝내지 말고 코드를 떠서 보인다. 인용이 길면 `<details>` 로 접되 핵심 라인은 펼친 채 둔다.

### 이미지·그림 — 적극 삽입

문제 분석은 **실물 증거(도면·스크린샷·로그·그래프)** 가 글 100줄보다 강하다. 큰 원본은 핵심 영역만 크롭한다.

```html
<div class="fig">
  <img src="/<short>-img/<name>.jpg" alt="설명">
  <figcaption><strong>제목.</strong> 핵심 포인트 + 강조 수치(<code>5.9</code> 등).</figcaption>
</div>
```

```bash
# 이미지는 docs 하위 img 폴더에 두고 public_html 에 폴더째 symlink
ln -sfn <repo>/docs/<path>/img/<topic> ~/public_html/<short>-img
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/<short>-img/<name>.jpg   # 200 확인
```

```python
# 큰 도면/스크린샷은 PIL 로 핵심 영역만 크롭 (예: 단면도 왼쪽 레벨 표기)
from PIL import Image
im = Image.open(src)                          # 원본 (예: 2977x2105)
im.crop((left, top, right, bottom)).save(out, quality=88)
```

크롭 후 **Read 도구로 한 번 열어** 의도한 영역(라벨·수치)이 담겼는지 눈으로 확인하고 좌표를 조정한다.

### 참조 구현

`BluePrintCheck/docs/reports/issue-2995-step6-pit-floor-height-20260602.html` — 2탭(쉬운/상세) + 도면 크롭 3장(GL 레벨 표기 강조) + `before/after`(정상 vs 오류) 풀구현. 같은 버그를 비전문가·엔지니어 두 버전으로. **신규 페이지는 위 골격대로 탭을 최상단 sticky 로 두고 🙂 쉬운 분석을 먼저(default) 둔다.**

### 적용 기준

- ✅ 버그 RCA / 이슈 분석 / 장애 회고 / 정합성·데이터 문제 분석 → **2탭 필수**
- ✅ 실물 증거(도면·스크린샷·그래프)가 있으면 → **크롭 삽입**
- ❌ 단순 안내·소개·가이드 문서 → 단일 탭으로 충분
- ❌ 독자가 엔지니어 한 종류뿐 → 기술 탭만

## SoT 룰 (절대)

| 항목 | 룰 |
|---|---|
| HTML 원본 | `<repo>/docs/...` (git tracked) |
| 노출 | `~/public_html/<name>.html` 은 symlink 만 |
| 자산 | `~/public_html/_assets` → `<repo>/docs/_assets` symlink |
| 예외 | 개인 작업물(repo 무관, hub index.html 등) 만 `~/public_html/` 원본 OK |

## 검증 — markwand 와 비교

같은 .md 를 양쪽에서 보고 본문 톤이 일치하는지 확인:

```
markwand (참조):    http://josh-dev:9999/markwand/?path=<url-encoded path>
doc-publish HTML:   http://josh-dev:8000/<short-name>.html
```

차이가 의심되면 Playwright 로 두 페이지의 셀렉터별 computed style diff (body/h1~h6/p/a/code/pre/table/blockquote 등) 를 비교. 위계가 어긋나면 HTML 안 inline 스타일이나 충돌 셀렉터를 의심.

## publish 전 체크

- [ ] `.doc-meta` (작성일·SoT) + `.lead` 있음
- [ ] inline 스타일로 색·폰트·사이즈 직접 지정 0
- [ ] **Mermaid 다이어그램이 있으면 Playwright 로 깨짐 검증** — 한국어 라벨·특수문자(`①`/`→`/괄호) 가 syntax error 자주 유발. 깨지면 ASCII 박스로 대체
- [ ] 시크릿 grep (`token|password|secret|api[_-]?key|bearer`) 매칭 0
- [ ] symlink 만 — `~/public_html/` 에 원본 두지 않음
- [ ] `curl -sI` → 200 OK + `Cache-Control: no-cache`
- [ ] **오류·문제 분석이면 최상단 sticky 2탭 둘 다 작성** — `<nav class="rca-tabs">` 가 `<body>` 직속(main 위), 🙂 쉬운 분석이 default active(먼저), 🔬 상세 분석은 file:line+코드 인용·로그·diff 까지. 패널 id(`pane-{data-tab}`) 일치 + 탭 토글 JS 포함
- [ ] **이미지 삽입 시** `~/public_html/<short>-img` 폴더 symlink + 각 이미지 `curl` 200 + 도면/스크린샷에 식별정보(고객·주소·시크릿) 노출 점검

**Mermaid 깨짐 검증 한 줄**:
```js
// /tmp/check.mjs — playwright 로 페이지 열고 console.error 잡기
import { chromium } from 'playwright';
const b = await chromium.launch();
const p = await (await b.newContext()).newPage();
const errs = [];
p.on('pageerror', e => errs.push(e.message));
p.on('console', m => m.type() === 'error' && errs.push(m.text()));
await p.goto('http://127.0.0.1:8000/<page>.html', { waitUntil: 'networkidle' });
await p.waitForTimeout(1500);
// mermaid 실패한 노드는 텍스트로 "Syntax error" 가 남는다
const ok = await p.$eval('body', el => !el.innerText.includes('Syntax error')).catch(() => false);
console.log(ok ? 'OK' : 'FAILED', errs);
await b.close();
```

## 외부 환경

swk-infra 없는 외부 레포에서 쓸 때 — 4 축만 치환:

| 축 | swk-infra | 로컬 대체 |
|---|---|---|
| 디자인 자산 | `<repo>/docs/_assets/swk-doc.{css,js}` | 본인 레포에 직접 복사 |
| 호스팅 | `httpshare.service` (Tailscale, no-cache) | `python3 -m http.server` / nginx / caddy |
| 공유 URL | `http://<hostname>:8000` (Tailnet) | `http://127.0.0.1:8000` 또는 본인 도메인 |
| 캐시 무효화 | 서버 단 `Cache-Control: no-cache` | 없으면 자산에 `?v=<mtime>` 쿼리 |

컬러·빌딩블록·골격 룰은 환경 무관 동일.

## 참조

- 디자인 자산 SoT: `~/workspace/swk-infra/docs/_assets/swk-doc.{css,js}`
- markwand 토큰 원본: `/etc/nginx/markwand-tokens.css`
- 실제 사용 예: `~/workspace/swk-infra/docs/essays/modern-infra-essays.html` (탭 + TOC + 5 essay 통합)
- HTML SoT 룰 (CLAUDE.md §8): `~/workspace/swk-infra/CLAUDE.md`
- HTTP 노출 셋업: `~/workspace/swk-infra/docs/machines/swk-dev.md` §3.1.1
