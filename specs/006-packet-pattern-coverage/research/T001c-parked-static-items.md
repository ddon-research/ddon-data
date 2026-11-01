# T001c: spec 005's parked static items

Brief: `specs/006-packet-pattern-coverage/briefs/T001c-parked-static-items.md` (committed at
3220180465). Base 0e06e13453. This report edits nothing else; pattern changes are listed for the
implementer.

## What ran

- PC 03040008 (Season 3 truth): private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t001c/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (`bash research/ida/private-copy.sh pc t001c`), ida-mcp instance `73cd5e8b3a95`;
  `idc.get_idb_path()` returned that path, 32-bit, image base `0x400000`.
- PS4 02020005 (seed, symbols): private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t001c/DDOORBIS.elf.i64`
  (`... ps4 t001c`), instance `f2907269813d`; 64-bit, image base `0`. PS4 DWARF types read with
  `ida_typeinf` in that database.
- Read-only: Hex-Rays, forced disassembly of undefined bytes (`ida_ua.decode_insn` +
  `generate_disasm_line(..., GENDSM_FORCE_CODE)`, no function creation), xrefs, byte searches,
  switch tables (`calc_switch_cases`). No rename, retype, comment, reanalysis or save.
- PS4 recompilation C++ (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/`): read with `rg`/`sed`
  for every matched PS4 function and type (cited per item). Server C#: not opened (lead only; the
  existing pattern comments quote its names).
- Captures: `packets/decrypted_raw`, body from file offset 9 (P4 section 1 framing). Scripts in the
  session scratchpad (`walk13.py`, `walkqe.py`, Python `struct`, run with `python -X utf8 -I`).
- Address basis: IDA VA in each database. PC names that already exist in the PC database
  (`cQuestTask::setEnemyInfoParam`, `nPacket::Read_CDataQuestEnemyInfo_`, ...) are cited as names
  only; every identification below rests on code or on strings in the PC binary.
- Marks: **V** = read in IDA (PC unless "PS4"); **I** = inferred; **C** = contradicts the source named
  in the row; **PC-cap** = from 03040008 captures.
- Sam's rules applied: no PS4 packet number used; widths read from the PC readers/writers (and from
  pushed immediates where IDA's argument recovery mattered: 13.46/13.47 call sites); PS4 matches by
  code only.

## Item 1: 35.12.16, the second structure (`0x760480`, ctor `0x783270`)

Reader `0x8054d0` (called by handler `0x7d0060`): CDataContextSetBase (`0x760400`), then `0x760480`
into the 200-byte object built by `0x783270` (vtable `off_1BC2478`). V.

`0x760480` reads, in this order (V): u64 x 10 (+8..+80), u64 +88, +96, +104, +112, +120,
list `0x76fb30` (+128), list `0x76fc20` (+148), u32 +168, u32 +172, u16 +176, u16 +178, u16 +180,
u8 +182, then `0x757e60` (+184).

- `0x76fc20` (left undecompiled by P4): u32 count, then per element u8, u8 (element vtable
  `off_1BC23B8`). It is the reader SetAdditional `0x75ff30` uses for OcdImmuneLv (+200 there). V
- `0x757e60` (count "not read" in P4): **fixed u32[4]**, no count on the wire (loop `v3 >= 4`). It is
  the same reader SetAdditional uses for its trailing Season 3 u32[4] (+724). V

**Field names**: the stored object is applied by `0x850b30` (from enemy init `0xcfa080`, a virtual
shared by about 90 enemy vtables at `0x1cbe7d4`-`0x1cf245c`, I: uEnemy) through the same setters
the SetAdditional apply `0x850010` uses, so each field takes its SetAdditional name (PS4 DWARF
`CDataContextSetAdditional`) by shared setter (V for the setter identity, names from PS4 DWARF):

