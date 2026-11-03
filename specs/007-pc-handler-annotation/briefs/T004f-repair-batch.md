007 T004f: repair the handler function starts on the work copy by headless batch, re-extract PC

Objective (PC 03040008): rerun T004d with T004e's fixed `research/03040008/ida-transfer/repair_functions.py`,
this time as headless batch jobs, which save and pack the copy (decision in `tasks.md`: database writes
only by `idat -A -S<script>` batch runs; never open the work copy in ida-mcp, its writes or leftovers
are lost or block the next open). Authorized writes: only the repairs the script applies.

1. Fresh work copy: delete `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/` (the
   T004d copy, writes lost, not reusable), then `bash research/ida/private-copy.sh pc-accepted 007work`.
   Record its sha256.
2. Batch runs (IDA 9.5: `C:/Program Files/IDA Professional 9.5/idat.exe`; `MSYS_NO_PATHCONV=1`; one log per
   run with `-L`; see the README for the exact argument form):
   a. dry run -> `dumps/repair-dryrun.jsonl`; stop and report if it would repair fewer than 125 or
      refuse more than 6 of the 131;
   b. apply -> `dumps/repair-apply.jsonl`;
   c. read-back: re-extract PC -> `dumps/pc-ida.jsonl` (batch); check `table_ok`, `missing_root` count
      (= refusals + failures of b), orphan refs.
   After each write run: the log shows no "unpacked"/"restore" prompt, the `.i64` mtime changed, and no
   `.id0`/`.id1`/`.nam`/`.til` files remain beside it. Record sha256 after b.
3. Spot checks by a read-only batch script you write in your scratchpad (not in the repo): for 6 repaired
   callbacks (2 of each repair kind) start/end and that `ida_hexrays.decompile` succeeds; the 3 T004d
   failures now repaired or refused with a stated check.
4. Update `dumps/MANIFEST.tsv` with `manifest.py`.

Owns: `research/03040008/ida-transfer/dumps/{repair-dryrun.jsonl,repair-apply.jsonl,pc-ida.jsonl,MANIFEST.tsv}`,
the run logs under `dumps/logs/`, and `specs/007-pc-handler-annotation/research/T004f-repair-batch.md`
(commands, counts, refusals with reasons, checks, sha256 before/after). Never touch the scripts, the
original or accepted databases, ddon-hook, client/, packets/; never open the work copy in ida-mcp.
Libraries: idat batch, jq.
Done: the report; final message with the path and at most 15 lines. Stop: budget 60 min of work time.
Base: the head when you start.
