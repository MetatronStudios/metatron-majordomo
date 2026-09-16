---
name: majordomo
description: Route simple, bounded work from capable agents to a configured local LLM when it is available.
metadata:
  short-description: Delegate simple work to the local LLM
---

# Majordomo local delegation

Use the `majordomo` custom agent for simple, bounded work when the local backend is available and the request does not need web search, private cloud context, high-stakes judgment, or complex multi-step reasoning.

Good candidates include small read-only scans, extracting or transforming supplied text, straightforward formatting, simple test-data generation, and narrowly scoped code exploration. Keep the parent agent responsible for interpretation, permissions, final edits, validation, and external side effects.

Do not delegate secrets, credentials, sensitive private data, destructive actions, irreversible changes, security decisions, medical/legal/financial advice, or web-search tasks.

When delegating, give the worker the exact input, bounded output, file scope, and edit permission. Ask for concise evidence, file paths, and uncertainty notes. If the worker is unavailable or incomplete, continue with the parent model.