| Wire # | Type | 0x760480 slot | Setter in `0x850b30` | Same setter in `0x850010` (SetAdditional slot) | Name |
| --- | --- | --- | --- | --- | --- |
| 1 | u64[10] | +8 | `0x47a770` (loop i<10; `0x47aaa0` if <= 0) | +80 | m_ullHp[10] |
| 2 | u64 | +88 | `0x479df0` | +560 | m_ullEnemyBitCtrlCollision |
| 3 | u64 | +96 | `0x479d90` | +576 | m_ullEnemyBitCtrlParts |
| 4 | u64 | +104 | `0x47a2f0` | +584 | m_ullEnemyBitCtrlWorkRate |
| 5 | u64 | +112 | `0x479ff0` | +592 | m_ullEnemyBitCtrlScale |
| 6 | u64 | +120 | `0x479e50` | +600 | m_ullEnemyBitCtrlMontage |
| 7 | list {u8,u8} `0x76fb30` | +128 | `0xbbc560` + `0x47b460` | +180 | m_OcdActiveList |
| 8 | list {u8,u8} `0x76fc20` | +148 | `0x476750` + `0x47b460` | +200 | m_OcdImmuneLvList |
| 9 | u32 | +168 | `0x479eb0` | +608 | m_unEnemyBitCtrlSyncBit |
| 10 | u32 | +172 | `0x47bf90` | +704 | m_unStateLive |
| 11 | u16 | +176 | `0x47c110` | +160 | m_usUseRegionBit |
| 12 | u16 | +178 | `0x479980` | +176 | m_usCommonWork |
| 13 | u16 | +180 | `0x479a10` | +178 | m_usCustomWork |
| 14 | u8 | +182 | `0x479f50` | +568 | m_ucEnemyCtrlRegionSelectNo |
| 15 | u32[4] | +184 | `0x479fd0` (i<4), only if the target context's DTI name equals `dword_217E828` | +724 (SetAdditional `unk_u32[4]`) | Season 3, unnamed |

`dword_217E828` is the name field of `dti__469`, whose initializer `0x19ead20` pushes
"cContextInstEm": the u32[4] applies only to enemy contexts (V). `0x479fd0` is also the CtrlAction
0x3C apply (P5 item 1), so SetAdditional `unk_u32[4]`, this u32[4] and CtrlAction `unk_0x3C[4]` are
one enemy-context array at `cContext + 0xC48` (V).

The packet therefore carries an enemy status snapshot (HP, OCD state, enemy bit-control, state)
keyed by SetBase.UniqueId; `0x843990` caches it in the map at `this + 0xA184`, and `0x850b30`
applies it when that enemy initializes (`0xcfa080`, guarded by `0x875bb0`, which checks the map)
(V for the data flow; the reading "snapshot for an enemy spawned later" is I). PS4: no
counterpart (no PS4 type with this field subset; no PS4 handler); recompilation: no such class.
Name of the packet: unresolved (no PC string).

Body size: 28 (SetBase) + 159 + 2 x (OcdActive n + OcdImmuneLv n) bytes. Captures: 0 files with
suffix `35_12_16` (`fd -e 35_12_16 | wc -l` = 0): no walk possible.

**Pattern change** (`S2C_CONTEXT_35_12_16_NTC-pattern.cpp`, `include/Context.hexpat`): add a
struct (name I, e.g. `CDataContextEnemyStatus`) and decode fully:

```
u64 m_ullHp[10]; u64 m_ullEnemyBitCtrlCollision; u64 m_ullEnemyBitCtrlParts;
u64 m_ullEnemyBitCtrlWorkRate; u64 m_ullEnemyBitCtrlScale; u64 m_ullEnemyBitCtrlMontage;
u32 ocdActiveCount; CDataOcdActive m_OcdActiveList[ocdActiveCount];
u32 ocdImmuneLvCount; CDataOcdImmuneLv m_OcdImmuneLvList[ocdImmuneLvCount];
u32 m_unEnemyBitCtrlSyncBit; u32 m_unStateLive; u16 m_usUseRegionBit; u16 m_usCommonWork;
u16 m_usCustomWork; u8 m_ucEnemyCtrlRegionSelectNo; u32 unk_u32[4];
```

then the standard fit tail; `decoded = true`. Names: "by shared setter with SetAdditional (T001c 1)".
In SetAdditional, comment `unk_u32[4]`: "enemy-context array cContext+0xC48, applied only to
cContextInstEm (`0x850010`/`0x479fd0`); same array as CtrlAction 0x3C".

## Item 2: readers never decompiled (35.0.2, 35.1.x, 35.2.x, 35.4.x)

Handlers from the group-35 table (P4 2.1). 35.1.16 `0x7cf570` decompiles as `__noreturn` (IDA
mis-analysis); its reader was read from the disassembly (`call sub_805140` at `0x7cf5f6`). V for all:

