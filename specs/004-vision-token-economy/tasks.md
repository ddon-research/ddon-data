# 004 Image input and token economy for client automation

A research feature with no `spec.md`. Sam asked on 2026-10-17 for best practices on multi-modal
input in Claude Code and Claude Desktop, and on saving tokens: ddon-hook's automation captures
screenshots (possibly at high quality), and file-size optimization may or may not save tokens.

- [x] R1 `general-purpose` (9 min, 56 tool calls, 207k tokens) (web, local code, measurements). Brief `brief-R1.md`; output
      `research/claude-vision-tokens.md`.
- [x] S1 Coordinator: hand the recommendations to ddon-hook (011) and record them in
      `research/external-references.md`.

## Running

- (none). Open for Sam: the live `count_tokens` run (`uv run research/claude-vision/count_image_tokens.py <png>` with ANTHROPIC_API_KEY set).
