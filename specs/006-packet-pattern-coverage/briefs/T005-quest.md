006 T005: group 11 QUEST evidence (two parts)

Objective (build 03040008, seed PS4 02020005): settle the wire layout of every uncovered id of group
`11` in `specs/006-packet-pattern-coverage/research/T001-triage.tsv` (79 ids, 4,352 captures:
60 matched, 11 unresolved `11.7.16 11.39.16 11.60.16 11.68.16 11.70.16 11.83.16 11.88.16 11.95.16
11.103.16 11.117.16 11.118.16`, 8 marked Season 3-exclusive `11.5.x 11.121.x 11.122.x 11.123.x`)
so an implementer can write patterns. Method, header rules and report shape as in
`research/T004-instance.md` (§ 0 method, § 19 summary, § 20 shared types). The existing quest
patterns and `research/03040008/packets/include/Quest.hexpat` (QuestEnemyInfo order settled in
T001c item 5) are the starting types; T001's `recompiled_body` column is overstated (T003/T004):
check each body.

Large: work in two parts by id range and write both into one report. Part A: ids 11.0-11.60
(incl. their unresolved ones); part B: the rest. If your context passes 300k tokens after part A,
commit nothing, finish the part A sections and summary rows, and end with `cut short:` and the
next id, so the coordinator resumes you or hands part B to a fresh agent.

Per id: PC reader/writer VA (handler table `0x1bc0110`, `WritePacket` `0x8bcbb0`), PS4 match
(V/I/rejected with reason; by code, never by PS4 id number), field table in wire order (width,
DWARF/PC-string name, V/I), Season 3 differences, one walked capture per id (`xxd`; body ends within
the last 15 bytes; bounded `fd`, select by id suffix), and a PS4-layout counter-test where the PC
layout differs. Unresolved: settle by code or give the concrete reason. Exclusive: confirm by code
there is no PS4 counterpart; if matched after all, include it; else record the PC layout only as
far as code shows it, marked Season 3-exclusive. Cross-check against the recompilation
`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp` + `PacketData`.
Arrowgene structures are leads only; list misplacements.

Owns: only `specs/006-packet-pattern-coverage/research/T005-quest.md`. Never touch patterns,
packets/, client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t005`.
Libraries: ida-mcp `execute_python`; stdlib Python for walks.
Done: per id or pair a section, summary table (id, name, PS4 mark, body bytes, walked capture,
fits), shared types per include, Arrowgene misplacements. Final message: report path + at most 15
lines. Stop: budget 180 min of work time; finish the scope.
Base: the head when you start.
