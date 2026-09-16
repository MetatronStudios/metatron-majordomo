# ChatGPT delegation test

Use this prompt in a ChatGPT/Codex session where the Majordomo skill is installed:

> Use Majordomo for this safe integration test. Run the repository's
> `scripts/test-majordomo.py`. Do not edit files. Report whether the result is
> `PASS` and include the local model tag.

Expected evidence:

```text
PASS: ChatGPT/Codex -> Majordomo -> Ollama (<model>) -> MAJORDOMO_CHAT_CALL_OK
```

The test only sends a sentinel text request to the configured local Ollama
model. It does not create, modify, delete, move, or rename project files.