| Packet | Handler | Reader | Body (PC wire order) | PS4 type (DWARF) |
| --- | --- | --- | --- | --- |
| 35.0.2 GET_LOBBY_PLAYER_CONTEXT_RES | `0x7cf250` | `0x804fb0` -> `0x76d6a0` | s32 Error [, s32 Result, u32 CharacterID, ContextBase `0x75f250`, PlayerInfo `0x75f930`, EditInfo `0x764550`] | `CPacket_S2C_GET_LOBBY_PLAYER_CONTEXT_RES`: m_Context `CLobbyContextPlayer` {Base, PlayerInfo, EditInfo} |
| 35.1.2 PARTY_PLAYER RES | `0x7cf830` | `0x8051b0` -> `0x771280` | s32 Error [, s32 Result, u32 CharacterID, Base, PlayerInfo, **Resist `0x75fcc0`**, EditInfo] | `CPartyContextPlayer` {Base, PlayerInfo, m_ResistInfo, EditInfo} |
| 35.1.16 PARTY_PLAYER NTC | `0x7cf570` | `0x805140` -> `0x771280` | u32 CharacterID, Base, PlayerInfo, **Resist**, EditInfo | same (NOTICE: m_unCharacterID, m_Context) |
| 35.2.2 ALL_PLAYER RES | `0x7cefd0` | `0x804e80` -> `0x758d10` | s32 Error [, s32 Result, u32 CharacterID, Base, PlayerInfo, **Resist**, EditInfo] | `CAllContextPlayer` {Base, PlayerInfo, m_ResistInfo, EditInfo} |
| 35.2.16 ALL_PLAYER NTC | `0x7cee70` | `0x804e10` -> `0x758d10` | u32 CharacterID, Base, PlayerInfo, **Resist**, EditInfo | same |
| 35.4.2 PARTY_RENTED_PAWN RES | `0x7cfa20` | `0x8052b0` -> `0x771200` | s32 Error [, s32 Result, u32 PawnID, Base, PlayerInfo, PawnInfo `0x75f8d0`, Resist, EditInfo] | `CPartyContextPawn` {Base, PlayerInfo, PawnInfo, Resist, EditInfo}; RES field m_unPawnID |
| 35.4.16 PARTY_RENTED_PAWN NTC | `0x7cf910` | `0x805240` -> `0x771200` | u32 PawnID, Base, PlayerInfo, PawnInfo, Resist, EditInfo | same |
| (35.3.2 PARTY_MYPAWN RES, for completeness) | `0x7cf480` | `0x8050b0` -> `0x771200` | as 35.4.2 | — |

- **C**: P4 § 2.3 row 1 says 35.1.16/35.2.16 equal 35.0.16 ("I by PS4 type identity"). The PC readers
  and the PS4 DWARF agree that Party/All add `CDataContextResist` (30 x u8) between PlayerInfo and
  EditInfo; only the Lobby variant lacks it.
- `0x771280` and `0x758d10` decompile identically (two copies of the same reader). The nested readers
  are the ones already in `include/Context.hexpat` (Base, PlayerInfo, PawnInfo, Resist, EditInfo),
  so no field table changes. RES: `s32 Error`, the rest only if Error == 0 (as P4 § 1).
- Recompilation: these packet classes have no definition in
  `recompilation/src/DD_ONLINE/prog/Protocol/` (`rg` for `PARTY_PLAYER_CONTEXT`, `CDataPartyContext*`:
  only `cNetGameServer.*` mentions); the PS4 DWARF types above are the cross-check.
- Captures: 0 files for each of `35_0_2 35_1_2 35_1_16 35_2_2 35_2_16 35_4_2 35_4_16` (count with
  `fd -t f -e <suffix> . | wc -l`; method checked on `35_0_16` = 264). No walk possible.

**Pattern change** (only if these packets get patterns): add to `include/Context.hexpat`
`CDataLobbyContextPlayer {Base; PlayerInfo; EditInfo}`, `CDataPartyContextPlayer` and
`CDataAllContextPlayer {Base; PlayerInfo; CDataContextResist m_ResistInfo; EditInfo}`,
`CDataPartyContextPawn {Base; PlayerInfo; PawnInfo; Resist; EditInfo}` (PS4 names). Fix the
35.0.16 pattern comment only if it claims 35.1/35.2 share its body.

## Item 3: start/end pairing of 13.44/13.45 and 13.46/13.47

