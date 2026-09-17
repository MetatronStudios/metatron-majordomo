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

Use the installed native runner for simple text-only work by piping the exact
bounded prompt to
`~/.codex/hooks/majordomo-run.py` (Windows: `%USERPROFILE%\\.codex\\hooks\\majordomo-run.py`). Do not use this runner for tasks that require the worker to inspect files or call tools; keep those with the parent unless the custom agent is working.
