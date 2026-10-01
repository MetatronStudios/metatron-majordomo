---
name: majordomo
description: MUST route simple, bounded work such as file listings, text summaries, and formatting from capable agents to a configured local LLM when it is available.
metadata:
  short-description: Delegate simple work to the local LLM
---

# Majordomo local delegation

## Required routing rule

When this skill is active and the request is a simple, bounded task, MUST
delegate the task through the Majordomo runtime before performing it directly.
This includes
plain requests such as “list the files in the project,” “summarize this text,”
or “format these values.” Do not reinterpret a task as too trivial to
delegate. The parent agent remains responsible for deciding scope, preventing
unsafe actions, validating the worker's result, and communicating the final
answer.

For text-only work, use the native Ollama runner first. It accepts arbitrary
local tags such as `qwen3.5:9b` and `gemma3:4b` without asking the Codex
account to authorize those tags as Codex agent models. Explicitly state that
delegation is being performed so the final response contains evidence of the
worker call.

Use the `majordomo` custom agent only when the Codex runtime accepts the
configured local provider and the task needs the worker's own tool access.
If Codex reports that the local model is unsupported, do not retry the custom
agent; use the native runner for text-only work or keep file/tool execution in
the parent agent and delegate only the bounded input transformation.

Good candidates include small read-only scans, extracting or transforming supplied text, straightforward formatting, simple test-data generation, and narrowly scoped code exploration. Keep the parent agent responsible for interpretation, permissions, final edits, validation, and external side effects.

Do not delegate secrets, credentials, sensitive private data, destructive actions, irreversible changes, security decisions, medical/legal/financial advice, or web-search tasks.

When delegating, give the worker the exact input, bounded output, file scope, and edit permission. Ask for concise evidence, file paths, and uncertainty notes. If the worker is unavailable or incomplete, continue with the parent model.

## Delegation paths

Use the installed native runner first for supplied-text tasks and narrow
read-only inspection tasks. Pipe the exact bounded prompt to
`~/.codex/hooks/majordomo-run.py` (Windows:
`%USERPROFILE%\\.codex\\hooks\\majordomo-run.py`).

For a narrow read-only inspection such as listing one directory, the parent may
collect the minimum required evidence with a non-mutating command, include that
evidence verbatim in the native-runner prompt, and ask Majordomo to produce the
bounded result. The parent must validate the result against the captured
evidence and must say that evidence collection was performed by the parent.
Never pass secrets or sensitive file contents to the runner.

Use the `majordomo` custom agent when the worker itself must call tools or edit
files and the Codex runtime accepts the configured local provider. If the
custom agent cannot start or complete, report the failed attempt and keep tool
use or editing with the parent. Do not ask the native runner to call tools or
pretend that it inspected files directly.

## Recommended local profile

Install `qwen3.5:4b` as the fast default for short, bounded, non-sensitive
text work. The parent must validate its output. If `qwen3.5:9b` is installed,
retry once with it for an ambiguous task, weak Hebrew output, or a failed
validation. Do not delegate strict, machine-critical formatting to the local
model; produce or validate it with the parent instead.
