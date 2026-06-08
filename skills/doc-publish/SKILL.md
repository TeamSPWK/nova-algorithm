---
name: doc-publish
description: |
  레포의 `docs/` 문서를 HTML 페이지로 출간 — md 만으로는 어려운 이해를 다이어그램·탭·TOC·박스 같은
  HTML 시각화로 돕고, `~/public_html/` 에 symlink 로 Tailscale 멤버에게 공유.
  본문 톤은 `josh-dev:9999/markwand/` 와 1:1 정렬 (베이지/녹색/Inter/GFM Alert).
  오류·문제 분석(버그 RCA·이슈·장애·정합성)은 항상 최상단 sticky 2탭(🙂 쉬운 분석 먼저 / 🔬 상세 분석)으로 만든다.

  Use proactively when user says "HTML 로 만들어줘", "테일스케일로 띄워줘",
  "도식화해서 보여줘", "남에게 보여주게 페이지로", "공유 페이지 만들어줘",
  "doc publish", "/doc-publish", "이거 페이지로 띄워줘".

  Triggers: doc-publish, HTML 공유, 도식화, 시각화 페이지, share as html, publish html, tailnet share.

  Do NOT use for: 일반 markdown 으로 충분한 문서, 코드/룰북(CLAUDE.md, AGENTS.md, .claude/rules/),
  단발 메모, 시크릿/자격증명 포함 가능 문서, 개인 작업물(이미 ~/public_html/ 자유 공간).
---

# doc-publish

## 본질

**HTML 시각화 도구.** md viewer 가 아니다 — md 를 그대로 옮기려면 markwand(`josh-dev:9999/markwand/`) 가 이미 있다. doc-publish 의 가치는 md 만으로는 어려운 것 — **다이어그램·탭 전환·sticky TOC·before/after·카드 그리드·인터랙션** — 으로 한 페이지에 담아 *남에게* 보여주는 데 있다.

본문 톤(색·폰트·표·코드)은 markwand 와 1:1 정렬한다 — 그래야 시각화 요소가 "톤 깨진 추가물" 이 아니라 "원래 그 페이지의 일부" 처럼 보인다. 톤 정렬은 *수단*, 시각화가 *목적*.

## 5 step

### 1. 대상 결정
어떤 md / 주제를 페이지로 만들지 합의. 신규 작성인지 기존 HTML 리팩토링인지 구분. 단순 md 로 충분하면 doc-publish 안 씀.

### 2. 자산 확인
```
<repo>/docs/_assets/swk-doc.css   # ★ v6 표준 — 베이지+녹색 팔레트 + 공유 컴포넌트 전부 내장 (이거 하나만 로드)
<repo>/docs/_assets/swk-doc.js    # Mermaid init + 코드블록 copy 버튼
```
없으면 `~/workspace/swk-infra/docs/_assets/` 에서 복사 (마스터). **`swk-doc.css` 하나만 로드하면 v6(녹색·흙빛 semantic·탭·칩·figure·decision-form·toc-rail 등 공유 컴포넌트)가 다 들어온다** (2026-06-07 정식 병합, 1647줄). 옛 `swk-doc-v6-tokens.css` 는 deprecated **no-op 스텁** — 새로 링크하지 말 것(거기엔 아무 컴포넌트도 없다).

### 3. HTML 골격
```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{문서 제목}</title>
<link rel="stylesheet" href="/_assets/swk-doc.css"><!-- v6 표준 (팔레트·컴포넌트 내장) -->
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

<!-- 본문 — 빌딩블록 적극 활용 -->

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
curl -sI http://127.0.0.1:8000/<short-name>.html | grep -iE "HTTP|cache-control"   # 200 + no-cache
```

### 5. 사용자 안내
```
http://<hostname>:8000/<short-name>.html    # MagicDNS (hostname = josh-dev 등)
```
서버 단 `no-cache` 적용 — Ctrl+Shift+R 불필요.

## 디자인 규율 — v6 (베이지 + 녹색)

색·폰트·표·코드 톤 + 컴포넌트는 **`swk-doc.css` 가 자동 적용**. 페이지에서 inline `style=` / `<style>` 로 색·폰트를 직접 지정하지 말고 **토큰만** 쓴다. 팔레트 근거(OKLCH·WCAG AA·레퍼런스 Farrow&Ball·Aesop)는 `docs/_assets/DESIGN-SYSTEM-v6-palette.md`.

