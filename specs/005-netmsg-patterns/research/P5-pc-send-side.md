# P5: PC 03040008 send side and the open static items

Brief: `specs/005-netmsg-patterns/briefs/P5-pc-send-side.md` (committed at 0497405271). Base 864405afc5.
Supersedes the cut-short P5 report at this path.

## What ran

- Databases (ida-mcp headless, private copies from the earlier P5 run, reused):
  - PC 03040008: `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-p5/2022_01_29_DDO_DUMP_FIX.exe.i64`,
    confirmed with `idc.get_idb_path()`, 32-bit, image base `0x400000`.
  - PS4 02020005: `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-p5/DDOORBIS.elf.i64`,
    confirmed, 64-bit, image base `0`.
- Read-only: decompilation, forced disassembly of undefined bytes (`generate_disasm_line` with
  `GENDSM_FORCE_CODE`; no function creation), xrefs, binary searches. Nothing renamed, retyped or saved.
- Not run: the generated C++ (`C:/ddon-dwarf-reconstructor-rust/output_2026-11-01_031_o6_a2/` does
  not exist on disk; PS4 DWARF types were read from the PS4 IDB instead); captures (`xxd`); no
  server source opened beyond the brief's citation.
- Address basis: IDA VA. Marks: **V** = read in IDA, **I** = inferred, **C** = contradicts an earlier claim.
- Caveat: several PC send methods and decoders lie in bytes IDA left as data
  (e.g. `0x8912a0`, `0x895500`, `0x5ff2e0`); they were read as forced disassembly, not pseudocode.
- Caveat: the PC IDB already carries user names on some functions (`Send_C2S_SET_CONTEXT_BASE_NOTICE`
  `0x824ba0`, `Send_C2S_SET_CONTEXT_NOTICE` `0x824c80`, `cNetGameServer::reqSetContext` `0x87c3e0`;
  `has_user_name` = True). They are earlier annotations of unknown provenance; none is used as
  evidence below. Names come only from strings in the PC binary or a PS4 symbol matched by code.

## Item 1: unnamed nNetMsg fields

PS4 DWARF (`nNetMsgData::CtrlAction::stMsgCtrlActionData`, `stCatchInfo`,
`SetNormal::stCreateContext`, `cContextInstance`) has none of these fields, so no field can take a
DWARF name. Roles below are read from the PC writer, reader and consumer.

| Field (include) | PC evidence | Answer | Mark |
| --- | --- | --- | --- |
| CatchRequest `unk_u64`, `unk_u8_0`, `unk_u8_1` (ids 0x1E, 0x38) | decoder `0x5fff80` stores +840/+848/+849; apply `0x88f500` passes +840 through the UID lookup `sub_88e380` like mCatchRequestUid, then setters `0x4795e0` (ctx +0x70, u64), `0x479600` (ctx +0x68, u8), `0x4795d0` (ctx +0x69, u8); the first triple uses `0x4795a0` (+0x60 uid), `0x4795c0` (+0x58 type), `0x479590` (+0x59 joint). Sender `0x891d10` writes uid, u8, u8, uid2, u8, u8, pos (getters `0x4746a0`,`0x4746c0`,`0x474690`,`0x4746e0`,`0x474700`,`0x4746d0`). | A second catch triple: `unk_u64` = second catch target UID, `unk_u8_0` = second catch type, `unk_u8_1` = second joint no. Names unresolved (no PC string, no PS4 field). | V layout and data flow; I role names |
| CatchInfo `unk_u8_0`, `unk_u64`, `unk_u8_1` (ids 0x1F, 0x20) | decoder `0x6000b0` stores +912 u8, +920 u64, +928 u8, +936 u8, +944 u64, +952 u8. Apply `0x88f6e0` uses only +936/+944/+952, as (type, uid, joint), for both context triples; +912/+920/+928 are not read there. | Same second-triple roles (type, uid, joint). On PC the apply ignores the PS4-era triple. | V; I names |
| CtrlAction 0x3C `unk_0x3C[4]` | decoder `0x600900` (+0x658); apply `0x88f970` calls `sub_479fd0(ctx, chara, i, v)` for i < 4, writing `ctx + 0xC48 + 4*i`, only if the character flag `+6616 & 2`, then vtable +960. Sender (case 60 of the CtrlAction send switch at `0x8915e3`) `0x8927f0` writes `sub_475520(ctx, chara, i)` for i = 0..3. | Four u32 values of a Season 3 context array at `cContext* + 0xC48`, synced absolutely. Name unresolved. | V |
| CtrlAction 0x3D `unk_0x3D` | decoder `0x6008a0` (+0x668); apply `0x88f910` acts only when the object's DTI is `uEm024000` (DTI `0x21c4568`, initializer `0x1a7efa0` pushes "uEm024000"), calling `sub_cd6f90(obj, v, 0)`: adds the **signed** delta to array slot 0 (`ctx+0xC48`), clamps to [0, obj+0x21A8], sets obj+0x21B8 when the max is reached. Sender (case 61) `0x892780` writes `uEm024000+0x21B0` (an accumulator filled by `0xcd7060`) and zeroes it. | A signed gauge delta for enemy class `uEm024000` (absent from PS4 02020005). Name unresolved. | V |
| GameNormal 0x0F-0x12 | see item 2 | | |
| SetCreateContext `unk_u8_0`, `unk_u8_1`, `unk_u64` (+0x458/+0x459/+0x460) | decoder `0x601b80` reads, after mStateLive (+864), u8 +1102, u8 +1103, u64 +1104 (PS4 mCatchType, mCatchJointNo, mCatchTargetUID), then u8 +1112, u8 +1113, u64 +1120. | Same (type, joint, uid) shape as the PS4 catch tail, repeated: a second catch triple, matching the second triple added to CatchRequest/CatchInfo and to cContextInstance (+0x68/+0x69/+0x70). The CreateContext consumer was not read. | V layout; I role |

