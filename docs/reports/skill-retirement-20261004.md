# 중복 스킬 공급을 닫고 사용자 소유 링크를 보존한다

<svg viewBox="0 0 660 112" role="img" aria-labelledby="change-title" style="width:100%;color:var(--swk-text)"><title id="change-title">옛 별도 절차에서 현재 작업과 보존 지식으로 전환</title><g fill="var(--swk-surface)" stroke="currentColor"><rect x="5" y="16" width="195" height="76" rx="8"/><rect x="232" y="16" width="195" height="76" rx="8"/><rect x="459" y="16" width="195" height="76" rx="8"/></g><g fill="currentColor" text-anchor="middle" font-size="17"><text x="102" y="58">옛 호출·강제 절차</text><text x="329" y="58">카탈로그 은퇴</text><text x="556" y="58">현재 경로·지식 보존</text><text x="216" y="58">→</text><text x="443" y="58">→</text></g></svg>

## 한눈에

nova-algorithm의 옛 역할·일반 절차 스킬 retire 5 skill supply and team-play; owned-link migration을 카탈로그에서 은퇴합니다. 유효 도구·기억·참고 자산은 보존하며 현행 공용 실행 경로를 사용합니다.

## 원래 기준

- request: 2026-10-04 사용자 승인 원문: “오케이 추천안으로 진행하고 디스크립션은 해당하는 일을할때 에이전트에게 바로 연상이 될수있는 것으로 간결하게해줘”, “모두다완료되면 머지 배선완료해 다른 데브박스까지”. 대화 원문 permalink는 없으며 해당 발췌를 적용했습니다.
- plan: [승인된 감사·Opus 최종 논의](https://github.com/TeamSPWK/swk-wiki/blob/main/docs/reports/skill-gardening-audit-20261004/index.md)의 프로젝트 은퇴 묶음을 적용했습니다.
- blueprint: 독립 청사진은 없으며 승인 보고서와 현행 README·AGENTS.md·실제 파일/소비자를 대조했습니다.
- mockup: 화면 변경이나 최초 화면 목업은 없습니다.

## 검증

bash -n; git diff --check; isolated installer removes five owned retired links/team-play; installs only claude-filter; uninstall preserves user-owned codex directory

배포와 데이터 처리 동작은 이 PR에서 실행하지 않았습니다. 되돌림은 이 PR revert입니다. 실행 기준을 완화하지 않았으며 옛 중복 역할·강제 자문 절차만 은퇴합니다.

## 변경과 확인할 곳

deep-dive-task·llm-review·codex·wiki-upload·pikes-filter의 SKILL.md와 team-play 명령을 은퇴합니다. reference·templates·llm_client·claude-filter는 보존합니다.

install.sh는 배포할 대상을 먼저 확인한 뒤 uninstall.sh의 소유 링크 회수 계약을 재사용합니다. 사라진 카탈로그의 기존 링크는 명시적으로 회수하며 새 공용 스킬·사용자 교체본은 손대지 않습니다.

격리 설치 검증: 옛 다섯 링크와 team-play 제거, claude-filter만 공급, 제거 대칭, 사용자 소유 codex 폴더/파일 보존. 유료 API 호출은 하지 않았습니다.

위험도: 낮음. 확인할 곳: install/uninstall의 exact-target 링크 소유. 되돌림: PR revert 후 installer 재실행.

## 태스크보드

없음. 기존 승인 보고서의 묶음을 수행합니다.
