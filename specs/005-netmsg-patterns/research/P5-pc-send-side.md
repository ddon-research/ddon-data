# P5: PC 03040008 send side and the open static items

state: cut short (session restart)

Brief: `specs/005-netmsg-patterns/briefs/P5-pc-send-side.md` (committed at 0497405271). Base 864405afc5.

## What ran

- Read: the brief, `research/P2-pc-deltas.md` (sections 0-4, 7), the coordinator correction in
  `research/P4-context-binary-character.md`, `research/03040008/packets/include/nNetMsg.hexpat`
  (lines 470-890), P1 rows on send path and CREATE_CONTEXT (`rg`).
- Private copies made (`bash research/ida/private-copy.sh pc p5`, `... ps4 p5`):
  - PC 03040008: `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-p5/2022_01_29_DDO_DUMP_FIX.exe.i64`
  - PS4 02020005: `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-p5/DDOORBIS.elf.i64`
- **Not run**: no database was opened; no IDA query ran. The coordinator stopped the work
  (session restart) before the first `open_database`. Nothing below is new evidence: every VA is a
  lead copied from P1/P2/P4 with its status there; no item is settled by P5.

## Per item: not done, with leads

Address basis: IDA VA (PC image base `0x400000`, 32-bit; PS4 base `0`, 64-bit), as P2/P4.

1. **Unnamed nNetMsg fields** (include `unk_*`: CatchRequest u64+u8+u8, CatchInfo u8+u64+u8,
   CtrlAction 0x3C `u32[4]` / 0x3D `u32`, GameNormal 0x0F-0x12, SetCreateContext +0x458/+0x459/+0x460).
   Not done. Leads: PC decoders CatchRequest `0x5fff80`, Caught block `0x6000b0`, 0x3C `0x600900`,
   0x3D `0x6008a0`, CREATE_CONTEXT `0x601b80`; CtrlAction send method = class vtable `0x1bd7668`
   slot 8 (P2 names `0x891750`, not read); apply `0x88ea60` (uses the struct offsets +0x658/+0x668,
   follow them to consumers). PS4 seed: `cNetMsgCtrlAction::sendMessage` `0x383410` and DWARF of
   the CtrlAction struct (no Season 3 fields expected there).
2. **CtrlAction 0x3D and GameNormal 0x0F-0x12 writers**. Not done. Leads: find callers of
   `cNetCtrl::sendNetMessage`-equivalent on PC with msg id 0x40010000|0x3D and 0x41000000|0x0F..0x12
   pushed as immediates (P1 row 1: PS4 `sendNetMessage` `0x2dc3c0`, cNetGame `0x2dc8f0`); GameNormal
   send = vtable `0x1bd7ba0` slot 8; receive `0x8949d0`, 0x0F handler `0x894bf0` (UID lookup
   `sub_88e380`). Names stay `UNK` until PC-side evidence.
3. **CREATE_CONTEXT bool polarity**. Not done. P2 2.25 (V on PC): tail read only when the bool is
   non-zero; P1 (PS4 `0x177060`) reads the s32 when zero. Lead: read PC `0x601b80` jump at the bool
   and the SetNormal send method (vtable `0x1bd8118` slot 8) to see what the writer emits; recheck
   PS4 `0x177060`. Current include follows P2.
4. **75 -> 100 clamp**. Not done. P2 2.6 / 2.25: mOcdActiveMsgNum clamp in receivePktCondition PC
   `0x6033d0` and CREATE_CONTEXT `0x601b80` (V in P2). The include already clamps the array count to
   100 in SetCreateContext; check that `Condition` (include line ~372) applies `min(n, 100)` to the
   array and whether the PC reader still consumes n entries or only the clamped count.
5. **SetNormal / ToolNormal / ToolEasy decoders and senders**. Not done. Leads: SetNormal decoder
   `0x5ff2e0` (jump table `0x5ff39c`), ToolEasy `0x5ff3e0` (jump table `0x5ff468`), stubs
   `0x5ff2c0`, `0x5ff3c0`, `0x5ff480` (I: SetBase/ToolBase/ToolNormal); receive methods
   `0x895d00`, `0x896040`, `0x895fd0` (bytes undefined: decode with `ida_ua`, do not create
   functions); ToolNormal vtable `0x1bd8650` slot 8 `0x8960e0`; DTI initialisers `0x1a370a0`,
   `0x1a37240`, `0x1a37200`. PS4 `cNetSet` `0x3927a0`, `cNetTool` `0x3933c0`.
6. **Send methods vs decoders**. Not done. Leads: slot 8 of each class vtable (CtrlBase `0x1bd7638`,
   CtrlAction `0x1bd7668`, GameNormal `0x1bd7ba0`, GameEasy `0x1bd7bd0`, SetNormal `0x1bd8118`,
   ToolNormal `0x1bd8650`, ToolEasy `0x1bd8680`); `Head::serialize` `0x603d00`; writeU64
   `0x15b3bd0`. Known PS4 mismatch to recheck on PC: sender writes DAMAGE_ACT before CORE_POINT (P1).
7. **Packet names (PC evidence only)** 35.5.16, 13.44-13.47.16, 35.8.16, 35.12.16, direction of
   63.11.16: all **unresolved**. Leads: group-35 handler table filled by `sub_1A2A4D0` (P4: key at
   +0x10 = (sub<<16)|id, handlers pass name strings to `callOnPacketFunc`); C2S writers from the 658
   call sites of `WritePacket` `0x8bcbb0` (cdecl `(packet, group, id, sub, -1)`); look for the
   callers of the 35.5/35.8/35.12/13.44-47 writers and any log/name strings; for 63.11.16 check
   whether PC has a `WritePacket(0x3F, 0x0B, 0x10)` call site (C2S) or a handler-table key (S2C).
   The withdrawn P4 claim (35.5.16 = CHARACTER_START_BAD_STATUS, by PS4 number) is not evidence.
8. **Server disagreements**. Not done beyond P4's list. Known lead: `PacketId.cs:2013`, field
   `C2S_63_11_16_NTC` vs Name `S2C_63_11_16_NTC` with `PacketSource.Server` (internal inconsistency
   of the server; lead only).

## Pattern changes

None proposed: nothing was verified in this run.

## Left for the live phase

Not determined: the static items above were not attempted. A fresh P5 should run them first
(Sam: static before live).
