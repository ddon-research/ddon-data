005 P5: close the open static items on the PC 03040008 send side

Question/objective (build 03040008, seed PS4 02020005): Sam (2026-11-01) wants the static path
exhausted before any live client/server run. Close every item below that IDA can close. Read first:
`research/P2-pc-deltas.md` (PC VAs, Season 3 widening), the coordinator correction at the top of
`research/P4-context-binary-character.md`, and the shared include
`research/03040008/packets/include/nNetMsg.hexpat` (what the patterns decode today).

Items:
1. nNetMsg fields the patterns leave unnamed (`unk`/`Unk` in the include): name each from the PC
   writer/reader and the PS4 DWARF names, or say why not.
2. CtrlAction 0x3D (1 x u32) and GameNormal 0x0F-0x12: what writes them on PC (send methods,
   callers, the data they read); names only from PC-side evidence or a PS4 function matched by code.
3. CREATE_CONTEXT bool polarity: P1 and P2 disagree; settle it from the PC code.
4. The 75 -> 100 clamp P2 reports: where, what it limits, whether a pattern needs it.
5. SetNormal, ToolNormal, ToolEasy messages (never captured): their PC decoders and senders, so the
   patterns cover them without captures.
6. The PC send methods for the nNetMsg classes (serialize side) cross-checked against the decoders.
7. Packet names from PC-side evidence only: 35.5.16, 13.44-13.47.16, 35.8.16, 35.12.16, and the
   direction of 63.11.16 (`PacketId.cs:2013` field `C2S_63_11_16_NTC`, Name `S2C_63_11_16_NTC`,
   `PacketSource.Server`). PS4 02020005 numbers packets as a flat u16, so a PS4 number never names a
   PC packet: use handler or log strings in the PC binary, or the PC caller of the writer matched to a
   PS4 symbol by code (callers, strings, data it reads). If nothing settles a name, say "unresolved".
8. Server structures are community-handcrafted leads, never evidence; list disagreements you meet.

Owns: only `specs/005-netmsg-patterns/research/P5-pc-send-side.md` (Write it; no other file).
Never touch: client/, packets/, research/03040008/packets/, the user's .i64 files, other reports.
Source boundary: PC and PS4 IDA 9.5 through ida-mcp on private copies
(`bash research/ida/private-copy.sh pc p5`, `... ps4 p5`); the generated C++
(`C:/ddon-dwarf-reconstructor-rust/output_2026-11-01_031_o6_a2/`, `D:/ddon-data-s2/recompilation/src/`);
captures via `xxd` (raw names now carry the server's current names, match by the `.<g>_<id>_<sub>`
suffix). No `*.elf.c/.h` or `IDA9.5/*.exe.c` exports.
Libraries: ida-mcp `execute_python`; no own tooling.
Done: per item a VA, the answer, a mark V (read in IDA) / I (inferred) / unresolved, and what a
pattern must change; a closing list "left for the live phase". Final message: the report path and
at most 15 lines; if the hand-back tool is refused, put it in plain text.
Stop: budget 90 min of work time. Stop and report if ida-mcp will not open the copies.
Base: 864405afc5.
