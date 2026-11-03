007 T007b: apply the wave-1 transfer to the work copy and verify it (batch runs, writes)

Objective (PC 03040008): run T007's `research/03040008/ida-transfer/apply_transfer.py` (README) on the work
copy `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`.
Authorized writes: only the rows `apply_transfer.py --apply` writes from `manifest/transfer/`. Headless
batch only (`idat -A -L<log> -S"<script> <args>"`); never open the work copy in ida-mcp.

1. Check the copy's sha256 is `65120b34...8b9111`; then copy the `.i64` to
   `ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64` (the rollback point; `cp`, then compare
   sha256).
2. Dry run -> `dumps/apply-dryrun.jsonl`: actions per kind (types, labels, names, prototypes, comments) and
   refusals with reasons; the copy's sha256 must be unchanged. Stop and report if refusals exceed 10% of a
   kind or anything fails parsing.
3. Apply -> `dumps/apply.jsonl`: written / already / refused / failed per kind; sha256 after. T007's IDA adapter
   runs here for the first time (udt build, `create_typedef`, tinfo serialize for undo): if any write
   `failed` or the read-backs disagree, restore the rollback copy (`cp` the before-T007b `.i64` back, compare
   sha256), stop and report the failing calls with their errors; do not edit the script.
4. Second apply -> `dumps/apply-2.jsonl`: everything `already`, nothing written (idempotence).
5. Verify (`--verify --apply-log dumps/apply.jsonl`; modes do not combine, see the README) -> `dumps/apply-verify.jsonl`: rows equal the database; counts before/after (only the rows
   changed); decompile results for every function with a new prototype (failures listed with va and error).
6. Re-extract PC (batch) -> `dumps/pc-ida-applied.jsonl` and compare with `dumps/pc-ida.jsonl`: changed
   names/prototypes are exactly the written rows (count both ways).
7. Spot checks (read-only batch script in your scratchpad, decompiled text in the report): 3 handlers,
   2 readers, 2 element readers, 2 senders, 1 requester: name, prototype, comment, and that the pseudocode
   reads sensibly (arguments named, the struct type on `this` where transferred).
After each write run: no "unpacked"/"restore" prompt in the log, no unpacked files left.

Owns: those dumps and logs, `dumps/MANIFEST.tsv` (`manifest.py`), the rollback copy, and the report
`specs/007-pc-handler-annotation/research/T007b-apply-run.md` (commands, counts, refusals, failures, sha256
at each step, spot-check pseudocode). Never touch scripts, the manifest, the original or accepted
databases, ddon-hook, client/, packets/.
Libraries: idat batch, jq. Done: the report; final message with the path and at most 15 lines.
Stop: budget 90 min of work time. Base: the head when you start.
