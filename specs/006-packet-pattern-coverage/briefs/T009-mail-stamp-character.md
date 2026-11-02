006 T009: groups 37 MAIL, 45 STAMP, 2 CHARACTER evidence

Objective (build 03040008, seed PS4 02020005): settle the wire layout of every uncovered id of
groups `37`, `45` and `2` in `specs/006-packet-pattern-coverage/research/T001-triage.tsv`
(column `group`; 17 + 8 + 23 ids, about 1,340 captures; unresolved: `2.5.16`, `2.6.16`,
`2.27.16`-`2.32.16`; marked exclusive: `45.3.1/2`, `45.4.1/2`)
so an implementer
can write patterns. Method, header rules, counter-tests and report shape exactly as
`research/T005-quest.md` (§ 0-1 method, § 43 summary, § 44 shared types); T001's `recompiled_body`
column is overstated (T003-T005): check each body. Character data overlaps the existing includes (`research/03040008/packets/include/{Character,Login,Context,Job,Pawn}.hexpat`)
and the 9.x save-blob work (`include/CharacterData.hexpat`): reuse those types and do not redo
covered ids; mail attachments may reuse the item types.

Per id: PC reader/writer VA (handler table `0x1bc0110`, `WritePacket` `0x8bcbb0`; some handlers sit in
code IDA has not marked as functions: read them instruction by instruction, never change the copy),
PS4 match (V/I/rejected with reason; by code, never by PS4 id number), field table in wire order
(width, DWARF/PC-string name, V/I), Season 3 differences with a PS4-layout counter-test, one walked
capture per id (`xxd`; body ends within the last 15 bytes; bounded `fd`, select by id suffix).
Unresolved: settle by code or give the concrete reason; exclusive: confirm by code.
Cross-check `D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp` +
`PacketData`. Arrowgene structures are leads only; list misplacements.

Owns: only `specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md`. Never touch
patterns, packets/, client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t009`.
Libraries: ida-mcp `execute_python`; stdlib Python for walks.
Done: per id or pair a section, summary table (id, name, PS4 mark, body bytes, walked capture,
fits), shared types per include, Arrowgene misplacements, open items. Final message: report path +
at most 15 lines. Stop: budget 150 min of work time; finish the scope; past 300k context end
`cut short:` with the next id.
Base: the head when you start.
