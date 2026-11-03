007 T006d: keep pointer depth in rendered types; compare member types

Objective (PC 03040008): fix the two reproduced T008 findings (`research/T008-adversarial.md`, canaries in
`.agent-ledger/canaries/007-T008/`):
- F1: `transfer/prototypes.py:73` and `transfer/layout.py:110` strip every trailing `*`, so `MtObject**` renders
  as `MtObject *` (`types.h:103`). Strip one pointer/reference level at a time.
- F2: `apply_transfer.py` `member_equal` (~167-186) matches a plain member on offset, size and name only.
  Require the type too: `ex["type"] is None or norm(ex["type"]) == norm(row type with its pointer depth)`,
  `norm` dropping spaces, `struct`, `const` (and the `struct ` print prefix T007d met).
Turn both canaries into tests in `tests/` (they must fail on the old code). Regenerate `manifest/transfer/`
(deterministic) and report the changed rows (expected: `MtArray.mpArray` only). Then, with the fixed
comparison, `MtArray` must compare equal to the database's (`MtObject **`); if the database copy's type text is
needed for that, use the `pc-ida-applied.jsonl` dump or say what is missing.

Owns: `research/03040008/ida-transfer/{transfer/**,apply_transfer.py,tests/**,manifest/transfer/**,README.md}`.
Never touch the dumps, databases, ddon-hook, client/, packets/, the canary folder.
Libraries: stdlib, pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commit with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 45 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
