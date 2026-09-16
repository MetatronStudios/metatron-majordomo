# Metatron Majordomo

![Metatron Majordomo mascot](logo.png)

A small in-house worker for Codex.

A small, cross-platform Codex skill and custom agent for sending simple, bounded work to a local LLM. It is designed for Sol, Astra, and other capable parent agents that should keep complex reasoning and final validation while reducing cloud-model usage for routine work.

MIT-licensed by Metatron.

## What it installs

- `majordomo` skill for delegation rules and safety boundaries.
- `majordomo` custom Codex agent with a configurable model and provider.
- A session-start health hook that tells Codex whether the local backend is available.
- A native Ollama runner for simple text-only delegation when a Codex release cannot run custom local agents reliably.

The installer writes only under the current user's Codex directory. It does not replace the primary model or route every task locally.

## Requirements

- Codex with custom agents and hooks enabled.
- Python 3.9+.
- A local OpenAI-compatible backend. Ollama is the default and is configured through its `/v1` Responses endpoint; LM Studio and other Codex-supported providers can be selected.

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

For Ollama, install any model separately when desired. Use the exact tag shown by `ollama list`:

```sh
ollama pull qwen3.5:9b
```

The installer automatically creates a `metatron_local` provider for Ollama at
`http://127.0.0.1:11434/v1`. This supports model tags such as `qwen3.5:9b`,
`qwen3:4b`, `gemma3:4b`, and `qwen2.5-coder:7b` without using Codex's built-in
Ollama model-discovery route.

The installer is idempotent and preserves unrelated Codex configuration. Restart Codex after installation so it reloads the new skill, agent, and hook.

## Test a ChatGPT delegation

From the project root, run the read-only integration test:

```sh
python3 scripts/test-majordomo.py
```

Windows PowerShell:

```powershell
py -3 scripts\test-majordomo.py
```

It checks the installed Majordomo configuration and sends a sentinel request
through the native Ollama runner. A successful result begins with `PASS` and
proves the local model answered the delegated request. A copyable ChatGPT test
prompt is in `tests/chatgpt-delegation-test.md`.

## How delegation works

The skill gives the parent model a narrow policy: simple, bounded, low-risk
work must be delegated to `majordomo`; keep secrets, web research, high-stakes
judgment, destructive actions, and final validation with the parent. The skill
also requires the parent to state when delegation occurred so it is auditable.

The health hook is informational and fails open. If the backend is down or the selected model is missing, the parent continues normally.

If Codex's custom-agent runner is unavailable, a parent agent can send a bounded
text-only request to the installed native runner:

```sh
printf '%s' 'Classify these labels: alpha, beta, gamma.' | python3 ~/.codex/hooks/majordomo-run.py
```

On Windows PowerShell:

```powershell
'Classify these labels: alpha, beta, gamma.' | py -3 "$env:USERPROFILE\.codex\hooks\majordomo-run.py"
```

## Configuration

Environment variables and installer flags:

| Setting | Default | Meaning |
| --- | --- | --- |
| `METATRON_LOCAL_MODEL` | `qwen3.5:9b` | Model tag written to the worker |
| `METATRON_LOCAL_PROVIDER` | `ollama` | Codex provider id |
| `METATRON_LOCAL_BASE_URL` | Ollama `/v1` endpoint when provider is `ollama` | Optional custom provider URL |
| `METATRON_CODEX_HOME` | platform default | Override the Codex home directory |

For a custom provider URL, the installer adds a `metatron_local` provider entry and points the worker at it. The provider must expose the Codex-supported Responses API.

## Uninstall

Remove these installed paths from your Codex home:

- `skills/majordomo`
- `agents/majordomo.toml`
- `hooks/majordomo-status.py`
- `hooks/majordomo-run.py`

Then remove the marked `metatron-majordomo` hook block from `config.toml`. The installer never removes a model from your local backend.
