#!/usr/bin/env python3
"""Run a bounded Majordomo request directly through Ollama's Responses API."""
from __future__ import annotations

import json
import os
import sys
import urllib.request


def post_json(url: str, payload: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def response_text(result: dict) -> str:
    direct = result.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    for item in result.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content", [])
        if isinstance(content, str) and content.strip():
            return content.strip()
        for part in content:
            if not isinstance(part, dict) or part.get("type") not in {"output_text", "text"}:
                continue
            text = part.get("text", "")
            if isinstance(text, str) and text.strip():
                return text.strip()
    return ""


def chat_text(result: dict) -> str:
    for choice in result.get("choices", []):
        message = choice.get("message", {})
        content = message.get("content", "")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return ""


def main() -> int:
    prompt = sys.stdin.read()
    if not prompt.strip():
        print("Majordomo requires a prompt on stdin.", file=sys.stderr)
        return 2

    base_url = os.environ.get("METATRON_LOCAL_BASE_URL", "http://127.0.0.1:11434/v1")
    model = os.environ.get("METATRON_LOCAL_MODEL", "qwen3.5:9b")
    payload = {
        "model": model,
        "input": prompt,
        "max_output_tokens": int(os.environ.get("METATRON_LOCAL_MAX_OUTPUT_TOKENS", "2048")),
        "reasoning": {"effort": "none"},
    }
    try:
        result = post_json(base_url.rstrip("/") + "/responses", payload, timeout=120)
        text = response_text(result)
        if not text:
            # Some Ollama models expose a valid Responses envelope but leave
            # its message content empty. Chat Completions is the broader
            # compatibility path and is supported by the same local server.
            fallback = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": payload["max_output_tokens"],
                "stream": False,
            }
            text = chat_text(post_json(base_url.rstrip("/") + "/chat/completions", fallback, timeout=120))
        if text:
            sys.stdout.write(text)
            return 0
    except Exception as exc:
        print(f"Majordomo Ollama request failed: {exc}", file=sys.stderr)
        return 1

    print("Majordomo Ollama returned no text output.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
