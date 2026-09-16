# Metatron Majordomo

![Metatron Majordomo](logo.png)

A small in-house worker for Codex.

A small, cross-platform Codex skill and custom agent for sending simple, bounded work to a local LLM. It is designed for Sol, Astra, and other capable parent agents that should keep complex reasoning and final validation while reducing cloud-model usage for routine work.

MIT-licensed by Metatron.

## What it installs

- `local-llm-delegation` skill for delegation rules and safety boundaries.
- `local_worker` custom Codex agent with a configurable model and provider.
- A session-start health hook that tells Codex whether the local backend is available.

The installer writes only under the current user's Codex directory. It does not replace the primary model or route every task locally.

## Requirements

- Codex with custom agents and hooks enabled.
- Python 3.9+.
- A local OpenAI-compatible backend. Ollama is the default; LM Studio and other Codex-supported providers can be selected.

## Install

Linux/macOS:

```sh
./scripts/install.sh --model qwen3.5:9b
```

Windows PowerShell:

```powershell
.\scripts\install.ps1 -Model qwen3.5:9b
```

To use another local model, rerun with its exact local tag, for example `--model llama3.2:3b` or `-Model mistral:7b`. The provider can be selected with `--provider` / `-Provider` (`ollama`, `lmstudio`, or a custom Codex provider id).

For Ollama, install the model separately when desired:

```sh
ollama pull qwen3.5:9b
```

The installer is idempotent and preserves unrelated Codex configuration. Restart Codex after installation so it reloads the new skill, agent, and hook.

## How delegation works

The skill gives the parent model a narrow policy: delegate only small, reversible, low-risk work; keep secrets, web research, high-stakes judgment, destructive actions, and final validation with the parent. The parent explicitly spawns `local_worker` when appropriate.

The health hook is informational and fails open. If the backend is down or the selected model is missing, the parent continues normally.

## Configuration

Environment variables and installer flags:

| Setting | Default | Meaning |
| --- | --- | --- |
| `METATRON_LOCAL_MODEL` | `qwen3.5:9b` | Model tag written to the worker |
| `METATRON_LOCAL_PROVIDER` | `ollama` | Codex provider id |
| `METATRON_LOCAL_BASE_URL` | empty | Optional custom provider URL |
| `METATRON_CODEX_HOME` | platform default | Override the Codex home directory |

For a custom provider URL, the installer adds a `metatron_local` provider entry and points the worker at it. The provider must expose the Codex-supported Responses API.

## Uninstall

Remove these installed paths from your Codex home:

- `skills/local-llm-delegation`
- `agents/local-worker.toml`
- `hooks/local-llm-status.py`

Then remove the marked `metatron-local-llm-delegation` hook block from `config.toml`. The installer never removes a model from your local backend.
