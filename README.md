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
| `/codex` | Skill | Codex CLI delegation standard — implementation handoff guide (gpt-5.3-codex) |

## Install

```bash
git clone https://github.com/TeamSPWK/nova-algorithm.git ~/.nova-algorithm
cd ~/.nova-algorithm
bash install.sh
```

Restart Claude Code after installation.

## API Keys

`/llm-review` and `/deep-dive-task` require external LLM API keys:

```bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
export GEMINI_API_KEY="your-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"
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
