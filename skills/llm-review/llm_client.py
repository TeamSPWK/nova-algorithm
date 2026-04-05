#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-LLM Client for External AI Consultation

Provides a unified interface for calling Gemini and OpenAI APIs with
hardcoded model names to prevent agent modifications.

Usage:
    python llm_client.py --provider gemini --phase consultation --prompt "..."
    python llm_client.py --provider openai --phase review --prompt-file task.md

Author: BluePrintCheck Team
Version: 2.1.0 (symmetric instructions, retry, reasoning effort)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

# =============================================================================
# HARDCODED MODEL CONFIGURATION - DO NOT MODIFY
# =============================================================================

MODELS = {
    "gemini": {
        "consultation": "gemini-3-flash-preview",     # Fast, cost-effective
        "review": "gemini-3.1-pro-preview",           # High quality, thorough
        "regulation": "gemini-3.1-pro-preview",       # 법규/규제 검토 (Gemini)
    },
    "openai": {
        "consultation": "gpt-5.4",                     # Fast consultation
        "review": "gpt-5.4",                           # High reasoning effort
        "regulation": "gpt-5.4",                       # 법규/규제 검토: thinking + web search
    },
}

TIMEOUTS = {
    "consultation": 420,  # 7 minutes
    "review": 900,        # 15 minutes
    "regulation": 1200,   # 20 minutes (reasoning=high + web_search)
}

MAX_TOKENS = {
    "consultation": 16384,
    "review": 65536,
    "regulation": 65536,
}

REASONING_EFFORT = {
    "review": "medium",
    "regulation": "high",
}

SYSTEM_INSTRUCTION = (
    "Analyze the provided context carefully. "
    "Be specific and actionable. "
    "Respond in the same language as the user's prompt."
)

MAX_RETRIES = 4
RETRY_DELAYS = [5, 15, 30, 60]
RETRYABLE_ERRORS = {"TimeoutError", "URLError"}
RETRYABLE_STATUS_CODES = {429, 502, 503}

# =============================================================================
# Environment Setup
# =============================================================================

def load_env():
    """Load .env file by walking up from cwd to find the nearest one."""
    # 1. cwd에서 위로 올라가며 .env 탐색
    current = Path.cwd()
    while current != current.parent:
        env_path = current / ".env"
        if env_path.exists():
            _parse_env_file(env_path)
            return True
        current = current.parent

    # 2. 홈 디렉토리 .env 폴백
    home_env = Path.home() / ".env"
    if home_env.exists():
        _parse_env_file(home_env)
        return True

    return False


def _parse_env_file(env_path: Path):
    """Parse a .env file and set environment variables."""
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def check_api_keys() -> Dict[str, bool]:
    """Check which API keys are available."""
    return {
        "gemini": bool(os.environ.get("GEMINI_API_KEY")),
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
    }


# =============================================================================
# Gemini Client
# =============================================================================