기준 톤 (참고용 hex — 페이지에선 `var(--swk-*)` 토큰명으로):
- 배경 `#f9f4e9` warm paper / surface `#fefbf6` / 본문 `#221f18` / **accent 녹색 `#446b3b`** (옛 teal `#0f766e` 폐기)
- muted `#635f50` / subtle `#786f5c` / border `#d0c8b8` / code `#eee7d8`
- 폰트 Inter·Pretendard·Apple SD Gothic·Noto Sans KR · 16px / lh 1.7 · h1 30 h2 24(둘 다 border-bottom) h3 20 h4 18 · 표 zebra 없음

callout (의미 박스 — v6: 녹색 + 흙빛 semantic, blue·purple·원색 폐기):
- `.note`·`.why` 정보·이유 (accent green subtle) · `.case` 핵심 강조 (green border)
- `.ok` 성공 (moss) · `.caution` 주의·보류 (ochre) · `.warn` 실패·위험 (terracotta)
- 상태가 아닌 단순 "강조" 에 semantic 쓰지 말 것 — accent 또는 weight 로.

**왜 규율인가** — doc-publish 의 1차 부채는 페이지마다 색·컴포넌트를 재발명한 것(103 페이지 중 71 개 자체 `<style>`, distinct hex 275 종, 외래 Tailwind 팔레트 침투). 새 페이지·리팩토링은 7항을 지킨다:

1. **색은 토큰만.** `<style>`/inline 에서 raw `#hex`·`rgb()`·`hsl()` 로 새 색 만들지 말 것. (예외: 데이터 시각화·증거 이미지 — legend 동반 시.)
2. **컴포넌트는 공유 레이어만 조합.** 탭·칩·카드·stat-band·figure·decision-form·commit-bar·toc-rail·repo-tag 는 `swk-doc.css` 에 이미 있다. 페이지에서 다시 정의하지 말 것. 새 컴포넌트가 진짜 필요하면 페이지가 아니라 v6 css 공유 레이어에 올린다.
3. **외래 팔레트 금지.** Tailwind slate/blue (`#0f172a`/`#475569`/`#2563eb`/`#f1f5f9`)·보라·청록·옛 teal·GitHub 원색 금지. accent = 녹색, 정보도 녹색(blue 아님), semantic = moss/ochre/terracotta.
4. **이모지를 chrome 색 노이즈로 쓰지 말 것.** nav·섹션 헤더·칩 라벨은 텍스트 + 카운트로.
5. **sticky nav/탭은 한 줄 고정.** 넘치면 `overflow-x:auto` + `flex-wrap:nowrap` 으로 **가로 스크롤** — 절대 `flex-wrap:wrap` 으로 세로로 쌓여 sticky 행이 깊어지게 두지 말 것. (filterbar 를 `flex:1` 로 탐욕적으로 키우면 칩이 세로로 무너진다.)
6. **클래스명 충돌 주의.** 공유 컴포넌트와 같은 이름(`.group-nav`/`.filterbar`/`.chip`)을 페이지에서 재정의하면 specificity 충돌로 한쪽이 덮인다(silent override). 페이지 고유 레이아웃은 고유 prefix(`.tbar-*`)로.
7. **페이지 `<style>` 허용 범위** = 특수 layout/SVG mechanics·print·grid column 수 정도. 그때도 색은 토큰.

자가 점검 (publish 전) — distinct hex 를 늘리지 않는 게 세련됨. 색을 더하면 후퇴다:
```bash
rg -n '#[0-9a-fA-F]{6}|rgb\(|hsl\(' <file>.html             # → 토큰 외 0 (swatch·data-viz 예외만)
rg -n 'slate|#0f172a|#2563eb|#8b5cf6|#0f766e' <file>.html   # → 0 (외래 팔레트·옛 teal)
```

## 빌딩블록 (이게 doc-publish 의 본질)

markwand 가 못 하는 것들. 적극 활용.

