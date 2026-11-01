005 P4: wire format of the context, binary-save and character notice packets

Question/objective (build: 03040008, seed PS4 02020005): Sam (2026-11-01) widened 005 from the
nNetMsg carriers to every context, binary and character-related packet next to them. Give a
pattern author the Season 3 PC wire format of the packets below, the way P1/P2 did for nNetMsg.
Read `specs/005-netmsg-patterns/research/P2-pc-deltas.md` first for the method, the PC address
basis and the Season 3 widening rule (most *Uid/*UniqueId fields u32 -> u64); do not redo its work.

Packets (group.id.sub; captured count in `packets/decrypted_raw`; raw file names come from an older
name table, so match files by the `.<g>_<id>_<sub>` suffix, not by name):
A. CONTEXT, group 35, every id the server lists: 35.0-35.4 x {1,2,16} (GET_LOBBY/PARTY/ALL_PLAYER,
   PARTY_MYPAWN, PARTY_RENTED_PAWN _CONTEXT), 35.5.16 (2, "Unknown"; server: C2S_CONTEXT_35_5_16_NTC),
   35.7.1 (223) / 35.7.2 (608) GET_SET_CONTEXT, 35.9.16 C2S_SET_CONTEXT_NTC (763), 35.10.x
   MASTER_THROW, 35.11.16 SET_CONTEXT_BASE_NTC (526), 35.12.16 (unnamed), 35.13.16 S2C_SET_CONTEXT_NTC
   (24), 35.14.16 MASTER_CHANGE_NTC (948), 35.15.16 MASTER_INFO_NTC (43); 35.0.16 (264) and
   35.3.16 (9) are captured too.
B. BINARY_SAVE, group 9: 9.0.1/9.0.2 GET_CHARACTER_BIN_SAVEDATA (0 captured), 9.1.1/9.1.2
   SET_CHARACTER_BIN_SAVEDATA (47 each). Besides the packet body: which class writes and reads the
   save blob, and its layout (field table; nested classes one level deep, deeper ones named only).
C. Character notices the raws call "Unknown": 2.13.16 CHARACTER_DOWN (14), 2.15.16 CHARACTER_DEAD
   (7), 2.19.16 PAWN_DOWN (20), 2.20.16 PAWN_DOWN_CANCEL (10), 13.44.16 / 13.45.16 CHARACTER
   START/END_BAD_STATUS (19 / 19), 13.46.16 / 13.47.16 ENEMY_BAD_STATUS_START/END (31 / 30).

Per packet, answer: the PC reader or writer VA (and the PS4 one with its symbol) and how it was
identified; a field table in wire order with Season 3 types; differences from PS4; for a captured
packet, a byte walk of one capture to `len` (`xxd`); where the server's structure
(`Arrowgene.Ddon.Shared/Entity/PacketStructure/*.cs` and `Entity/Structure/CData*.cs` in
`C:/Users/morph/Documents/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Upstream`) disagrees with the
client. Leads: DDON_RE `packet_docs/GamePackets.md` in the clone `D:/GitHub/sebastian-heinz/DDON_RE`
lists PC handler VAs per packet (P2 found 0x7e97a0/0x7e9880 that way); the PS4 symbols
(`cSeedGameSvConnection::OnPacket_*`, `*::ReadPacket`, `*::WritePacket`); the server's names are
leads, not proof. Note how the context packets relate to nNetMsg (CtrlBase CREATE_CONTEXT,
mUniqueId, master/session index) where the code shows it.

Server structures are community-handcrafted (Sam, 2026-11-01; sent to the running agent): derive
each layout from the client first (PS4 IDA, then PC IDA), cross-check with the generated C++
(`C:/ddon-dwarf-reconstructor-rust/output_2026-11-01_031_o6_a2/`, `D:/ddon-data-s2/recompilation/src/`),
and only then list the server's misplacements (order, width, signedness, missing/extra fields,
counts, PacketSource/name in `PacketId.cs`) in a "Server structure misplacements" section with
server file:line, client VA and V/I mark.

Priority if time runs short: A (captured ones first), then C, then B's packet body, then B's blob.

Owns: only `specs/005-netmsg-patterns/research/P4-context-binary-character.md` (Write it; no other
file). Never touch: client/, packets/ data, the user's .i64 files, research/03040008/packets/, the
P1/P2 reports.
Source boundary: the PC and PS4 IDA 9.5 databases through ida-mcp on private copies
(`bash research/ida/private-copy.sh pc p4`, `bash research/ida/private-copy.sh ps4 p4`); P1/P2;
the server and DDON_RE clones (read-only); captures via `xxd`. Do not read
`binaries/PS4_02020005/*.elf.c/.h` or `IDA9.5/*.exe.c` exports.
Libraries: ida-mcp `execute_python` (ida_hexrays, ida_bytes, idautils); no own tooling.
Done: each packet has a VA, a field table and a mark per item: V (read in IDA), I (inferred),
PC-cap (captures only); each captured type has a walk ending at `len` or the offset where it
fails; a list of what is left open. Return a summary of at most 40 lines. If the hand-back tool is
refused, put the summary in your final message as plain text.
Stop: budget 90 min of work. Stop and report if ida-mcp will not open the copies, or if no PC
handler for group A is located within 25 min (report what you tried).
Base: 2a9f798b05. No commits.
