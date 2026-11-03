007 T009b: turn the settled conflicts into correction rows; apply supports them

Objective (PC 03040008): T009 (`research/T009-conflicts.md`, `T009-decisions.tsv`) decided all 61 conflict rows
`ours`: 7 names (5 earlier names copy the PC group prefix into a PS4-style name, `0x833670` has no class,
`0x7DA410` uses the PS4 form where the PC string differs) and 54 prototypes (50 handlers differ only in argument
names, `0x8320B0`/`0x87B140` have a wrong `__fastcall`, `0x7D3880`/`0x833670` are less specific).

1. `transfer/`: read `specs/007-pc-handler-annotation/research/T009-decisions.tsv` (path as an input with its
   sha256 in the output header); a conflict row whose decision is `ours` becomes status `correct` (names) /
   `replace` (prototypes) with the decision's reason and evidence VAs; `theirs` -> `keep` (not written);
   `merge` -> the decision's final value; `undecided` -> stays `conflict`. A decision for a row that is not a
   conflict, or whose recorded current value differs from the row's, is an error.
2. `apply_transfer.py`: `correct`/`replace` rows overwrite the current name/prototype only if the database's
   current value equals the value the row records (else `refused current-changed`), with the before-state in
   the undo record as for every write. Verify treats them like `set` rows.
3. Regenerate `manifest/transfer/` (deterministic; report the changed rows: 61 expected).
Tests: an `ours` name correction, an `ours` prototype replace, a stale current value refused, a decision for a
non-conflict row is an error, `theirs` not written.

Owns: `research/03040008/ida-transfer/{transfer/**,transfer.py,apply_transfer.py,tests/**,manifest/transfer/**,README.md}`.
Never touch the decisions TSV, dumps, databases, ddon-hook, client/, packets/.
Libraries: stdlib, pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commit with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 45 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
