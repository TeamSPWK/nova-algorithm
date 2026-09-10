# Nova Algorithm

Claude Code skills for multi-agent orchestration, multi-LLM consultation, and quality auditing.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| `/team-play` | Command | Multi-agent orchestrated task execution with verification gates |
| `/deep-dive-task` | Skill | Multi-AI consultation for structured TASK document creation |
| `/llm-review` | Skill | Multi-LLM consultation wrapper (Gemini + GPT) |
| `/pikes-filter` | Skill | Rob Pike 5 principles — code complexity & over-engineering audit |
| `/claude-filter` | Skill | Production agent design principles — prompt/CLAUDE.md/skill audit |
| `/codex` | Skill | Codex CLI delegation standard — implementation handoff guide |
| `/wiki-upload` | Skill | **Internal (SPACEWALK)** — 사람이 손에 든 자료를 swk-wiki `swk-wiki-vault/10_Raw/ingest` 에 메타 추론으로 투입(append-only). `~/workspace/swk-wiki` 절대경로 의존. |

## Install

```bash
git clone https://github.com/TeamSPWK/nova-algorithm.git ~/.nova-algorithm
cd ~/.nova-algorithm
bash install.sh
```

Restart Claude Code after installation.

## API Keys

`/llm-review` and `/deep-dive-task` require external LLM API keys. The bundled
client is installed with the skills and can also be run from this checkout:

```bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
export GEMINI_API_KEY="your-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

From this checkout:

```bash
python3 skills/llm-review/llm_client.py --check-keys
```

## Uninstall

```bash
cd ~/.nova-algorithm
bash uninstall.sh
```

## Update

```bash
cd ~/.nova-algorithm
git pull
```

Symlinks update automatically - no reinstall needed.
