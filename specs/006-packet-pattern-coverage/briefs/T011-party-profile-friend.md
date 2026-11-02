006 T011: groups 6 PARTY, 26 PROFILE, 16 FRIEND, 17 BLACK, 5, 24 evidence

Objective (build 03040008, seed PS4 02020005): settle the wire layout of every uncovered id of
groups `6`, `26`, `16`, `17`, `5` and `24` in `specs/006-packet-pattern-coverage/research/T001-triage.tsv`
(column `group`; 11 + 6 + 4 + 2 + 2 + 1 ids, about 1,150 captures; unresolved: `5.2.16`, `5.3.16`, `6.8.16`,\n`6.10.16`, `6.18.16`, `24.6.16`)
so an implementer
can write patterns. Method, header rules, counter-tests and report shape exactly as
`research/T005-quest.md` (§ 0-1 method, § 43 summary, § 44 shared types); T001's `recompiled_body`
column is overstated (T003-T005): check each body. Party, friend and profile data overlap the existing includes (`Character`, `Context`, `Login`,
`CharacterInfo`, `Pawn` in `research/03040008/packets/include/`; `CDataCharacterListElement` carries the
Season 3 trailing u8): reuse those types and do not redo covered ids. Naming: a field gets a name only if code backs it (V) or it is inferred with a stated basis
(I); server names go to comments as leads, never into field or `unk_` names.

Per id: PC reader/writer VA (handler table `0x1bc0110`, `WritePacket` `0x8bcbb0`; some handlers sit in
code IDA has not marked as functions: read them instruction by instruction, never change the copy),
PS4 match (V/I/rejected with reason; by code, never by PS4 id number), field table in wire order
(width, DWARF/PC-string name, V/I), Season 3 differences with a PS4-layout counter-test, one walked
capture per id (`xxd`; body ends within the last 15 bytes; bounded `fd`, select by id suffix).
Unresolved: settle by code or give the concrete reason; exclusive: confirm by code.
Cross-check `D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp` +
`PacketData`. Arrowgene structures are leads only; list misplacements.

Owns: only `specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md`. Never touch
patterns, packets/, client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t011`.
Save the capture walk as `research/T011-walk.py` (re-runnable from the repo root).
Libraries: ida-mcp `execute_python`; stdlib Python for walks.
Done: per id or pair a section, summary table (id, name, PS4 mark, body bytes, walked capture,
fits), shared types per include, Arrowgene misplacements, open items. Final message: report path +
at most 15 lines. Stop: budget 150 min of work time; finish the scope; past 300k context end
`cut short:` with the next id.
Base: the head when you start.
