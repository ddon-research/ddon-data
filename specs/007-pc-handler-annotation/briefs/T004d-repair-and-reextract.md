007 T004d: make the work copy, repair the handler function starts, re-extract PC (evidence run, writes)

Objective (PC 03040008): run T004c's `research/03040008/ida-transfer/repair_functions.py` on the spec's
persistent work copy, then re-run the PC extractor. Authorized writes: only the function repairs the
script applies (Sam, 2026-11-03: annotate the PC database; writes go to a copy, never the original or
the accepted database).

1. Work copy: `bash research/ida/private-copy.sh pc-accepted 007work` (this copy persists for the whole
   spec; if `ddon-data-007work` already exists, stop and report). Open it with ida-mcp. Record its
   sha256 before any write in the report.
2. Dry run: `exec(open(".../repair_functions.py").read(), {"OUT": ".../dumps/repair-dryrun.jsonl", "APPLY": False})`.
   Summarize: would-repair / refused by check / already-ok. If any refusal looks like a script defect
   (a clean prologue refused), report it with the va and the listing; do not edit the script.
3. Apply: the same with `APPLY: True` and `OUT` `dumps/repair-apply.jsonl` (the undo log is part of it).
   Spot-check 5 repaired functions in the listing (start, end, the decompiler renders without error).
4. Re-extract: `exec(open(".../extract_ida.py").read(), {"OUT": ".../dumps/pc-ida.jsonl", "SIDE": "pc"})`;
   check `table_ok`, the `missing_root` count (expected: only the refusals), the `onpacket_orphan_refs`
   count. Update `dumps/MANIFEST.tsv` with `manifest.py`.
5. Persistence: the worker saves after each `execute_python`. Before you end, note the work copy's
   `.i64` size, mtime and whether unpacked `.id0`/`.id1`/`.nam`/`.til` files are beside it.

Owns: `research/03040008/ida-transfer/dumps/{repair-dryrun.jsonl,repair-apply.jsonl,pc-ida.jsonl,MANIFEST.tsv}`
and the report `specs/007-pc-handler-annotation/research/T004d-repair.md` (commands, counts, refusals
with reasons, spot checks, persistence state). Never touch the scripts, the original or accepted
databases, ddon-hook, client/, packets/.
Libraries: ida-mcp `execute_python`.
Done: the report; final message with the path and at most 15 lines. Stop: budget 60 min of work time;
stop before APPLY if the dry run would repair fewer than 100 or refuse more than 30.
Base: the head when you start.