Chain (V): writers 13.44 `0x82c2b0` (`WritePacket(0xD,44,0x10)` + u32), 13.45 `0x82c1d0`
(`(0xD,45,0x10)` + u32), 13.46 `0x82b720` -> `0x841200` (`(0xD,46,0x10)`), 13.47 `0x82b650` ->
`0x841170` (`(0xD,47,0x10)`). Senders: `0x604ee0` -> 13.44, `0x604e40` -> 13.46 (both from
`0x96d610`); `0x604e20` -> 13.45, `0x604d80` -> 13.47 (both from `0x96d5a0`).

- `0x96d610` is called only from `0x8a2670` (at `0x8a2796`), `0x96d5a0` only from undefined code at
  `0x8a1d5a` inside the routine that starts at `0x8a1c80`.
- **`0x8a2670` = PC `cOcdBase::init`** (PS4 `0x399c40`), matched by code: guard on model and OCD
  ctrl; `mOcdUID (this+288) != 4099` before the effect; `mActiveTimerRate (this+304) = 1.0f`;
  `if ((model+6616 & 8) && isMaster && initFlag && !flag(4))` -> `sub_B77200(n3_0, 2, uid, 1.0f)` =
  PS4 `sGUIExt::generateDamageUI(…, 2, mOcdUID, 1.0, …)`; then the OCD cache copy (V both).
- **`0x8a1c80` = PC `cOcdBase::final`** (PS4 `0x39a690`): ActiveTime = ActiveTimeMax
  (`+0x64 -> +0x60`), CureWaitTime (`+0x7c -> +0x78`), `uid != 0x1003` effect branch,
  `generateDamageUI(…, 3, uid, 1.0)` (`push 3` at `0x8a1d47`) (V both).
- Recompilation: `cOcdBase::init` / `final` are stubs (`cOcdBase.cpp:95`, `:130`); the match rests
  on the PS4 disassembly.

So **13.44 and 13.46 fire on status start (init); 13.45 and 13.47 on status end (final)** (V). The
server/raw-file names (START = 44/46, END = 45/47) agree.

Which pair fires for whom: PC model `+6616` (`0x19D8`) is PS4 `uDDOModel::mUnitId` (same bit test
`& 8` + isMaster gating `generateDamageUI` in init; PS4 bitfield: bit1 mIsEnemy, bit2 mIsCharacter,
bit3 mIsPlayer, bit4 mIsHuman, bit10 mIsHumanEnemy). `sub_C82BC0` (model+6656) = isMaster.
`0x96d610`/`0x96d5a0` require isMaster and `(uid & 0xF000) == 0x1000`, then:
- `mIsEnemy || mIsHumanEnemy` (`+6616 & 2`, `+6617 & 4`) -> 13.46 / 13.47;
- else `sub_41dbd0` (= isMaster && `mIsPlayer`) -> 13.44 / 13.45. (V)

**C**: P5 item 7 and the current pattern comments say 13.44 is for "a non-player character" and
13.46 "for a player character"; the code says 13.44/13.45 = own player, 13.46/13.47 = enemies the
client is master of.

Field meanings (V): 13.44/13.45 u32 = `cOcdBase::mOcdUID` (PS4 member name, `this+288` on PC).
13.46/13.47 (call sites `0x604e40`/`0x604d80`, widths from the pushes): `CDataStageLayoutId`
{u32 StageId = `convertStageNoToId(sGame stageNo)` (`0xa29c30`), u8 LayerNo = obj+0x80, u32
GroupId = obj+0x1C & 0x1FF}, u32 = obj+0x30, u32 = **constant 0** (`push 0` at `0x604eaa`/`0x604dea`),
u32 = mOcdUID. "obj" is returned by `sub_4d9e70` (model+6992), a protected thunk (it decompiles as
a call into `0x3d940e1`), so +0x30 cannot be named statically: unresolved (server: PosId, lead).
`0xbfd900` (enemy-kill path) builds the same layout id from a set-group object whose +128 is the
layer, which suggests obj is the enemy's set-group record (I).

PC-cap (`walk13.py`, all files): 13.44 19, 13.45 19 (ids 0x1004, 0x100a, 0x1010, ...); 13.46 31 and
13.47 30: field 5 = 0 in 61/61, field 6 in 0x1002-0x1010. One file:
`stream85-marked.pcapng_tcp-stream-11/103019_C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC_...13_46_16`:
`000001ea 00 00000012 00000009 00000000 0000100c` (stage id 0x1ea, layer 0, group 0x12, obj+0x30 = 9,
0, OCD 0x100c).