Pattern change: rename only in comments (e.g. `// Season 3, second catch target UID (inferred)`);
make `unk_0x3D` an `s32`. No layout change.

## Item 2: writers of CtrlAction 0x3D and GameNormal 0x0F-0x12

- CtrlAction send body: vtable `0x1bd7668` slot 8 = `0x8912a0` (data bytes). It calls the base
  writer `0x891750`, writes four bools from `[ebp+0x19D8]` bits 1, 2, 4 and `[ebp+0x19D9]` bit 3,
  then include sections by bit, then a per-id switch at `0x8915e3` on the message id byte
  `this+0x31`. Case 60 → `0x8927f0`, case 61 → `0x892780` (item 1). **V**
- GameNormal send body: vtable `0x1bd7ba0` slot 8 = `0x895500` (data bytes), switch on `this+0x31`:
  - 0x0F → `0x895650`: from `sEnemyManager` (singleton `dword_21af4f4`; its vtable `0x1c8e208`
    slot 4 returns DTI `0x21af500`, whose initializer pushes "sEnemyManager") block at +0xDB0
    (`sub_b551e0`): `writeU32(+8)`, UID writer `0x88e3d0`(+0x10), UID writer(+0x18). Receive
    `0x894bf0` reads +60 u32, +64 and +72 through `sub_88e380` (UID lookup) and stores them with
    `sub_4d3060` into the same block. **V**. The include's "inferred: a UID" becomes V.
  - 0x10 → `0x895630`: `writeU32(sEnemyManager+0xDB0+0x28)`; receive `0x894bc0` stores it back. **V**
  - 0x11 → `0x8958b0`: if `sGame+0x74` is non-null, writes constant `u32 1`; otherwise writes
    **nothing**. Receive `0x894e00` ORs the value into `cContextInstPl + 0x3A94` (setter
    `0x478e40`, DTI check "cContextInstPl") of the sender's character. **V**
  - 0x12 → `0x895870`: if `sGame+0x74` is non-null, writes `u32 = sub_477380(sub_bb0eb0(id))` =
    `cContextInstPl + 0x3A90` of the player found by the id at `cContextInstHm + 8676`; otherwise
    nothing. Receive `0x894dc0` sets `cContextInstPl + 0x3A90` (setter `0x47baf0`) and calls
    `sub_bb1600`. **V**
