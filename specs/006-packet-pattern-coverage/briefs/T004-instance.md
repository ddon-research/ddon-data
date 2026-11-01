006 T004: group 13 INSTANCE evidence

Objective (build 03040008, seed PS4 02020005): settle the wire layout of every uncovered id of group
`13` in `specs/006-packet-pattern-coverage/research/T001-triage.tsv` (32 ids, 5,617 captures:
21 matched, 7 unresolved `13.1.16 13.2.16 13.20.16 13.23.16 13.31.16 13.32.16 13.42.16`, 4 marked
Season 3-exclusive `13.16.1/2 13.17.1/2`) so an implementer can write patterns. Method, RES/NTC
header rules and report shape as in `research/T003-connection-server-cert.md` (§ 0 method, § 17
summary, § 18 shared types); 13.44-13.47 are already covered (spec 005 + T001c: read
`research/T001c-parked-static-items.md` item 3 for the bad-status pairing; do not redo them).

Per id: PC reader/writer VA (handler table `0x1bc0110`, `WritePacket` `0x8bcbb0`), the PS4 match
(V/I/rejected with reason; by code, never by PS4 id number), field table in wire order (width,
DWARF/PC-string name, V/I), Season 3 differences, one walked capture per id with `xxd` (body ends
within the last 15 bytes; bounded `fd` under `packets/decrypted_raw/`, select by id suffix).
Unresolved ids: settle each by code or give the concrete reason. Exclusive ids: confirm there is no
PS4 counterpart by code (a different handler shape is not enough when a PS4 function does the same
work); if one turns out matched, include it; otherwise record its PC reader layout only as far as
the PC code shows it (no PS4 names), marked Season 3-exclusive for the later spec.
Cross-check against the recompilation `D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp`
and `PacketData` (accurate where it has a body; T003 found T001's `recompiled_body` column
overstated: check each). Reuse types from `research/03040008/packets/include/` (Context, Character,
nNetMsg, Server, Login …). Arrowgene structures are leads only; list every misplacement.

Owns: only `specs/006-packet-pattern-coverage/research/T004-instance.md`. Never touch patterns,
packets/, client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t004`.
Libraries: ida-mcp `execute_python`; stdlib Python for walks.
Done: per id or REQ/RES pair a section, summary table (id, name, PS4 mark, body bytes, walked
capture, fits), shared types per include, Arrowgene misplacements. Final message: report path + at
most 15 lines. Stop: budget 150 min of work time; finish the scope.
Base: the head when you start.
