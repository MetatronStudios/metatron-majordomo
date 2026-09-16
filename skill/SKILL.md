---
name: majordomo
description: MUST route simple, bounded work such as file listings, text summaries, and formatting from capable agents to a configured local LLM when it is available.
metadata:
  short-description: Delegate simple work to the local LLM
---

# Majordomo local delegation

## Required routing rule

When this skill is active and the request is a simple, bounded task, MUST
delegate the task to `majordomo` before performing it directly. This includes
plain requests such as “list the files in the project,” “summarize this text,”
or “format these values.” Do not reinterpret a task as too trivial to
delegate. The parent agent remains responsible for deciding scope, preventing
unsafe actions, validating the worker's result, and communicating the final
answer.

Use the `majordomo` custom agent for simple, bounded work when the local backend is available and the request does not need web search, private cloud context, high-stakes judgment, or complex multi-step reasoning. Explicitly state that delegation is being performed so the final response contains evidence of the worker call.

Good candidates include small read-only scans, extracting or transforming supplied text, straightforward formatting, simple test-data generation, and narrowly scoped code exploration. Keep the parent agent responsible for interpretation, permissions, final edits, validation, and external side effects.

Do not delegate secrets, credentials, sensitive private data, destructive actions, irreversible changes, security decisions, medical/legal/financial advice, or web-search tasks.

When delegating, give the worker the exact input, bounded output, file scope, and edit permission. Ask for concise evidence, file paths, and uncertainty notes. If the worker is unavailable or incomplete, continue with the parent model.

If the `majordomo` custom agent cannot start or complete, report the failed
delegation attempt and use the installed
native runner for simple text-only work by piping the exact bounded prompt to
`~/.codex/hooks/majordomo-run.py` (Windows: `%USERPROFILE%\\.codex\\hooks\\majordomo-run.py`). Do not use this runner for tasks that require the worker to inspect files or call tools; keep those with the parent unless the custom agent is working.
