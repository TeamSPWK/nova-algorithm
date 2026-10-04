# Nova Algorithm

이 저장소는 남아 있는 `claude-filter` 스킬과 과거 참고 자산을 보관합니다. 일반 계획·다중 모델 자문·코드 위임·위키 적재·단순화 리뷰는 회사 공용 `subagent`, `claude`, `codex`, `gemini`, `wiki-upload`, `pikes-filter`에서 진행합니다.

## 설치

```bash
git clone https://github.com/TeamSPWK/nova-algorithm.git ~/.nova-algorithm
cd ~/.nova-algorithm
bash install.sh
```

설치기는 `SKILL.md`가 있는 폴더만 배포합니다. 현재 공급원은 `claude-filter` 하나입니다. 재설치와 제거는 이 checkout을 가리키는 링크만 회수하며 사용자 소유 교체본은 보존합니다.

```bash
bash uninstall.sh
```

## 보존 자산

- `skills/deep-dive-task/{reference,templates}.md`: 과거 참고 템플릿. 별도 강제 절차가 아닙니다.
- `skills/llm-review/llm_client.py`: 기존 독립 API 클라이언트. CLI `--help`에서 옵션을 확인하며 스킬로 배포하지 않습니다.
- `skills/codex/AGENTS.template.md`: 과거 대상 레포 템플릿. 현행 에이전트 규율을 덮어쓰지 않습니다.
- [team-play 역사 기록](docs/history/team-play.md): 옛 역할·검수 의식의 이력.
- `skills/doc-publish/README.md`: 이미 스킬 파일이 없는 옛 문서 발행 안내. 삭제 스킬 수에 포함하지 않습니다.

2026-10-04 `deep-dive-task`, `llm-review`, `codex`, `wiki-upload`, `pikes-filter`, `team-play` 공급을 은퇴했습니다.
