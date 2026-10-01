#!/usr/bin/env python3
"""Verify the ChatGPT/Codex-to-Majordomo-to-Ollama delegation path."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


SENTINEL = "MAJORDOMO_CHAT_CALL_OK"


def default_home() -> Path:
    override = os.environ.get("METATRON_CODEX_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".codex"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", type=Path, help="Path to majordomo-run.py")
    parser.add_argument("--model", help="Ollama model tag to test")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    home = default_home()
    runner = args.runner or home / "hooks" / "majordomo-run.py"
    skill = home / "skills" / "majordomo" / "SKILL.md"
    config = home / "config.toml"
    missing = [str(path) for path in (runner, skill, config) if not path.is_file()]
    if missing:
        print("FAIL: missing installed files: " + ", ".join(missing))
        return 1

    runner_text = runner.read_text(encoding="utf-8")
    skill_text = skill.read_text(encoding="utf-8")
    config_text = config.read_text(encoding="utf-8")
    required_skill_text = (
        "MUST",
        "delegate the task through the Majordomo runtime",
        "native Ollama runner first",
        "minimum required evidence",
        "validate the result against the captured",
    )
    if any(value not in skill_text for value in required_skill_text):
        print("FAIL: Majordomo skill does not require delegation for bounded work")
        return 1
    if "base_url = \"http://127.0.0.1:11434/v1\"" not in config_text:
        print("FAIL: Ollama /v1 provider is missing from config.toml")
        return 1

    environment = os.environ.copy()
    if args.model:
        environment["METATRON_LOCAL_MODEL"] = args.model
    runner_default = re.search(r"^DEFAULT_MODEL = ['\"]([^'\"]+)['\"]$", runner_text, re.MULTILINE)
    model = environment.get("METATRON_LOCAL_MODEL", runner_default.group(1) if runner_default else "qwen3.5:4b")
    if not args.model:
        if not runner_default:
            print("FAIL: native runner default model is missing")
            return 1
    prompt = (
        "This is an integration test called by the parent ChatGPT/Codex agent. "
        "This is a bounded text-only task. Do not use tools or edit files. "
        f"Reply with exactly: {SENTINEL}"
    )
    try:
        result = subprocess.run(
            [sys.executable, str(runner)],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=args.timeout,
            check=False,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        print(f"FAIL: Ollama model {model} did not respond within {args.timeout}s")
        return 1

    output = result.stdout.strip()
    if result.returncode != 0 or output != SENTINEL:
        print(f"FAIL: model={model} exit={result.returncode} output={output!r}")
        if result.stderr:
            print(result.stderr.strip())
        return 1

    print(f"PASS: ChatGPT/Codex -> Majordomo -> Ollama ({model}) -> {SENTINEL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
