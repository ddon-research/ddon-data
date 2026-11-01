006 T002: login group evidence (C2L/L2C, all 21 uncovered ids)

Objective (build 03040008, seed PS4 02020005): settle the wire layout of every uncovered login-server
id so an implementer can write patterns: rows `L:*` of `specs/006-packet-pattern-coverage/research/T001-triage.tsv`
(21 ids, groups L0-L5: ping, logout, client challenge, game session key, login setting, next connect
server, error message list REQ/RES/NTC, GP course, character list, decide character id, login wait
num). 6 are matched, 15 have only a PS4 candidate (`(candidate)` in `ps4_symbol`): confirm or reject
each candidate by code (reader/writer body shape, handler structure, strings, callers), never by the
PS4 id number (PS4 ids are a flat u16 and do not name PC packets).

Per id: PC reader/writer VA (handler table, login list `0x1bd6270`, `WritePacket` `0x8bcbb0`), the
PS4 match (V/I/rejected, with the reason), the field table in wire order (width, name from PS4 DWARF
or PC strings, V/I), RES error handling (PC `s32 Error`, then body only when Error == 0), and any
Season 3 difference from PS4. Cross-check each layout against the recompilation
`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/LoginSession/{C2L,L2C}.cpp` (accurate where
it has a body; IDA misreads stack arguments: read widths from the disassembly pushes) and reuse the
shared types of the existing `C2L_LOGIN_REQ` / `L2C_LOGIN_RES` patterns and `research/03040008/packets/include/`
where they match. Arrowgene's `Arrowgene.Ddon.Shared/Network` structures are leads only; list every
misplacement you find in them. Walk one capture per id with `xxd` (select by the id suffix, e.g.
`.5_0_2`, under `packets/decrypted_raw/`; bounded `fd`): the body must end within the last 15 bytes.

Owns: only `specs/006-packet-pattern-coverage/research/T002-login.md`. Never touch patterns, packets/,
client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t002`.
Libraries: ida-mcp `execute_python`; stdlib Python for walks.
Done: one section per id (or per REQ/RES pair) as above, a summary table (id, name, PS4 match mark,
body bytes, walked capture, fits), the shared types a pattern author should add to which include,
and the Arrowgene misplacement list. Final message: report path + at most 15 lines.
Stop: budget 120 min of work time; finish the scope.
Base: a564bde7f0.
