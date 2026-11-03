008 T001: triage every captured packet id without a pattern (evidence)

Question (client 03040008): which ids in `packets/decrypted_raw` still have no pattern, and for each, what do PC
code, captures, the extractor data and the server leads already give? Read `specs/008-remaining-packets/spec.md`
(sources, marks) and `specs/006-packet-pattern-coverage/research/season3-exclusive.tsv` (115 ids, PC VAs, the
006 reports' layout notes).

1. **Inventory**: recount the uncovered ids: distinct (side, g.id.sub) in `packets/decrypted_raw` (login vs game
   by the raw name prefix, as 006 T001 § Method; suffix `.<g>_<id>_<sub>`; TC3 added `_1`, `_2` stem suffixes)
   minus the `// packet-id:` of `research/03040008/packets/*-pattern.cpp`. Count files per id and per stream. Use
   `os.scandir` (stdlib); never list `packets/` unbounded in the shell.
2. **Per id** (TSV `research/T001-triage.tsv`): direction; captured count; size range of bodies; PC handler VA
   (S2C: the handler table, `research/03040008/ida-transfer/dumps/pc-ida.jsonl` `table` records) or PC sender VA
   (C2S: the function calling `WritePacket` `0x8bcbb0` with that constant key, from the v6 dump's call-site argument
   values); the PC `OnPacket_` string name if any; the PC reader/writer VA and its codec call tree as a width
   sequence (codec widths from the dump's `codec` fields; element readers by call; strings / arrays marked), or
   "no reader" (handler ignores the body); the 006 report's notes; the Arrowgene lead (`PacketId.cs` name and the
   C# structure's field list, file:line); a first fit check of the PC width sequence against the captures
   (fits n/m, with arrays expanded from the count fields).
3. **Batches**: group the ids into batches of about 10-20 by group / shared structures, ordered by captured count;
   say for each batch which need IDA reading (reader not in the dump, indirect calls, inline reads).

Tools: stdlib Python over the dumps, raws and Arrowgene sources (scripts under
`specs/008-remaining-packets/research/t001/`); IDA only if a reader is missing from the dump (read-only, private copy
`bash research/ida/private-copy.sh pc-accepted t001` or headless batch on a `cp` of the wave-2 database in
`PC_DDON_03040008/ddon-data-t001w/`, deleted after).
Owns: `specs/008-remaining-packets/research/T001-*` and `research/t001/`. Never touch patterns, packets/, client/,
the databases' originals, ddon-hook.
Done: `research/T001-triage.md` (counts, method, batches) + the TSV; final message with the path and at most 15
lines. Stop: budget 120 min of work time. Base: the head when you start.
