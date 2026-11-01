005 P2: PC 03040008 deltas against the PS4 nNetMsg wire format

Question/objective (build: 03040008): turn the PS4 02020005 decoder description in
`specs/005-netmsg-patterns/research/P1-ps4-wire-format.md` (read it first; it is the baseline)
into the Season 3 PC wire format, by reading the PC decoders. Report only what differs from P1,
plus confirmations, so a pattern author can apply the deltas to P1's tables.

Answer, from the PC database (no symbols; locate by structure):
1. Locate the PC counterparts of P1's decoders: Head::deserialize, CtrlBase, CtrlAction::deserialize
   and every helper P1 lists (2.4-2.20), GameNormal, GameEasy, SetNormal, ToolEasy, popNetPos,
   popNormalPos. Leads: the DTI name strings ("cNetMsgCtrlAction", "cNetMsgGameNormal", ...) and
   their MtDTI constructors and vtables; createNetMsg's `msgIdFull & 0xFFFFFF00` lookup; the
   receive handlers from DDON_RE (S2C_LOBBY_3_4_16_NTC 0x7e2ad0, S2C_PARTY_6_22_16_NTC 0x7e72b0,
   S2C_PARTY_6_24_16_NTC 0x7e97a0, S2C_PARTY_6_26_16_NTC 0x7e9880); P1's PS4 VAs for byte and
   call-shape comparison. Names already in the PC database (ddon-hook annotated some) may help;
   cite them as names, not proof.
2. Per decoder, the deltas: widened or narrowed types (P1 inferred u64 for Head.mRpcId,
   CtrlBase.mUniqueId and the TARGET mTargetUid; check every other *Uid/*UniqueId field), added,
   removed or reordered fields, changed clamps/counts, changed switch cases.
3. The PC include-packet table (createIncludePacketCtrl): every entry, and its size (Season 3
   captures carry msg ids up to at least 0x3C; P1's PS4 table stops at 0x38 = index 0x37). Bits
   that are new on PC and what the decoder reads for them.
4. Season 3 msg ids beyond the PS4 enum (0x3C and any other): what they read. Names only if an
   enum, string or log text gives one; otherwise call them `NET_MSG_ID_UNK_0x3C`.
5. The packet bodies of 3.3.16, 3.4.16, 6.23.16, 6.25.16 (and the S2C 6.22/6.24/6.26) on PC: confirm
   or correct P1 section 1.
6. Walk, byte by byte to `len`, one capture each for msg ids 0x02, 0x08, 0x0B, 0x0D, 0x24, 0x25,
   0x34, 0x37 (lobby 3.3.16 or binary 6.25.16) and 0x23, 0x2E, 0x31, 0x35, 0x3C (binary 6.25.16).
   msgIdFull is the BE u32 at payload offset 12 in both packet types (s32 session, u64 rpc,
   u32 msgIdFull); the payload starts after the `s32 len` (lobby: packet offset 18; 6.25.16 with an
   empty CharacterIdList: packet offset 17). Pick samples by file name under
   `packets/decrypted_raw/` and dump them with `xxd`.
   Report where a walk does not end at `len`.

Owns: only `specs/005-netmsg-patterns/research/P2-pc-deltas.md` (Write it; no other file).
Never touch: client/, packets/ data, the user's .i64 files, research/03040008/packets/, P1's report.
Source boundary: the PC IDA 9.5 database through ida-mcp on your private copy
(`bash research/ida/private-copy.sh pc p2`); the PS4 copy too if a comparison needs it
(`bash research/ida/private-copy.sh ps4 p2`; the name p1 is still held); P1's report; captures
via `xxd`. Do not read `binaries/PS4_02020005/*.elf.c/.h` or `IDA9.5/*.exe.c` exports.
Libraries: ida-mcp `execute_python` (ida_hexrays, ida_bytes, idautils); no own tooling.
Done: the report has (a) a PC VA for each decoder with how it was identified, (b) one delta table
per decoder (or "same as P1" with the evidence), (c) the full PC include table, (d) the new msg
ids, (e) packet bodies, (f) the walks; each item marked V (read in IDA), I (inferred) or
PC-cap (captures only). Return a summary of at most 40 lines.
Stop: budget 75 min of work. Stop and report if ida-mcp will not open the copy, or if the PC
decoders cannot be located within 25 min (report what you tried).
Base: <filled at spawn>. No commits.