| 블록 | 용도 | 마크업 |
|---|---|---|
| Mermaid | flowchart / sequence — **렌더 후 반드시 Playwright 로 깨짐 검증** | `<pre class="mermaid">` |
| ASCII 박스 | 단순 도식 — **한국어 라벨 많거나 의심스러우면 1순위** | `<pre><code>` |
| hero-diagram | 페이지 상단 통합도 (1회) | `.hero-diagram` |
| callout | 의미 박스 (note/why/case/ok/caution/warn) | `.case` 등 |
| before / after | 변경 전후 2칸 | `.before-after` |
| landing-cards | 멀티-탭 진입 카드 | `.landing-cards` + `.landing-card` |
| chip / stat-band / repo-tag | 상태 badge · 숫자 요약 · 출처 표시 | `.chip[data-tone]` · `.stat-band` · `.repo-tag` |
| tabs + TOC / sidebar | 멀티 essay · 긴 인덱스 sticky 목차 | `.essay-tabs` · `.toc-rail` (≥1100px 좌측) |
| details | 자주 안 보는 참조 | `<details><summary>` |
| **error-2탭** | **버그/이슈/장애/정합성 분석 — 최상단 sticky 2탭, 필수** | §특수 패턴 B |
| **figure (이미지)** | **실물 증거(도면/스크린샷/로그/그래프) 크롭 — 글 100줄보다 강함** | `.fig` + `<figcaption>` (§특수 패턴 B) |
| **decision-form** | **사용자 입력 받기 + 결과 markdown 복사** | §특수 패턴 A |

## SoT 룰 (절대)

| 항목 | 룰 |
|---|---|
| HTML 원본 | `<repo>/docs/...` (git tracked) |
| 노출 | `~/public_html/<name>.html` 은 **symlink 만** |
| 자산 | `~/public_html/_assets` → `<repo>/docs/_assets` symlink |
| 예외 | 개인 작업물(repo 무관, hub index.html 등) 만 `~/public_html/` 원본 OK |

## 검증 — markwand 와 비교

같은 .md 를 양쪽에서 보고 본문 톤이 일치하는지:
```
markwand (참조):    http://josh-dev:9999/markwand/?path=<url-encoded path>
doc-publish HTML:   http://josh-dev:8000/<short-name>.html
```
차이가 의심되면 Playwright 로 셀렉터별 computed style diff(body/h1~h6/p/a/code/pre/table). 어긋나면 inline 스타일이나 충돌 셀렉터를 의심.

## publish 전 체크

- [ ] `.doc-meta`(작성일·SoT) + `.lead` 있음 · `swk-doc.css` 한 줄 로드 (별도 토큰 파일 X)
- [ ] **색·컴포넌트 규율 자가 점검 grep 통과** (§디자인 규율 — raw 색·외래 팔레트·옛 teal 0)
- [ ] 탭·칩·카드·figure·decision-form·toc-rail 은 **공유 컴포넌트 재사용** (페이지 재정의 0), sticky nav/탭 한 줄 고정
- [ ] **Mermaid 있으면 Playwright 로 깨짐 검증** — 한국어 라벨·특수문자(`①`/`→`/괄호)가 syntax error 유발. 깨지면 ASCII 박스로 대체
- [ ] 시크릿 grep `token|password|secret|api[_-]?key|bearer` → 0 · 이미지에 식별정보(고객·주소) 노출 점검
- [ ] symlink 만 (`~/public_html/` 원본 X) · `curl -sI` → 200 + `Cache-Control: no-cache`
- [ ] **오류·문제 분석이면 §특수 패턴 B 의 2탭 둘 다 작성** (🙂 쉬운=default, 🔬 상세=file:line+코드+로그)

Mermaid 깨짐 검증 (playwright 스니펫) — 실패 노드는 텍스트에 `Syntax error` 가 남는다:
```js
import { chromium } from 'playwright';
const b = await chromium.launch(); const p = await (await b.newContext()).newPage();
await p.goto('http://127.0.0.1:8000/<page>.html', { waitUntil: 'networkidle' });
await p.waitForTimeout(1500);
const ok = await p.$eval('body', el => !el.innerText.includes('Syntax error')).catch(() => false);
console.log(ok ? 'OK' : 'FAILED'); await b.close();
```

---

# 특수 패턴 (필요할 때만)

대부분의 publish 는 위까지로 끝난다. 아래 둘은 **해당 상황에서만** 쓴다.

## 특수 패턴 A — 사용자 입력 받기 (decision-form)

에이전트 ↔ 사람 의사결정 핸드오프 도구. 백엔드 없음 — 페이지에서 입력 → **markdown 클립보드 복사** → 채팅에 paste → 에이전트가 후처리.