class GeminiClient:
    """Google Gemini API client."""

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 16384,
        temperature: float = 0.7,
        timeout: int = 180,
    ) -> Dict[str, Any]:
        """Generate response from Gemini API."""
        import urllib.request
        import urllib.error

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

        payload = {
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                elapsed = time.time() - start_time

                # Extract response text
                text = ""
                tokens = {"prompt": 0, "completion": 0, "total": 0}

                if "candidates" in result and result["candidates"]:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        text = "".join(p.get("text", "") for p in parts)

                if "usageMetadata" in result:
                    usage = result["usageMetadata"]
                    tokens = {
                        "prompt": usage.get("promptTokenCount", 0),
                        "completion": usage.get("candidatesTokenCount", 0),
                        "total": usage.get("totalTokenCount", 0),
                    }

                return {
                    "success": True,
                    "response": text,
                    "tokens": tokens,
                    "elapsed_seconds": round(elapsed, 2),
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", str(e))
            except json.JSONDecodeError:
                error_msg = error_body or str(e)

            return {
                "success": False,
                "error": error_msg,
                "error_type": "HTTPError",
                "status_code": e.code,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": str(e.reason),
                "error_type": "URLError",
            }
        except TimeoutError:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "error_type": "TimeoutError",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }


# =============================================================================
# OpenAI Client
# =============================================================================

class OpenAIClient:
    """OpenAI API client."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 16384,
        temperature: float = 0.7,
        timeout: int = 180,
        high_effort: bool = False,
        web_search: bool = False,
        reasoning_effort: str = "medium",
    ) -> Dict[str, Any]:
        """Generate response from OpenAI API."""
        import urllib.request
        import urllib.error

        # review/regulation → Responses API (reasoning 지원)
        if high_effort:
            return self._generate_with_responses_api(
                prompt=prompt, model=model, max_tokens=max_tokens,
                timeout=timeout, web_search=web_search,
                reasoning_effort=reasoning_effort,
            )

        # consultation phase → Chat Completions API
        url = "https://api.openai.com/v1/chat/completions"

        system_content = SYSTEM_INSTRUCTION

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_completion_tokens": max_tokens,
            "temperature": temperature,
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                elapsed = time.time() - start_time

                # Extract response text
                text = ""
                tokens = {"prompt": 0, "completion": 0, "total": 0}

                if "choices" in result and result["choices"]:
                    choice = result["choices"][0]
                    if "message" in choice:
                        text = choice["message"].get("content", "")

                if "usage" in result:
                    usage = result["usage"]
                    tokens = {
                        "prompt": usage.get("prompt_tokens", 0),
                        "completion": usage.get("completion_tokens", 0),
                        "total": usage.get("total_tokens", 0),
                    }

                return {
                    "success": True,
                    "response": text,
                    "tokens": tokens,
                    "elapsed_seconds": round(elapsed, 2),
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", str(e))
            except json.JSONDecodeError:
                error_msg = error_body or str(e)

            return {
                "success": False,
                "error": error_msg,
                "error_type": "HTTPError",
                "status_code": e.code,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": str(e.reason),
                "error_type": "URLError",
            }
        except TimeoutError:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "error_type": "TimeoutError",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _generate_with_responses_api(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 16384,
        timeout: int = 900,
        web_search: bool = False,
        reasoning_effort: str = "medium",
    ) -> Dict[str, Any]:
        """Responses API로 reasoning + (선택) web search 호출."""
        import urllib.request
        import urllib.error

        url = "https://api.openai.com/v1/responses"

        payload = {
            "model": model,
            "input": prompt,
            "instructions": SYSTEM_INSTRUCTION,
            "reasoning": {"effort": reasoning_effort},
            "temperature": 1,
            "max_output_tokens": max_tokens,
        }

        if web_search:
            payload["tools"] = [{"type": "web_search"}]

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
                elapsed = time.time() - start_time

                # Responses API: output 배열에서 message type 추출
                text = ""
                for item in result.get("output", []):
                    if item.get("type") == "message":
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                text += content.get("text", "")

                tokens = {"prompt": 0, "completion": 0, "total": 0}
                if "usage" in result:
                    usage = result["usage"]
                    tokens = {
                        "prompt": usage.get("input_tokens", 0),
                        "completion": usage.get("output_tokens", 0),
                        "total": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                    }

                return {
                    "success": True,
                    "response": text,
                    "tokens": tokens,
                    "elapsed_seconds": round(elapsed, 2),
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", str(e))
            except json.JSONDecodeError:
                error_msg = error_body or str(e)
            return {
                "success": False,
                "error": error_msg,
                "error_type": "HTTPError",
                "status_code": e.code,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": str(e.reason),
                "error_type": "URLError",
            }
        except TimeoutError:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "error_type": "TimeoutError",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }


# =============================================================================
# Main Interface
# =============================================================================

def _read_include_files(file_specs: list, max_lines: int = 0) -> str:
    """
    Read files and format them for inclusion in the prompt.

    Supports:
      - "path/to/file.py"           → entire file
      - "path/to/file.py:100-200"   → lines 100 to 200
      - "path/to/file.py:100"       → from line 100 to end

    Args:
        file_specs: List of file paths, optionally with :start-end line ranges
        max_lines: Max lines per file (0 = unlimited)

    Returns:
        Formatted string with all file contents
    """
    sections = []
    total_lines = 0

    for spec in file_specs:
        # Parse "file:start-end" or "file:start" or just "file"
        line_start, line_end = None, None
        if ":" in spec:
            parts = spec.rsplit(":", 1)
            # Check if the part after : looks like a line range (not a Windows drive letter)
            range_part = parts[1]
            if range_part.replace("-", "").isdigit():
                spec = parts[0]
                if "-" in range_part:
                    line_start, line_end = map(int, range_part.split("-", 1))
                else:
                    line_start = int(range_part)

        path = Path(spec)
        if not path.exists():
            sections.append(f"## {spec}\n\n[FILE NOT FOUND: {spec}]\n")
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            sections.append(f"## {spec}\n\n[READ ERROR: {e}]\n")
            continue

        # Apply line range
        if line_start is not None:
            start_idx = max(0, line_start - 1)  # 1-based to 0-based
            end_idx = line_end if line_end else len(lines)
            lines = lines[start_idx:end_idx]
            range_info = f" (lines {line_start}-{line_end or 'end'})"
        else:
            range_info = ""

        # Apply max_lines
        truncated = False
        if max_lines > 0 and len(lines) > max_lines:
            lines = lines[:max_lines]
            truncated = True

        content = "".join(lines)
        line_count = len(lines)
        total_lines += line_count

        header = f"## {spec}{range_info}"
        if truncated:
            header += f" [TRUNCATED to {max_lines} lines]"

        # Detect language from extension for code block
        ext = path.suffix.lstrip(".")
        lang_map = {"py": "python", "js": "javascript", "ts": "typescript",
                     "rs": "rust", "rb": "ruby", "go": "go", "java": "java",
                     "sh": "bash", "yml": "yaml", "yaml": "yaml", "json": "json",
                     "toml": "toml", "md": "markdown", "sql": "sql"}
        lang = lang_map.get(ext, ext or "")

        sections.append(f"{header}\n\n```{lang}\n{content}\n```\n")

    if not sections:
        return ""

    result = "\n".join(sections)
    result += f"\n---\nTotal: {len(sections)} files, {total_lines} lines\n"
    return result


def call_llm(
    provider: str,
    phase: str,
    prompt: str,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Call LLM with specified provider and phase.

    Args:
        provider: "gemini" or "openai"
        phase: "consultation", "review", or "regulation"
        prompt: The prompt to send
        verbose: Print debug info

    Returns:
        Dict with response or error
    """
    # Validate inputs
    if provider not in MODELS:
        return {
            "success": False,
            "error": f"Invalid provider: {provider}. Use 'gemini' or 'openai'",
            "error_type": "ValidationError",
        }

    if phase not in MODELS[provider]:
        return {
            "success": False,
            "error": f"Invalid phase: {phase}. Use 'consultation', 'review', or 'regulation'",
            "error_type": "ValidationError",
        }

    # Get hardcoded model and timeout (not overridable)
    model = MODELS[provider][phase]
    max_tokens = MAX_TOKENS[phase]
    timeout = TIMEOUTS[phase]

    if verbose:
        print(f"[DEBUG] Provider: {provider}", file=sys.stderr)
        print(f"[DEBUG] Phase: {phase}", file=sys.stderr)
        print(f"[DEBUG] Model: {model}", file=sys.stderr)
        print(f"[DEBUG] Max tokens: {max_tokens}", file=sys.stderr)
        print(f"[DEBUG] Timeout: {timeout}s", file=sys.stderr)
        print(f"[DEBUG] Prompt length: {len(prompt)} chars", file=sys.stderr)
        print(f"[DEBUG] Prompt preview: {prompt[:200]!r}", file=sys.stderr)

    # Determine reasoning effort for OpenAI Responses API
    reasoning_effort = REASONING_EFFORT.get(phase)

    # Create client and call API with retry
    def _do_call():
        try:
            if provider == "gemini":
                client = GeminiClient()
                return client.generate(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
            else:  # openai
                client = OpenAIClient()
                return client.generate(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    high_effort=(phase in ("review", "regulation")),
                    web_search=(phase == "regulation"),
                    reasoning_effort=reasoning_effort or "medium",
                )
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "ConfigurationError",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    result = None
    for attempt in range(MAX_RETRIES):
        result = _do_call()
        if result["success"]:
            break
        is_retryable = (
            result.get("error_type") in RETRYABLE_ERRORS
            or result.get("status_code", 0) in RETRYABLE_STATUS_CODES
        )
        if is_retryable and attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAYS[attempt]
            if verbose:
                print(
                    f"[RETRY] attempt {attempt + 2}/{MAX_RETRIES} "
                    f"after {delay}s ({result.get('error_type')})",
                    file=sys.stderr,
                )
            time.sleep(delay)
            continue
        break

    # Add metadata
    result["provider"] = provider
    result["model"] = model
    result["phase"] = phase
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    if reasoning_effort:
        result["reasoning_effort"] = reasoning_effort

    return result


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Multi-LLM Client for External AI Consultation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Gemini consultation
  python llm_client.py --provider gemini --phase consultation --prompt "Analyze..."

  # OpenAI review from file
  python llm_client.py --provider openai --phase review --prompt-file task.md

  # Check API keys
  python llm_client.py --check-keys

  # List models
  python llm_client.py --list-models
""")

    parser.add_argument(
        "--provider",
        choices=["gemini", "openai"],
        help="LLM provider to use"
    )
    parser.add_argument(
        "--phase",
        choices=["consultation", "review", "regulation"],
        help="Phase determines model selection (regulation = thinking + web search)"
    )
    parser.add_argument(
        "--prompt",
        help="Prompt text to send"
    )
    parser.add_argument(
        "--prompt-file",
        help="Read prompt from file"
    )
    parser.add_argument(
        "--output",
        help="Write response to file (default: stdout)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print debug info"
    )
    parser.add_argument(
        "--include-files",
        nargs="+",
        metavar="FILE",
        help="Append file contents to prompt (supports file:start-end line ranges)"
    )
    parser.add_argument(
        "--max-file-lines",
        type=int,
        default=0,
        help="Max lines per included file (0 = unlimited)"
    )
    parser.add_argument(
        "--check-keys",
        action="store_true",
        help="Check API key availability"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List hardcoded models"
    )

    args = parser.parse_args()

    # Load environment
    load_env()

    # Handle utility commands
    if args.check_keys:
        keys = check_api_keys()
        result = {
            "gemini": "available" if keys["gemini"] else "not set",
            "openai": "available" if keys["openai"] else "not set",
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if any(keys.values()) else 1)

    if args.list_models:
        print(json.dumps(MODELS, indent=2))
        sys.exit(0)

    # Validate required args for LLM call
    if not args.provider:
        parser.error("--provider is required")
    if not args.phase:
        parser.error("--phase is required")
    if not args.prompt and not args.prompt_file:
        parser.error("--prompt or --prompt-file is required")

    # Get prompt
    if args.prompt_file:
        try:
            with open(args.prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            result = {
                "success": False,
                "error": f"Failed to read prompt file: {e}",
                "error_type": "FileError",
            }
            print(json.dumps(result, indent=2))
            sys.exit(1)
    else:
        prompt = args.prompt

    # Warn if review/regulation without --include-files
    if args.phase in ("review", "regulation") and not args.include_files:
        print(
            "[WARN] review/regulation phase without --include-files. "
            "The LLM will only see the prompt text, not any source code.",
            file=sys.stderr,
        )

    # Append included files to prompt
    if args.include_files:
        file_sections = _read_include_files(args.include_files, args.max_file_lines)
        if file_sections:
            prompt = prompt.rstrip() + "\n\n" + "=" * 60 + "\n"
            prompt += "# ATTACHED SOURCE CODE\n"
            prompt += "=" * 60 + "\n\n"
            prompt += file_sections

    # Call LLM
    result = call_llm(
        provider=args.provider,
        phase=args.phase,
        prompt=prompt,
        verbose=args.verbose,
    )

    # Output
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            if args.verbose:
                print(f"[DEBUG] Response written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to write output: {e}", file=sys.stderr)
            print(output_json)
            sys.exit(1)
    else:
        print(output_json)

    # Exit code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