- No PC string names any of these; PS4 02020005 has no counterpart (PS4 `sEnemyManager` is 232
  bytes). Names: **unresolved**.
- The callers that request these message ids were not found: `0x4100000F..12` / `0x4001003C/3D`
  immediates do not occur as message ids (the 0x4100000F hits are floats). Left open.

Pattern change: 0x11 and 0x12 may carry an empty body; the u32 must be optional (read only if
bytes remain), otherwise such a message will not `fits`.

## Item 3: CREATE_CONTEXT bool polarity

- PC `0x601b80`: `mAdditionalData = (u8 != 0)`; everything after it is read only when it is
  non-zero. **V**
- PS4 `nNetMsgData::SetNormal::receiveMsgSetCreateContext` `0x177060`:
  `if (!pData->mCreateContextInfo.mAdditionalData) return;` then mMasterIndex. **V**
- P1's claim (the s32 is read when the bool is zero) is **contradicted (C)**; P2 2.25 is right on
  both platforms. The PS4 C2S path agrees: `cNetGameServer::reqSetContext` `0x363440` sends
  SET_CONTEXT_NOTICE when `isAdditional`, SET_CONTEXT_BASE_NOTICE otherwise.

Pattern change: the include already follows P2; fix only the comment at include line 776-777
(drop "P1 reads the s32 when it is zero", cite PS4 `0x177060`).

## Item 4: the 75 → 100 clamp

- PC readers: `receivePktCondition` `0x6033d0` (count at +104, `if > 0x64 → 100`, stored back,
  loop `while i < stored count`) and CREATE_CONTEXT `0x601b80` (count at +244, same). Entries read
  = the clamped count. Each entry is two bytes; the first byte's top 3 bits are clamped to 6 as a
  value. **V**
- PS4 `0x177060` clamps to 75 the same way. **V**
- PC sender `0x893160` writes the count `sub_476810(ctx)` and that many entries with no clamp at
  the send site (whether the source container is bounded by 100 was not read). **V / not run**
- Pattern: `min(n, 100)` in `Condition` and `SetCreateContext` is right; it mirrors the client. A
  message with n > 100 would leave trailing bytes for the client too, so no further change.

## Item 5: SetNormal, ToolNormal, ToolEasy