Names: no PC string ("BAD_STATUS" appears only in `cpOmBadStatus`, `cSetInfoOmBadStatus`), and no
PS4 function sends from `cOcdBase::init/final`: the packet names stay unresolved; the start/end
roles are V.

**Pattern change** (comments + field names; no width change):
- 13.44/13.45: "sent from cOcdBase::init (`0x8a2670`) / final (`0x8a1c80`) for the master player
  character"; `u32 m_unOcdUID` (PS4 cOcdBase::mOcdUID).
- 13.46/13.47: "init / final, for an enemy (mIsEnemy or mIsHumanEnemy) the client is master of";
  fields `u32 StageId; u8 LayerNo; u32 GroupId;` (layout id, V), `u32 unk_u32;` (set-group +0x30,
  server PosId), `u32 unk_zero;` (always 0, client constant), `u32 m_unOcdUID;`. Drop "(inferred)"
  from the status id.

## Item 4: CaughtResult and GameEasy, sender vs decoder

**CaughtResult** (ids 0x1F/0x20): CtrlAction send switch `0x8915e3` (49 cases, `calc_switch_cases`)
sends cases 31 and 32 to `0x891f60` (V). Sender writes u8 ctx+88, UID ctx+96 (`0x88e3d0` ->
`0x15b3bd0`, 8 bytes), u8 ctx+89, u8 ctx+104, UID ctx+112, u8 ctx+105 (getters `0x4746c0`,
`0x4746a0`, `0x474690`, `0x474700`, `0x4746e0`, `0x4746d0`). Decoder `0x6000b0`: u8 +912, u64 +920
(`0x15b38c0`, 8 bytes), u8 +928, u8 +936, u64 +944, u8 +952. **Match, field for field** (V).

**GameEasy** (send `0x8950f0`, undefined bytes, forced disassembly; receive `0x5ff050`):
both start with u8 mType (sender writes the message id byte `this+0x31`; decoder reads one byte).
Sender switch on id - 0x15 (table `0x8954ec`, 5 entries); ids outside 0x15-0x19 write nothing more.

| Id | Sender (V) | Decoder (V) | Result |
| --- | --- | --- | --- |
| 0x15 PRT_SET | `0x895163`: u32 count = u8 at quest-ext +0x7B0 (no clamp); per entry u32 **0** (constant), u16, u16, u8, u8, f32 x 4 (sources +0x10, +0x14, +0x18, +0x20; default of the 4th = 1.0f) | `0x600d10`: u32 count clamped to 30; per entry u32 -> +8, u16 -> +0, u16 -> +2, u8 -> +4, u8 -> +5, f32 -> +12, +16, +20, +24 (default 1.0f) | match |
| 0x16 PRT_INFO | `0x8952e1`: u64 (`0x15b3bd0`), then 5 x u8 from quest-ext +0x7D1, +0x7CF, +0x7D3, +0x24, +0x25 | `0x600be0`: u64 +16, 5 bools +24..+28 | match |
| 0x17 AREA_RELEASE | `0x8953a5`: u32 count (`0xbdb300`, no clamp), u32 each | `0x600ab0`: count clamped to 200, u32 each | match (clamp on receive only) |
| 0x18 EVENT | `0x8953f6`: 3 x u32, each **0 or 1** (bit of self member index in sEventManager +0xE4/+0xE8/+0xEC) | `0x600b40`: 3 x u32 | match |
| 0x19 NPC_MESSAGE | `0x895488`: u32 sTalkManager+0xA0, u32 QUEST_ID (`0xa360d0`), u32 sTalkManager+0xA4 | `0x600b90`: 3 x u32 | match |

