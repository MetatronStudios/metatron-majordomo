#!/usr/bin/env python3
"""Emit Codex hook context describing the configured local backend."""
import json
import os
import sys
import urllib.request

base_url = os.environ.get("METATRON_LOCAL_BASE_URL", "http://127.0.0.1:11434")
model = os.environ.get("METATRON_LOCAL_MODEL", "qwen3.5:9b")
tags_url = base_url.rstrip("/") + "/api/tags"

try:
    with urllib.request.urlopen(tags_url, timeout=2) as response:
        payload = json.load(response)
    names = {item.get("name", "") for item in payload.get("models", [])}
    if not any(name == model or name.startswith(model + ":") for name in names):
        message = f"Local backend is reachable, but configured model {model} is not installed."
    else:
        message = f"Local LLM worker is available with {model}. Use local_worker only for simple, bounded work."
except Exception:
    message = f"Local LLM worker is configured, but the backend is not reachable at {base_url}."

json.dump({"additionalContext": message}, sys.stdout, separators=(",", ":"))
