#!/usr/bin/env python3
"""Run a bounded Majordomo request directly through Ollama's Responses API."""
from __future__ import annotations

import json
import os
import sys
import urllib.request


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
    request = urllib.request.Request(
        base_url.rstrip("/") + "/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    except Exception as exc:
        print(f"Majordomo Ollama request failed: {exc}", file=sys.stderr)
        return 1

    for item in result.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                sys.stdout.write(content.get("text", ""))
                return 0
    print("Majordomo Ollama returned no text output.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
