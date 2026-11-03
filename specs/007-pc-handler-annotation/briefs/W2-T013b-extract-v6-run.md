007 W2 T013b: run extractor v6 on both sides and the matcher (read-only batch runs)

Objective (PC 03040008, PS4 02020005): v6 dumps (T013a; README) and the regenerated matcher manifest.
1. PC: headless batch on the work copy `ddon-data-007work` (sha256 `f7f3a219...3c25` before and after; the extract
   discards its session) -> `dumps/pc-ida.jsonl` (the wave-1 baseline `pc-ida-applied.jsonl` stays).
2. PS4: `bash research/ida/private-copy.sh ps4 w2b`, batch -> `dumps/ps4-ida.jsonl`; delete the copy after.
   Re-run `extract_dwarf.py --ida-dump` only if the PS4 function count changed.
3. Counts: call sites with argument values by kind (constant, obj+X, stack, element), padding nops skipped, the
   T012 numbers to compare (502 PC / 340 PS4 lea destination sites; 975 aligned codec site pairs). Spot checks
   (read-only batch script under `specs/007-pc-handler-annotation/research/w2b/`): 3 call sites per side against
   the listing.
4. `cd research/03040008/ida-transfer && uv run python match.py`: report the changes in `manifest/*.tsv` against
   the committed state (pairs added/removed per rule, `callsites.tsv` new columns filled); twice identical.
5. `manifest.py` for `dumps/MANIFEST.tsv`.
Owns: the dumps, logs, `dumps/MANIFEST.tsv`, the regenerated `manifest/*.tsv` (not `manifest/transfer/`), the
spot-check script folder, the report `specs/007-pc-handler-annotation/research/W2-T013b-run.md`. Never touch the
scripts, the original or accepted databases, ddon-hook, client/, packets/; never open the work copy in ida-mcp.
Libraries: idat batch, uv, jq. Done: the report; final message with the path and at most 15 lines.
Stop: budget 60 min of work time. Base: the head when you start.