**언제** — ✅ 결정 항목 **3개 이상** 모아 받을 때 / 권고안 제시 + 동의·수정 흐름 / 결과를 task.md·PR 에 반영. ❌ 단순 보여주기(입력 0) · 1~2개 짧은 결정(채팅이 빠름) · 다수 협업자 공유(localStorage 는 브라우저 종속 → 백엔드 필요).

**구조** — 본문 결정 항목별 설명+권고 → 각 항목 끝 `.decision-form`(라디오+textarea) → 페이지 하단 `.commit-bar`(`position:sticky;bottom:0`) 📋 MD 복사 / 📥 JSON / 🗑 클리어.

**원칙** — ① MD 복사 버튼은 하단 sticky 로 항상 노출 ② 입력은 localStorage 자동 저장(새로고침 유지) ③ 라디오 default = 권고안 checked ④ 사유 textarea 옵션 ⑤ MD 복사가 메인, JSON 은 대량일 때만.

생성 markdown(사용자가 paste 하면 즉시 후처리 가능):
```markdown
# {task} 결정안 ({ISO timestamp})
## ① 비교 scope
- **결정**: (권고대로) 1차: landuse / districts / PNU
- **메모**: 면적은 ±1㎡ 허용
```

⚠️ **클립보드 gotcha (필수)** — `navigator.clipboard.writeText()` 는 secure context(HTTPS/localhost)에서만 동작. Tailscale 평문 HTTP(`josh-dev:8000`)에선 권한 거부 → 조용히 실패. **표준 대응**: `<textarea>` 에 md 를 미리 렌더 → `display:block` → `select()` → `document.execCommand('copy')`(실패 시 "Ctrl+C 로 복사" toast). execCommand 는 deprecated 지만 **HTTP context 에서 가장 안정적** — fallback 으로 유지.

**참조 구현** — `josh-dev:8000/db-relay-decisions.html` (swk-infra `docs/tasks/active/managed-db-relay-decisions.html`) · `site-context-3d-decisions.html` — decision-form + sticky commit-bar + localStorage + md 복사 풀구현.

## 특수 패턴 B — 오류·문제 분석 (최상단 sticky 2탭)

**버그 RCA·이슈·장애 회고·정합성 문제는 항상 2탭으로.** 같은 사건을 두 독자가 본다:
- **🙂 쉬운 분석** (비전문가 — 기획·PM·고객) — 용어 제거, 비유, 그림 우선, "무슨 일→왜→영향→어떻게". **기본 활성 탭(먼저).**
- **🔬 상세 분석** (엔지니어) — file:line + 실제 코드 인용, 로그·스택트레이스·diff 원문, 데이터 표, 확정/추론/미확정.

기술 탭만 있으면 비전문가가 못 읽고, 쉬운 탭만 있으면 엔지니어가 근거를 못 본다 → **둘 다 만든다.** 쉬운 분석을 default 로(엔지니어는 한 번 더 누르면 됨).

**언제** — ✅ 버그 RCA·장애·정합성·데이터 문제 → 2탭 필수 / 실물 증거 있으면 크롭 삽입. ❌ 단순 안내·가이드 → 단일 탭 / 독자가 엔지니어뿐 → 기술 탭만.

**골격** — §3 HTML 골격에 더해, 탭 `<nav>` 를 `<body>` 직속(main 위)에 두고 본문을 두 pane 으로:
```html
<body>
<nav class="rca-tabs" role="tablist" aria-label="분석 깊이">
  <button role="tab" data-tab="easy" aria-selected="true">🙂 쉬운 분석</button>
  <button role="tab" data-tab="tech" aria-selected="false">🔬 상세 분석</button>
</nav>
<main class="doc">
  <h1>…</h1> <div class="doc-meta">…</div> <p class="lead">…</p>  <!-- 공통 헤더, 항상 보임 -->
  <section class="rca-pane" id="pane-easy" data-active role="tabpanel">…쉬운…</section>
  <section class="rca-pane" id="pane-tech" role="tabpanel">…상세…</section>
</main>
```
`.rca-tabs`·`.rca-pane`·`.fig` CSS 는 `swk-doc.css` 에 내장 — **페이지에서 재정의 말 것**(옛 가이드가 페이지 `<style>` 에 직접 정의하라 한 게 sprawl 원인이었다). 마크업만 쓴다. 토글 JS 만 페이지에 둔다:
```html
<script>
  const tabs = document.querySelectorAll('.rca-tabs button'), panes = document.querySelectorAll('.rca-pane');
  tabs.forEach(b => b.addEventListener('click', () => {
    tabs.forEach(t => t.setAttribute('aria-selected', t === b ? 'true' : 'false'));
    panes.forEach(p => p.id === 'pane-' + b.dataset.tab ? p.setAttribute('data-active','') : p.removeAttribute('data-active'));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }));
</script>
```
> 이 토글은 매 페이지 복붙이라 drift 위험 — 후속으로 `swk-doc.js` 공유 레이어에 올리면 0 (개선 후보).

