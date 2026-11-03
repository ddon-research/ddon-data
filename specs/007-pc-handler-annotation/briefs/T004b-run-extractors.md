007 T004b: run the IDA fact extractor on both databases (evidence run)

Objective (PC 03040008, PS4 02020005): produce the matcher's IDA dumps with
`research/03040008/ida-transfer/extract_ida.py` (T004, 15322cb3d0; read its docstring), then rerun the
DWARF extractor on the PS4 IDA scope.

1. Private copies: `bash research/ida/private-copy.sh pc-accepted t004b` and `... ps4 t004b`; open each
   with ida-mcp (never save_database).
2. In each, one `execute_python`: `exec(open("D:/ddon-data/research/03040008/ida-transfer/extract_ida.py").read(), {"OUT": "D:/ddon-data/research/03040008/ida-transfer/dumps/<side>-ida.jsonl", "SIDE": "<side>"})`
   with side `pc` then `ps4`. If a call times out, rerun with the script's batching options or headless
   (`idat -A -S"extract_ida.py <OUT> <SIDE> --exit" <copy>`, see the docstring); never change the script.
   The PC run must report `table_ok` (1,041 records, 1,040 callbacks, 74 initializers); if not, stop
   and report what it found.
3. From `research/03040008/ida-transfer/`: `uv run python extract_dwarf.py --ida-dump dumps/ps4-ida.jsonl`
   (check its `--help` for the output path; keep the default) and update `dumps/MANIFEST.tsv` with the
   project's `manifest.py` as the script documents.
4. Sanity counts (jq or stdlib Python): functions per dump, how many PC table callbacks are in scope,
   how many PC functions reference an `OnPacket_` string, PS4 roots by kind, call sites per function
   (median), and 3 spot checks per side: pick a function, compare its call targets and strings with
   IDA's disassembly listing in the same session.
5. A defect in a script (wrong count, a crash, a wrong field): do not fix it; report it with the
   function va and what IDA shows.

Owns: the dumps and `dumps/MANIFEST.tsv` only, and the report
`specs/007-pc-handler-annotation/research/T004b-extract-run.md` (commands, times, sizes, sha256, the
counts, the spot checks). Never touch the scripts, the original databases, ddon-hook, client/, packets/.
Libraries: ida-mcp `execute_python`, uv, jq.
Done: both IDA dumps and the rerun DWARF dump with their sha256 in MANIFEST.tsv; the report; final message
with the path and at most 15 lines. Leave no IDA worker open at the end (close the databases).
Stop: budget 90 min of work time; stop and report if a dump run takes over 30 minutes.
Base: the head when you start.
