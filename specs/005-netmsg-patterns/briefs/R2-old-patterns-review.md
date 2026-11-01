005 R2 (T023): review the 36 fixed old packet patterns and their includes

Objective (build 03040008): an independent review of P12a (5c1d58caef..0fb1644208) and P12b
(e44421b3c5..25aa58b571) before spec 005 closes. Commits are the git receipt; you cannot run git.
Files: `research/03040008/packets/include/{Packet,Quest,Area,Character,Clan,Item,Pawn,Skill,Context}.hexpat`
and the 36 patterns those commits touched in `research/03040008/packets/`.

Review against the evidence: `specs/005-netmsg-patterns/research/P11a-old-patterns.md`,
`P11b-old-patterns.md`, and the PS4 recompilation C++ `D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/`
(`UserSession/{C2S,S2C}.cpp` ReadPacket/WritePacket, `LoginSession/`, `PacketData/*.h`; believed
accurate where present, gaps elsewhere; IDA can misread stack-argument order).

Look for, in this order:
1. A field whose width, order, signedness, count or condition disagrees with P11a/P11b or with a
   recompiled ReadPacket body (the two recorded disagreements: 13.3.2 Result s32 vs u32, RES Error
   s32 vs PS4 u16; judge whether the comments are right).
2. The RES error guard (Result and body only when Error == 0) and 18.0.2's server-written trailing
   bytes: correct, and the fit flags meaningful?
3. Shared includes: one definition per structure, no duplicate or diverging copies, comments with
   the PC reader VA, the PS4 match and V/I marks.
4. Names and enums: no name from a PS4 packet number or from server C# as evidence; enums only from
   PS4 DWARF; `unk_*` placeholders where the evidence has no name.
5. The 0.1.1/0.1.2 login vs game-server CONNECTION_LOGIN suffix collision: is the selection safe?
6. Consistency with the P9/P10 conventions (header keys, `count`/`entries`, `sourceOk`,
   `paddingSize`, `fits`, `// packet-id:`).

Owns: nothing (read-only).
Done: findings ranked by severity with file:line, the report or recompilation line contradicted, a
failure case and a fix; what you checked and found correct; what you could not check. Final
message: at most 80 lines.
Stop: budget 45 min of work time.
Base: 29fef68022.