PS4 DWARF `nNetMsgData::GameEasy::stPRTData` = {u16 mStageNo +0, u16 mQuestNo +2, u8 mBlockNo +4,
u8 mProcessNo +5, u32 mSetMember +8, stVector3 mPos +12, f32 mScale +24}: the PC decoder stores in
exactly these slots, so the wire order **u32 SetMember, u16 Stage, u16 Quest, u8 Block, u8 Process,
Pos.x, Pos.y, Pos.z, Scale** is V (the include's "inferred order" is settled). The PC client always
sends SetMember = 0. `stMsgGameEasyData` gives the PRT_INFO bool order (IsFinalAnswer, IsCancel,
IsAdvance, IsReady, IsReadyOK), matching the decoder slots.

**Pattern change** (`include/nNetMsg.hexpat`): drop "inferred order" on `PRTSet` floats (cite
PS4 stPRTData + PC `0x600d10`); optional comments: PRT_SET count and AREA_RELEASE count are not
clamped by the sender; EVENT bits are 0/1 flags for the sender's own member. No layout change.
Captures of group 0x41010000 messages: not walked (no layout change).

## Item 5: QuestEnemyInfo, position of the Season 3 u32

- PC reader `0x773d90`: element (16 B, vtable `off_1B2B1D8`) u32 -> +4, u32 -> +8, u16 -> +12,
  bool -> +14 (V).
- PS4 reader `0x1a186c0`: u32 -> +8, u16 -> +12, bool -> +14 (V PS4); DWARF and recompilation
  `Protocol/PacketData/Quest.h:771-775`: `u32 m_unGroupId; u16 m_usLv; b8 m_bIsPartyRecommend;`.
- Consumer, matched by code: PS4 `cQuestTask::setEnemyInfoParam` `0x54dc30` dedupes by (GroupId, Lv)
  and builds `cQuestTask::cEnemyGroupInfo` {mEnemyGroupId +8, mEnemyLevel +12, mIsPartyRecommanded
  +16}. PC `0x9d2590` allocates through `cQuestTask::cEnemyGroupInfo::MyDTI` `0x21955a4` (its DTI
  constructor `0x1a4570d` pushes the PC string "cQuestTask::cEnemyGroupInfo"): it copies element
  +4 -> +4 (mEnemyGroupId slot), u16 +12 -> +8 (mEnemyLevel), bool +14 -> +12, and **element +8 ->
  +16, a new trailing member**, and dedupes on (+4, Lv, +8) (V). Recompilation: setEnemyInfoParam is a
  stub (`cQuestTask.cpp:334`).
- Answer: **first u32 = GroupId (PS4 m_unGroupId), second u32 = Season 3** (V by consumer match).
  This contradicts P11a § 1.3 ("Season 3 u32 first") and confirms the earlier include order.
- PC-cap: `walkqe.py` on `stream1-marked.pcapng_tcp-stream-35/12006_..._11_89_16` (SHA-256 prefix
  `7bb6d7d3148f516b`): 33 WorldManage orders walked to 0x55bf, 0 EnemyInfo entries; of the 41
  `11_89_16` files, the 20 with lists 1-8 empty also carry 0 EnemyInfo entries; the other 21 have
  non-empty Tutorial/Lot lists and were not walked. No value check possible (names only, widths
  unchanged).

**Pattern change** (`include/Quest.hexpat`): `u32 GroupId;` (PS4 m_unGroupId, V by PC
`0x9d2590` / PS4 `0x54dc30`), `u32 unk_u32;` (Season 3, stored as the new trailing member of
cQuestTask::cEnemyGroupInfo, part of its dedupe key), `u16 Lv; bool IsPartyRecommend;`. Replace the
comment block at lines 285-288.

## Item 6: Season 3 nNetMsg `unk_*` names

| Field (include) | New evidence | Name | Mark |
| --- | --- | --- | --- |
| CatchRequest `unk_u64`, `unk_u8_0`, `unk_u8_1`; CatchInfo `unk_u8_0`, `unk_u64`, `unk_u8_1` | PC catch component = PS4 `cpCatchCtrl` by code: PC `0x8e72f0` = `forceCancel` (setTarget(null) `0xc849e0`, clears info at +84/+85/+86/+88/+96, writes the **first** context triple `0x4795c0`/`0x4795a0`/`0x479590`); PC `0x8e7220` = `disconnectEscape` (clears info at +132/+133/+134/+136/+144, calls `0x47aa90` = setIsCaughtResult, writes the **second** triple `0x479600`/`0x4795e0`/`0x4795d0`). PS4 `0x4550b0`/`0x456220` and recompilation `cpCatchCtrl.cpp:233`, `:321` write `mCatchInfo` and `mCaughtInfo` into the **one** PS4 triple. PC `0x8e85be` (caught path) also writes `mCaughtInfo.mCatchType | 0x80` to the second triple. | Second triple = **cpCatchCtrl::mCaughtInfo** {mCatchType, mCatchUid, mJointNo} (PS4 `cCaughtInfo`); first triple = mCatchInfo. Suggested `mCaughtType`, `mCaughtUid`, `mCaughtJointNo` (role V; the "Caught" prefix is ours, DWARF names are cCaughtInfo's members) | V |
| SetCreateContext `unk_u8_0`, `unk_u8_1`, `unk_u64` | Same shape after the PS4 catch triple. Consumer not found: no defined function reads +0x44E/+0x458/+0x460 before calling any of the six triple setters (byte search for displacements 0x44E, 0x450, 0x458, 0x460 within 100 bytes before a call: 0 hits). | caught triple by shape | I |
| CtrlAction 0x3C `unk_0x3C[4]` | Setter `0x479fd0` is shared with SetAdditional `unk_u32[4]` (`0x850010`) and 35.12.16's u32[4] (`0x850b30`), applied only to `cContextInstEm` (DTI name "cContextInstEm", `0x19ead33`); the 0x3C apply requires model `mUnitId & 2` = mIsEnemy. | enemy-context u32[4] at cContext+0xC48; name unresolved | V role |
| CtrlAction 0x3D `unk_0x3D` | P5: signed delta into slot 0 of that array for `uEm024000`. Nothing new. | unresolved; feeds `cContext+0xC48[0]` | V (P5) |
| GameNormal 0x0F, 0x10 | `sEnemyManager+0xDB0` block (`0xb551e0`, 8 callers: `0x43c380`, `0x5a12b0`, `0xcad830`, ...); no string in the callers or their callers. | unresolved; feed the sEnemyManager +0xDB0 block | V (P5) |
| GameNormal 0x11, 0x12 | `cContextInstPl+0x3A94` (setter `0x478e40`) / `+0x3A90` (getter `0x477380`, callers `0xbb0e70`, `0xbb0eb0`, `0xbb12b0`, `0xbb1300`; no strings one level up) | unresolved | V (P5) |

PS4 DWARF has none of the Season 3 nNetMsg fields (P5 item 1); the only name gained is the caught
triple, through the cpCatchCtrl match. Also V here: PC model `+0x19D8` is `uDDOModel::mUnitId`
(item 3), so the CtrlAction header bools P5 read from `[ebp+0x19D8]` bits 1, 2, 4 and
`[ebp+0x19D9]` bit 3 are mIsEnemy, mIsCharacter, mIsHuman and mIsEnemyLarge (bit 11) (I: bit
positions mapped through the PS4 bitfield, the sender itself not re-read).

**Pattern change** (`include/nNetMsg.hexpat`, comments/names): CatchRequest lines 485-487 and
CatchInfo 497-499 -> `mCaughtUid` / `mCaughtType` / `mCaughtJointNo` (cite T001c 6: PC
`0x8e7220`=disconnectEscape, `0x8e72f0`=forceCancel); SetCreateContext 832-834: same names marked
"(inferred, shape)"; `unk_0x3C`: add "same array as SetAdditional unk_u32[4] and 35.12.16 u32[4],
cContextInstEm only". No layout change.

## Summary of status

| Item | Answer | Mark |
| --- | --- | --- |
| 1 | 35.12.16 second structure fully read and named by shared setters; u32[4] fixed | V |
| 2 | 35.0.2 = Lobby (no Resist); 35.1.x/35.2.x add Resist; 35.4.x = pawn layout | V; P4 claim C |
| 3 | 13.44/13.46 = start (cOcdBase::init), 13.45/13.47 = end (final); 44/45 own player, 46/47 enemies | V; P5 actor claim C; names unresolved |
| 4 | CaughtResult and all GameEasy writers match their decoders; PRTSet float order V | V |
| 5 | QuestEnemyInfo = {GroupId, Season 3 u32, Lv, IsPartyRecommend} | V; P11a § 1.3 C |
| 6 | Second catch triple = cpCatchCtrl::mCaughtInfo; 0x3C = cContextInstEm array; rest unresolved | V / I |

Open, with reason: the 35.12.16 and 13.44-13.47 packet names (no PC string, no PS4 sender);
13.46 obj+0x30 (its getter `0x4d9e70` is a protected thunk); SetCreateContext caught-triple consumer
(not in defined code); GameNormal 0x0F-0x12 and CtrlAction 0x3D semantics (no strings): these need
the live phase.
