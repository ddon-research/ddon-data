# External references

The outside repositories and documents the research here relies on, so that no one repeats a
survey or a clone. Modelled on the reconstructor's `docs/reference/external-resources.md` and its
`specs/prior-art-*` reports.

- **Clones** live in `D:/GitHub/<owner>/<repo>` (`git clone --depth 1 --filter=blob:none`; refresh
  with `git pull --ff-only`). They are read-only reference: never build them or run their code.
- **Manifest**: `research/external-references.jsonl`, one JSON object per clone or document:
  `{"name", "url", "path", "commit", "fetched", "topics": [...], "report"}`. `commit` is the SHA the
  report read; `report` is the repo-relative file that holds the findings. Add a row when you clone,
  update `commit` and `fetched` when you refresh, and re-check the report's claims against the new
  commit before relying on them.
- **Before researching** a library, tool or technique, look it up here and in the reports listed
  below. Extend an existing report rather than starting a new one.

## Reports

| Topic | Report | Spec |
| --- | --- | --- |
| PC client protections, hooking libraries, anti-anti-debug tools, crash triage | `research/03040008/protections/` | `specs/003-client-protections/` |
| Claude vision: image token accounting, Claude Code image handling, cheaper capture for automation | `research/claude-vision-tokens.md`, script `research/claude-vision/count_image_tokens.py` | `specs/004-vision-token-economy/` |
