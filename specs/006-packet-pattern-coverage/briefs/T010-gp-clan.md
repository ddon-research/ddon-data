006 T010: groups 28 GP, 31 CLAN evidence

Objective (build 03040008, seed PS4 02020005): settle the wire layout of every uncovered id of
groups `28` and `31` in `specs/006-packet-pattern-coverage/research/T001-triage.tsv`
(column `group`; 25 + 14 ids, about 790 captures; unresolved: `28.24.16`-`28.26.16`, `31.53.2`; marked exclusive: `28.23.x`, `28.34.x`, `31.40.1`,\n`31.53.1`)
so an implementer
can write patterns. Method, header rules, counter-tests and report shape exactly as
`research/T005-quest.md` (§ 0-1 method, § 43 summary, § 44 shared types); T001's `recompiled_body`
column is overstated (T003-T005): check each body. GP data overlaps `research/03040008/packets/include/GP.hexpat` (login GP course types, T002) and clan
data the existing clan patterns and `include/Clan.hexpat`: reuse those types and do not redo covered
ids. Naming: a field gets a name only if code backs it (V) or it is inferred with a stated basis
(I); server names go to comments as leads, never into field or `unk_` names.

Per id: PC reader/writer VA (handler table `0x1bc0110`, `WritePacket` `0x8bcbb0`; some handlers sit in
code IDA has not marked as functions: read them instruction by instruction, never change the copy),
PS4 match (V/I/rejected with reason; by code, never by PS4 id number), field table in wire order
(width, DWARF/PC-string name, V/I), Season 3 differences with a PS4-layout counter-test, one walked
capture per id (`xxd`; body ends within the last 15 bytes; bounded `fd`, select by id suffix).
Unresolved: settle by code or give the concrete reason; exclusive: confirm by code.
Cross-check `D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp` +
`PacketData`. Arrowgene structures are leads only; list misplacements.

Extra item (from T009b): in 2.0.2 sample 10055 `CDataStatusInfo` (PC reader `0x77a810`,
`include/Character.hexpat:136-152`) decodes Hp 4507 but MaxHp 760. Read the PC reader's stores and a
consumer of the fields to say whether the order or the PS4 names are wrong for PC (V/I), or whether
the values are consistent (e.g. MaxHp is not the cap); one section in the report.

Owns: only `specs/006-packet-pattern-coverage/research/T010-gp-clan.md`. Never touch
patterns, packets/, client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t010`.
Save the capture walk as `research/T010-walk.py` (re-runnable from the repo root).
Libraries: ida-mcp `execute_python`; stdlib Python for walks.
Done: per id or pair a section, summary table (id, name, PS4 mark, body bytes, walked capture,
fits), shared types per include, Arrowgene misplacements, open items. Final message: report path +
at most 15 lines. Stop: budget 150 min of work time; finish the scope; past 300k context end
`cut short:` with the next id.
Base: the head when you start.
