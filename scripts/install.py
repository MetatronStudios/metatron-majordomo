#!/usr/bin/env python3
"""Install the Metatron local worker into the user's Codex home."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
from pathlib import Path

MARKER = "# BEGIN metatron-majordomo"
END_MARKER = "# END metatron-majordomo"
PROVIDER_MARKER = "# BEGIN metatron-majordomo-provider"
PROVIDER_END_MARKER = "# END metatron-majordomo-provider"


def codex_home() -> Path:
    override = os.environ.get("METATRON_CODEX_HOME")
    if override:
        return Path(override).expanduser()
    if platform.system() == "Windows":
        return Path(os.environ.get("USERPROFILE", "~")) / ".codex"
    return Path.home() / ".codex"


def replace_tokens(text: str, provider: str, model: str) -> str:
    return text.replace("{{MODEL_PROVIDER}}", provider).replace("{{MODEL}}", model)


def add_hook(config: Path, command: str, provider: str, base_url: str) -> None:
    existing = config.read_text(encoding="utf-8") if config.exists() else ""
    if MARKER in existing:
        existing = existing[: existing.index(MARKER)].rstrip() + "\n"
    block = f"""{MARKER}
[[hooks.SessionStart]]
matcher = \".*\"

[[hooks.SessionStart.hooks]]
type = \"command\"
command = '{command}'
timeout = 5
additionalContextLimit = 1000
{END_MARKER}
"""
    if base_url:
        if PROVIDER_MARKER in existing:
            existing = existing[: existing.index(PROVIDER_MARKER)].rstrip() + "\n"
        block += f"\n{PROVIDER_MARKER}\n[model_providers.metatron_local]\nname = \"Metatron Ollama backend\"\nbase_url = \"{base_url}\"\nwire_api = \"responses\"\n{PROVIDER_END_MARKER}\n"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(existing.rstrip() + "\n\n" + block, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("METATRON_LOCAL_MODEL", "qwen3.5:9b"))
    parser.add_argument("--provider", default=os.environ.get("METATRON_LOCAL_PROVIDER", "ollama"))
    parser.add_argument("--base-url", default=os.environ.get("METATRON_LOCAL_BASE_URL", ""))
    args = parser.parse_args()

    # Ollama exposes its Codex-compatible Responses API under /v1. Using a
    # named provider avoids Codex's built-in OSS model-discovery path, which
    # is not consistent across Codex and Ollama versions.
    base_url = args.base_url
    if args.provider == "ollama" and not base_url:
        base_url = "http://127.0.0.1:11434/v1"

    root = Path(__file__).resolve().parents[1]
    home = codex_home()
    legacy_skill = home / "skills" / "local-llm-delegation"
    legacy_agent = home / "agents" / "local-worker.toml"
    legacy_hook = home / "hooks" / "local-llm-status.ps1"
    if legacy_skill.is_dir() and (legacy_skill / "SKILL.md").exists():
        if "name: local-llm-delegation" in (legacy_skill / "SKILL.md").read_text(encoding="utf-8"):
            shutil.rmtree(legacy_skill)
    if legacy_agent.is_file() and 'name = "local_worker"' in legacy_agent.read_text(encoding="utf-8"):
        legacy_agent.unlink()
    if legacy_hook.is_file() and "Local LLM worker" in legacy_hook.read_text(encoding="utf-8"):
        legacy_hook.unlink()

    skill_dst = home / "skills" / "majordomo"
    agent_dst = home / "agents" / "majordomo.toml"
    hook_dst = home / "hooks" / "majordomo-status.py"
    runner_dst = home / "hooks" / "majordomo-run.py"

    if skill_dst.exists():
        shutil.rmtree(skill_dst)
    shutil.copytree(root / "skill", skill_dst)
    agent_dst.parent.mkdir(parents=True, exist_ok=True)
    provider = "metatron_local" if base_url else args.provider
    agent_dst.write_text(
    replace_tokens((root / "templates" / "majordomo.toml").read_text(encoding="utf-8"), provider, args.model),
        encoding="utf-8",
    )
    hook_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "scripts" / "majordomo-status.py", hook_dst)
    shutil.copy2(root / "scripts" / "majordomo-run.py", runner_dst)

    command = f'python3 "{hook_dst}"'
    if platform.system() == "Windows":
        command = f'py -3 "{hook_dst}"'
    config = home / "config.toml"
    add_hook(config, command, provider, base_url)
    print(f"Installed Majordomo using {args.model} ({provider}) into {home}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
