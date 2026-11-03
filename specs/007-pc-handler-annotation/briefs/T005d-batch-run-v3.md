007 T005d: repair undefined call targets on the work copy, re-extract both sides (batch runs, writes)

Objective (PC 03040008, PS4 02020005): run T005c's v3 scripts. Authorized writes: only the repairs
`repair_functions.py` applies, on the work copy `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/`
(state after T004f: sha256 `7189b4c6...1b2c65`; check it before writing, stop if it differs). Writes only by
headless batch (`idat -A -L<log> -S"<script> <args>" <.i64>`, see the README); never open the work copy in
ida-mcp.

1. PC repair v3: dry run -> `dumps/repair3-dryrun.jsonl`, then apply -> `dumps/repair3-apply.jsonl`.
   T005c's warning: `add_func` auto-analysis may create functions at the new body's callees, which the
   neighbour read-back reports as `failed` (`readback_neighbours`) although the function exists; count
   those separately and check 3 of them in the listing (do not edit the script).
   Summarize repaired / refused by check / failed, per root kind (table callback, call target) and per
   address range (`0x758000`-`0x77C000`, `0x888000`-`0x88E000`, other). Stop before apply if failures
   or refusals exceed 25% of the would-repair count, and report.
2. Re-extract PC (batch) -> `dumps/pc-ida.jsonl`: `table_ok`, missing roots, orphan refs, count of call
   sites with constant arguments, functions with a `codec` field (compare with T005b § 2.1: every listed
   PC codec VA has the width T005b gives).
3. PS4 extract v3 on a private copy (`bash research/ida/private-copy.sh ps4 t005d`, batch or ida-mcp
   read-only) -> `dumps/ps4-ida.jsonl`; same counts; codec check against T005b § 2.2.
4. After each write run: the log has no "unpacked"/"restore" prompt, the `.i64` changed, no unpacked
   files remain; sha256 after. Spot-check 6 repaired call targets (3 per range) by a read-only batch
   script in your scratchpad: bounds and `decompile` succeeds. Then `manifest.py` for `dumps/MANIFEST.tsv`.

Owns: those dumps, `dumps/logs/*`, `dumps/MANIFEST.tsv`, and the report
`specs/007-pc-handler-annotation/research/T005d-batch-v3.md`. Never touch the scripts, the original or
accepted databases, ddon-hook, client/, packets/. Delete your PS4 private copy at the end if no worker
holds it.
Libraries: idat batch, jq.
Done: the report (commands, counts, refusals with reasons, checks, sha256 before/after); final message with
the path and at most 15 lines. Stop: budget 75 min of work time.
Base: the head when you start.
