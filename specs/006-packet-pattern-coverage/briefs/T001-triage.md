006 T001: triage every uncovered packet id (PS4-matched or Season 3-exclusive)

Objective (build 03040008, seed PS4 02020005): read `specs/006-packet-pattern-coverage/spec.md`
first. For every packet id in the raws without a pattern, find its PC handler and decide whether it
has a PS4 counterpart by code, so 006 can batch the PS4-matched ids by group and list the rest.

1. Inventory: a stdlib Python script (scratch, run with `python -X utf8 -I`) walks
   `packets/decrypted_raw/*/` (os.scandir; never print the listing), groups files by the
   `.<g>_<id>_<sub>` suffix (count, current raw name), subtracts the ids in the `// packet-id:`
   lines of `research/03040008/packets/*-pattern.cpp`, and writes
   `specs/006-packet-pattern-coverage/research/T001-inventory.tsv` (id, raw name, captured count).
   Spec 005 counted about 508 uncovered ids.
2. Per uncovered id (in `PacketId.cs` group order; login C2L/L2C first): the PC S2C handler/reader
   (P4/P11 handler tables, e.g. the group-35 table at `0x212bc68`, the per-group tables P11 found) or
   the C2S writer (the 658 `WritePacket` call sites at `0x8bcbb0`), and the PS4 match by code
   (reader body shape, callers, strings; `cSeedGameSvConnection::OnPacket_*` / `Send_*` symbols),
   never by packet number. Mark: matched (PS4 symbol), exclusive (no PS4 counterpart), unresolved.
   Note whether the PS4 recompilation (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/`)
   has a ReadPacket/WritePacket body for it.
3. Write `research/T001-triage.tsv` (id, raw name, captured, group, PC VA, PS4 symbol or "-", mark,
   recompiled body yes/no) and `research/T001-triage.md` (method, per-group summary: matched /
   exclusive / unresolved counts and packets, the suggested batch order).

Scale: about 508 ids. Work group by group and write the TSV as you go, so a cut-short run still
leaves a usable table; if the budget ends, report which groups are done.
Owns: only the three files under `specs/006-packet-pattern-coverage/research/` named above.
Never touch: patterns, packets/, client/, the user's .i64 files.
Source boundary: PC and PS4 IDA 9.5 via ida-mcp on private copies (`bash research/ida/private-copy.sh
<pc|ps4> t001`); spec 005 reports P2/P4/P5/P11a/P11b for tables and method; the recompilation;
`PacketId.cs` in the Upstream server clone for group numbers and names only.
Libraries: ida-mcp `execute_python`; stdlib Python for the inventory.
Done: the TSV covers every inventory id (or says which groups are not done); the summary. Final
message: report path + at most 15 lines. Stop: budget 120 min of work time; past 300k tokens commit
nothing (you cannot), write the files and hand off with `cut short:`.
Base: ae52337e2d.