- Decoders (receive, slot 9): SetNormal `0x895d00` → SetBase `0x5ff2c0` (allocates 4 bytes, reads
  nothing) + SetNormal `0x5ff2e0`; ToolEasy `0x895fd0` → ToolBase `0x5ff3c0` (reads nothing) +
  ToolEasy `0x5ff3e0`; ToolNormal `0x896040` → ToolBase `0x5ff3c0` + ToolNormal `0x5ff480`
  (reads nothing). **V** (settles P2's "I" on the three stubs.)
- SetNormal jump table `0x5ff39c` (id − 2, 7 entries): 2 `0x602900`, 3 `0x601ab0`, 4 `0x602770`,
  5 `0x602670`, 6 `0x6029a0`, 7 `0x602810`, 8 `0x601b80`. ToolEasy table `0x5ff468` (id − 4):
  4 `0x6008d0`, 5 `0x600820`, 6 `0x600430`, 7 `0x600460`. Both match the include. **V**
- Senders (slot 8): SetNormal `0x895d70` accepts ids 2-8 and writes no body (jump table
  `0x895da4` sends every id to `return 1`); ToolNormal `0x8960e0` writes no body; ToolEasy
  `0x8960b0` writes no body and refuses ids 5-7. `sub_88e4b0` only creates the coder. **V**
- PS4 is the same: `cNetMsgSetNormal::sendMessage` `0x38b6b0`, `cNetMsgToolNormal::sendMessage`
  `0x38bb20`, `cNetMsgToolEasy::sendMessage` `0x38bca0` return after `sendMessageCore`;
  `cNetSet::sendNetMessage` `0x3927a0` adds only the Head. **V**
- So the client never serialises SetNormal or ToolEasy bodies: any body on the wire comes from
  another sender, probably the server (**I**). The patterns can cover them only from the decoders,
  which they already do.

Pattern change: none to the layouts. Change the include's note "ToolBase and ToolNormal read
nothing (PS4; not checked on PC)" to "checked on PC (`0x5ff3c0`, `0x5ff480`)".

## Item 6: send methods vs decoders

- Slot 8 is the send method and slot 9 the receive method in every nNetMsg vtable (CtrlBase
  `0x891750`/`0x88e9f0`, CtrlAction `0x8912a0`/`0x88e990`, GameNormal `0x895500`/`0x8949d0`,
  GameEasy `0x8950f0`/`0x894560`, SetNormal `0x895d70`/`0x895d00`, ToolNormal `0x8960e0`/`0x896040`,
  ToolEasy `0x8960b0`/`0x895fd0`). **V**
- CtrlAction include order, sender `0x8912a0` vs decoder `0x5feac0`: identical except at the end.
  Sender: ENEMYWAITTING, ENEMYSTARTWAIT, DAMAGE_ACT (0x80000, `0x8935d0`), CORE_POINT (0x400000,
  `0x893580`), WALL_CLIMB, STATE_LIVE. Decoder: ENEMYSTARTWAIT, CORE_POINT, DAMAGE_ACT, WALL_CLIMB.
  The PS4 mismatch (P1) is present on PC too. **V**. No entry of the include table
  (`createIncludePacketCtrl`, include lines 248-274) sets both bits, so it never affects a message
  (**V** from the table).
- KILLAREA and SAFE_POS are sent only when `[ebp+0x19D8] & 0x10` (the third bool, mIsHuman), as the
  include reads them. **V**
- Condition: sender `0x893160` and decoder `0x6033d0` use the same branches (u32 HP for
  enemy/large enemy; u16, u16, u32 for human; u16 otherwise). **V**
- CatchRequest sender `0x891d10` matches decoder `0x5fff80` field for field. **V**
- CaughtResult sender (case 31/32 `0x891f60`), GameEasy and the other per-id writers were not
  compared (budget).

## Item 7: packet names from PC-side evidence

PC handler table for group 35 (initializer `0x1a2a4d0`; entry = handler pointer, 8 zero bytes, key
`(sub<<16)|id` at +0x10; base `0x212bc68`) holds S2C keys (0,2) (0,16) (1,2) (1,16) (2,2) (2,16)
(3,2) (3,16) (4,2) (4,16) (7,2) (10,2) (10,16) (11,16) (12,16) (13,16) (14,16) (15,16). C2S writers
were found among the 658 `nUserSession::CPacket::WritePacket` `0x8bcbb0` call sites from the
pushed `(packet, group, id, sub, -1)`.

| Packet | PC evidence | Name | Mark |
| --- | --- | --- | --- |
| 35.5.16 | C2S writer `0x824900` (`WritePacket(0x23,5,0x10)` + `Write_u32(value)`), called only by `0x87d350`: connection status 4, `isLoginSuccessPrivate`, `(cond − 4097) <= 0x1E`, send `cond − 4097`. PS4 `cNetGameServer::sendBadStatusNotice` `0x363df0` has the same code and calls `cSeedGameSvConnection::Send_C2S_CHARACTER_START_BAD_STATUS_NOTICE` `0x19c88b0` (one u32). | **C2S_CHARACTER_START_BAD_STATUS_NOTICE**, by caller code match (not by number) | V match |
| 35.8.16 | C2S writer `0x824ba0` (`WritePacket(0x23,8,0x10)` + `Write_CDataContextSetBase`), called from `0x87c3e0` on the non-additional branch; 35.9.16 `0x824c80` on the additional branch. PS4 `cNetGameServer::reqSetContext` `0x363440`: `isAdditional` → `Send_C2S_SET_CONTEXT_NOTICE`, else `Send_C2S_SET_CONTEXT_BASE_NOTICE` `0x19c7ab0`. | **C2S_SET_CONTEXT_BASE_NOTICE** (and 35.9.16 = C2S_SET_CONTEXT_NOTICE) | V match |
| 35.12.16 | S2C only: table key 0x0010000C → `0x7d0060`; packet class ctor `0x787210` (group 35, id 12, sub 16). It reads a CDataContextSetBase (`0x760400`) plus a second 200-byte structure (`0x760480`, ctor `0x783270`), runs the session check `sub_897ec0(…,1,0x90000)`, applies the base (`0x850010`, also used by 35.11.16 and 35.13.16) and stores the second structure keyed by UniqueId (`0x843990`). No name string. PS4 has two SET_CONTEXT notices; PC has three (11, 12, 13). | **unresolved** (a Season 3 SET_CONTEXT notice variant, I) | V shape |
| 13.44.16 | C2S writer `0x82c2b0` (one u32), via `0x604ee0` from `0x96d610`: for a bad-status condition `(c & 0xF000) == 0x1000` when the character is not a player (`sub_41dbd0` true). | **unresolved** | V direction |
| 13.45.16 | C2S writer `0x82c1d0` (one u32), via `0x604e20` from `0x96d5a0` (same test, other event). | **unresolved** | V direction |
| 13.46.16 | C2S writer `0x841200`/`0x82b720`: u32, u8, u32, u32 value, u32, u32; reached from `0x604e40`/`0x96d610` for a player character (`+6616 & 2` or `+6617 & 4`). | **unresolved** | V direction |
| 13.47.16 | C2S writer `0x841170`/`0x82b650`, same body; reached from `0x604d80`/`0x96d5a0`. | **unresolved** | V direction |
| 63.11.16 | C2S writer `0x826270` (`WritePacket(0x3F,0x0B,0x10)`, empty body), called from `0xe6e440` after the same connection/login checks. | Direction **C2S**; name **unresolved** | V |

PS4 02020005 has no caller matching 13.44-13.47 (the only `sendBadStatusNotice` callers are
`cOcdWetHuman`/`cOcdBadOilHuman` init): Season 3 additions (I). Which of each pair is "start" and
which "end" was not settled (callers `0x8a2670` and `0x8a1d5a` not read).

## Item 8: server disagreements met

- `PacketId.cs:2013` (from the brief, lead only): field `C2S_63_11_16_NTC`, Name `S2C_63_11_16_NTC`,
  `PacketSource.Server`. The PC client writes 63.11.16 (`0x826270`), so Name and PacketSource
  disagree with the client; the field name agrees.
- The withdrawn P4 claim (35.5.16 = CHARACTER_START_BAD_STATUS by PS4 number) now holds by caller
  code match; the earlier reasoning stays invalid.
- No other server file was opened; other disagreements were not checked.

## Pattern changes (for the implementer; this report edits nothing)

1. `CtrlAction` 0x3D: `u32 unk_0x3D` → `s32` (signed delta, item 1).
2. `GameNormal` 0x11 and 0x12: make the u32 optional (empty body when `sGame+0x74` is null).
3. `GameNormal` 0x0F: drop "inferred" from the two UID comments (V, item 2).
4. Comments only: second catch triple roles on CatchRequest, CatchInfo, SetCreateContext; CREATE_CONTEXT
   comment (item 3); ToolBase/ToolNormal checked on PC (item 5); CtrlAction sender order note
   holds on PC and never matters (item 6).
5. Packet names, if the packet patterns carry them: 35.5.16 C2S_CHARACTER_START_BAD_STATUS_NOTICE,
   35.8.16 C2S_SET_CONTEXT_BASE_NOTICE, 35.9.16 C2S_SET_CONTEXT_NOTICE; 63.11.16 direction C2S.
   35.12.16 and 13.44-13.47.16 stay unnamed.

## Left for the live phase

- Meaning of the CtrlAction 0x3C array and the 0x3D gauge, and which enemy `uEm024000` is.
- Meaning of the sEnemyManager +0xDB0 block (GameNormal 0x0F/0x10) and of cContextInstPl
  +0x3A90/+0x3A94 (0x11/0x12); who requests these messages.
- Whether SetNormal/ToolEasy bodies ever reach the client, and from whom (server-sent, I).
- Names of 35.12.16 and 13.44-13.47.16; start/end pairing of 13.44/13.45 and 13.46/13.47; the
  trigger of 63.11.16 (`0xe6e440`).
- Role of the second catch triple in CreateContext (consumer not read).
- Static leftovers not run in budget: the CaughtResult/GameEasy sender-vs-decoder comparison, the
  bound of the Condition source container, the second structure read by `0x760480`.
