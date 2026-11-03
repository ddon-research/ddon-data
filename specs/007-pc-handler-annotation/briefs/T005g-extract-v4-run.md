007 T005g: run extractor v4 on both sides (read-only batch runs)

Objective (PC 03040008, PS4 02020005): v4 dumps for the matcher and the transfer rules. `extract_ida.py` v4
(778d9264db; README). Read-only: the extract batch discards its session.

1. PC: batch on the work copy `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`
   (check sha256 `65120b34...8b9111` before and after; must be unchanged) -> `dumps/pc-ida.jsonl`.
2. PS4: `bash research/ida/private-copy.sh ps4 t005g`, batch -> `dumps/ps4-ida.jsonl`; delete the copy after.
3. Counts per side: functions, `table_ok` (PC), missing roots, object-relative access records (and how many
   `indexed`, how many via a pointer load), `requester_site` records, PS4 slot stores, functions with a
   non-null `codec_distance`, run time and size. Spot checks (a read-only batch script in your scratchpad):
   for 2 PC and 2 PS4 functions, 5 access records each against the listing (base register really holds the
   argument, disp and width right); for 2 requesters per side, the slot value against the listing.
4. `manifest.py` for `dumps/MANIFEST.tsv`; also run `uv run python extract_dwarf.py --ida-dump dumps/ps4-ida.jsonl`
   if the PS4 scope grew (compare function counts), and note it.

Owns: the dumps, `dumps/logs/*`, `dumps/MANIFEST.tsv`, the report
`specs/007-pc-handler-annotation/research/T005g-extract-v4.md`. Never touch scripts, the original or
accepted databases, ddon-hook, client/, packets/; never open the work copy in ida-mcp.
Libraries: idat batch, jq. Done: the report; final message with the path and at most 15 lines.
Stop: budget 60 min of work time. Base: the head when you start.
