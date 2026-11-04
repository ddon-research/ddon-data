# Tools

This directory holds the repository's local gate and the hooks behind it, hand-written, for anyone who changes a file here or met a refusal. What each section and hook does is on [Gate and hooks](../docs/reference/gate-and-hooks.md); to run the gate, see [Run the gate](../docs/how-to/run-the-gate.md). The documentation map is [`docs/index.md`](../docs/index.md).

| Path | Holds |
| --- | --- |
| `check.sh` | the gate |
| `docs_check.py`, `test_docs_check.py` | the documentation check and its tests |
| `hooks/` | the Claude Code hooks and their tests, wired in `.claude/settings.json` and the role files |
| `orchestration/` | `progress.py`, `retro.py` and `section.py`, with their tests |