**쉬운 분석** — 한 줄 요약(`.case`) → 무슨 일 → 그림(이미지) → 왜(비유) → 다행인 점(`.ok`) → 어떻게 고치나(표) → 한 장 정리. `before/after` 로 정상 vs 오류 대비. **코드·file:line 금지**(상세 탭 몫).

**상세 분석** — 엔지니어가 그대로 재현·검증할 만큼 근거를 다 깐다. 순서: `TL;DR(file:line) → 증상(로그·스택트레이스 원문 그대로, 요약 금지) → 호출경로(ASCII) → 근본원인(file:line + 실제 코드 인용, 어느 줄이 왜 틀렸는지 주석) → before/after → 재현 절차 → 영향 범위(표) → 수정 위치(증상 막기 vs 근본) → 확정/추론/미확정 정직 분류`. **근거는 항상 file:line + 실제 값/코드** — "아마 여기일 것" 으로 끝내지 말고 코드를 떠서 보인다.

**이미지·그림** — 실물 증거(도면·스크린샷·로그·그래프)는 글 100줄보다 강하다. 큰 원본은 PIL 로 핵심 영역만 크롭(`im.crop((l,t,r,b)).save(out, quality=88)`). **크롭 후 Read 로 한 번 열어** 의도한 영역(라벨·수치)이 담겼는지 눈으로 확인하고 좌표 조정. docs 하위 img 폴더에 두고 폴더째 symlink:
```bash
ln -sfn <repo>/docs/<path>/img/<topic> ~/public_html/<short>-img
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/<short>-img/<name>.jpg   # 200
```
```html
<div class="fig"><img src="/<short>-img/<name>.jpg" alt="설명">
  <figcaption><strong>제목.</strong> 핵심 포인트 + 강조 수치(<code>5.9</code>).</figcaption></div>
```

**참조 구현** — `BluePrintCheck/docs/reports/issue-2995-step6-pit-floor-height-20260602.html` — 2탭 + 도면 크롭 3장 + `before/after` 풀구현. (live 2탭 예: `josh-dev:8000/icheon-floor-area-ocr.html`)

## 외부 환경

swk-infra 없는 외부 레포에서 쓸 때 — 4 축만 치환 (컬러·빌딩블록·골격 룰은 환경 무관 동일):

| 축 | swk-infra | 로컬 대체 |
|---|---|---|
| 디자인 자산 | `swk-doc.css` (v6 내장) + `swk-doc.js` | 본인 레포에 직접 복사 |
| 호스팅 | `httpshare.service` (Tailscale, no-cache) | `python3 -m http.server` / nginx / caddy |
| 공유 URL | `http://<hostname>:8000` (Tailnet) | `http://127.0.0.1:8000` 또는 본인 도메인 |
| 캐시 무효화 | 서버 단 `Cache-Control: no-cache` | 없으면 자산에 `?v=<mtime>` 쿼리 |

## 참조

- 디자인 자산 SoT: `~/workspace/swk-infra/docs/_assets/swk-doc.css` (v6 표준 — 팔레트·컴포넌트 병합 내장) + `swk-doc.js`
- 팔레트 SoT(베이지+녹색, OKLCH·WCAG·레퍼런스): `~/workspace/swk-infra/docs/_assets/DESIGN-SYSTEM-v6-palette.md`
- markwand 토큰 원본: `/etc/nginx/markwand-tokens.css`
- 실제 사용 예: `josh-dev:8000/design-system-v5.html` (디자인 시스템 페이지) · `doc-catalog.html` (인덱스 IA — 사이드바·검색·필터·repo태그, repo 원본 `docs/doc-publish-catalog.html`) · `modern-infra-essays.html` (탭 + TOC)
- HTML SoT 룰 (CLAUDE.md §8): `~/workspace/swk-infra/CLAUDE.md`
- HTTP 노출 셋업: `~/workspace/swk-infra/docs/machines/swk-dev.md` §3.1.1
