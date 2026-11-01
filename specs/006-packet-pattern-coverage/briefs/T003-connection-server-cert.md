006 T003: game-server connection setup evidence (groups 0 CONNECTION, 1 SERVER, 44 CERT)

Objective (build 03040008, seed PS4 02020005): settle the wire layout of every uncovered id of
groups `0`, `1` and `44` in `specs/006-packet-pattern-coverage/research/T001-triage.tsv` (column
`group`; 15 + 10 + 2 ids, about 5,400 captures) so an implementer can write patterns. Method as in
`research/T002-login.md` (read its method and RES/NTC header sections; reuse its findings: the
manager status/error slots, the PC RES header `s32 Error` then `s32 Result` + body only when
Error == 0, NTCs without error header unless the code reads one). The game server reuses the login
server's g.id.sub for 0.0.x/0.2.x: the existing `C2S_CONNECTION_LOGIN_REQ`/`S2C_CONNECTION_LOGIN_RES`
patterns and the login patterns show how `// packet-select:` keeps them apart.

Per id: PC reader/writer VA (handler table `0x1bc0110`, `WritePacket` `0x8bcbb0`), the PS4 match
(V/I/rejected, with the reason; confirm by code, never by the PS4 id number), the field table in wire
order (width, DWARF/PC-string name, V/I), Season 3 differences, and one walked capture per id with
`xxd` (body ends within the last 15 bytes; bounded `fd` under `packets/decrypted_raw/`, select by id
suffix). Settle `0.10.16` (unresolved in the triage) by code or say why it cannot be.
`44.0.1` C2S_CERT_CLIENT_CHALLENGE_REQ: T002d re-decrypted its 166 raws (spec
`research/T002c-challenge-decrypt.md`): the 336-byte files are the client challenge with no 9-byte
header, the 304-byte files are the server's public key packet under the same name (Sam: keep the
names; patterns select by size, like `C2L_CLIENT_CHALLENGE_REQ-pattern.cpp`). Read the PC writer and
compare it with 1.0.1, and settle why the PC writer calls `WritePacket(p,1,0,1,-1)` while the wire
body has no header (T002c left this open).
Cross-check every layout against the recompilation
`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp` and
`PacketData` (accurate where it has a body; read widths from the disassembly pushes). Reuse types
from `research/03040008/packets/include/` (incl. the new `Login.hexpat`). Arrowgene structures
are leads only; list every misplacement.

Owns: only `specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md`. Never touch
patterns, packets/, client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t003`.
Libraries: ida-mcp `execute_python`; stdlib Python for walks.
Done: one section per id or REQ/RES pair, a summary table (id, name, PS4 match mark, body bytes,
walked capture, fits), shared types per include, the Arrowgene misplacement list. Final message:
report path + at most 15 lines. Stop: budget 120 min of work time; finish the scope.
Base: 20a4617cd4.
