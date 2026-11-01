# P4: wire format of the context, binary-save and character notice packets

Brief: `specs/005-netmsg-patterns/briefs/P4-context-binary-character.md`. Base 2a9f798b05.
Method and PC address basis as P2 (`research/P2-pc-deltas.md`).

- Build: PC 03040008 (Season 3 truth). Database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-p4/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (`bash research/ida/private-copy.sh pc p4`); `idc.get_idb_path()` returned that path, 32-bit, image
  base `0x400000`. Seed: PS4 02020005, private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-p4/DDOORBIS.elf.i64`
  (`... ps4 p4`); 64-bit, image base `0`. Both queried read-only through ida-mcp `execute_python`
  (Hex-Rays, `idautils`, `ida_typeinf` for the PS4 DWARF-derived local types). No renames,
  comments, retypes or saves.
- Address basis: IDA VA in each database. PC names such as `nUserSession::CPacket::WritePacket`,
  `nPacket::Write_CDataContextSetBase_`, `cSeedGameSvConnection::Send_C2S_SET_CONTEXT_NOTICE` are
  pre-existing names in the PC database: cited as names, not proof. PS4 names are symbols.
- Marks: **V** = read in IDA (PC unless "PS4" is said); **I** = inferred; **PC-cap** = from
  03040008 captures only; **C** = contradicts a source named in the row.
- Wire primitives (PC, as P2): integers and floats big-endian; NetPos = f64 X, f32 Y, f64 Z (20 B);
  Vec3 = 3 x f32; MtString = u16 BE length (<= 0x800) + bytes (`nPacket::Read_MtString`, V);
  list = u32 count + elements; bool = 1 byte.

> **Coordinator correction (Sam, 2026-11-01).** PS4 02020005 uses an entirely different packet id
> scheme (a flat u16 number), so a PS4 number never names a PC 03040008 packet. The per-group
> offsets in summary item 3, the 35.5.16 = CHARACTER_START_BAD_STATUS claim (§ 2.6, § 7 rows 1 and
> 13) and any other name taken from the numbering are **withdrawn as naming evidence**; those PC
> names stay unresolved. Wire layouts read from the PC writers and readers are unaffected. A PC name
> needs PC-side evidence: a handler or log string in the PC binary, or the PC caller of the
> writer matched to a PS4 symbol by code (callers, strings, data it reads), never by number.
> Open for P5 (T008): 35.5.16, 13.44-13.47.16, and the names of 35.8.16 and 35.12.16.

## 0. Summary

1. **Every group-35 S2C handler on PC was located** in the static handler table filled by
   `sub_1A2A4D0`: each entry is `{handler, ..., key at +0x10 = (sub << 16) | id}`. The keys give
   ids 0-4, 7, 10-15 (subs 2 and 16), matching DDON_RE's VAs one to one (V). The group number 35
   is I (DDON_RE + the handler-name strings below); the RES handlers pass their own name strings
   to `cSeedGameSvConnection::callOnPacketFunc`
   (e.g. "…OnPacket_CONTEXT_GET_SET_CONTEXT_RES", "…OnPacket_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES") (V).
2. **C2S writers** were found from the 658 call sites of `WritePacket` (`0x8bcbb0`,
   cdecl `(packet, group, id, sub, -1)`) by their pushed immediates (V).
3. **PS4 numbering**: PS4 does not use group/id/sub; its C2S `Send_*` write a flat u16 packet
   number. Within a group the PC (id) and PS4 numbers differ by a constant, anchored by names on
   both sides (V for the anchors, I for the rest): group 2: PC id = PS4 no. - 0x1C3 (anchors
   DOWN 0x1D0 = 2.13, POINT/GOLDEN/PENALTY_REVIVE 0x1D3-0x1D5 = 2.16-2.18 per DDON_RE, PAWN_DOWN
   0x1D6 = 2.19); group 35: PC id = PS4 no. - 0x1A2 (anchors GET_SET_CONTEXT_REQ 0x1A9 = 35.7,
   SET_CONTEXT_BASE_NOTICE 0x1AA = 35.8, MASTER_THROW_REQ 0x1AC = 35.10). Consequence: **PS4
   `C2S_CHARACTER_START_BAD_STATUS_NOTICE` (0x1A7, one u32 m_unStatusID) is 35.5.16** (I), the
   packet the server calls `C2S_CONTEXT_35_5_16_NTC`/"Unknown".
4. **Season 3 widening** confirmed for this family: CDataContextSetBase.UniqueId u32 -> u64 and a
   new trailing u32; CDataMasterInfo.UniqueId u32 -> u64; SetAdditional ActFreeWork,
   ClimbEnemyID, TargetUID, CatchTargetUID u32 -> u64 plus 4 trailing u32; PlayerInfo
   CatchTargetUID u32 -> u64 plus 2 trailing u32 (V).
5. **Captures**: all 3,654 files of the 20 captured types walk to the end within the 16-byte
   cipher padding (raw files are padded to 16; `len` is not stored, see 6). 0 failures. The PS4
   widths fail every 35.0.16, 35.7.1 and 35.11.16 capture; they do **not** fail 35.14.16 (the
   4-byte change hides in the padding) (PC-cap).
6. The server (`Arrowgene.DragonsDogmaOnline.Upstream`) agrees with the client field by field for
   every packet below; differences are listed per packet (one naming issue, one reader issue, one
   missing packet).

## 1. Capture file framing (PC-cap, = P2)

Each `packets/decrypted_raw/*.<g>_<id>_<sub>` file is: u8 group, u16 id, u8 sub, u8 source
(0x00 client, 0x34 server), u32 counter, then the body from **file offset 0x09**. Files are padded
to a multiple of 16 bytes (every size observed is a multiple of 16; padding bytes are not zero).
The walk therefore checks: no read past the file end, and file size - end in 0..15. This is a
weaker check than P2's in-payload `len`; small width errors can pass (see 0.5).

RES packets (sub 2): `s32 Error`; **only if Error == 0** a `s32 Result` follows (readers
`0x805340`, `0x8015b0`, `0x801530`, V). NTC/REQ bodies have no error header.

## 2. Group 35 CONTEXT

### 2.1 Locations

| Packet | Dir | PC VA (how) | PS4 VA / symbol | Captured |
| --- | --- | --- | --- | --- |
| 35.0.1-35.4.1 GET_*_CONTEXT_REQ | C2S | no `WritePacket(0x23, 0..4, 1)` call site on PC (V, by scan) | no `Send_` on PS4 (V, by name list) | 0 |
| 35.0.2 GET_LOBBY_PLAYER_CONTEXT_RES | S2C | handler `0x7cf250` (table key 2/0, name string), reader `0x804fb0` | `OnPacket_S2C_GET_LOBBY_PLAYER_CONTEXT_RES` `0x3256c0`, `CPacket_S2C_GET_LOBBY_PLAYER_CONTEXT_RES::ReadPacket` `0x19dcee0` | 0 |
| 35.0.16 GET_LOBBY_PLAYER_CONTEXT_NTC | S2C | handler `0x7cf0b0` (key 16/0), reader `0x804f10` | `OnPacket_S2C_GET_LOBBY_PLAYER_CONTEXT_NOTICE` `0x325f40` | 264 |
| 35.1.2 / 35.1.16 PARTY_PLAYER | S2C | `0x7cf830` / `0x7cf570` (keys 2/1, 16/1) | `0x326950` / `0x326d50` | 0 |
| 35.2.2 / 35.2.16 ALL_PLAYER | S2C | `0x7cefd0` / `0x7cee70` (keys 2/2, 16/2) | `0x327620` / `0x327a20` | 0 |
| 35.3.2 PARTY_MYPAWN_RES | S2C | `0x7cf480` (key 2/3; named `…OnPacket_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_RES`) | `0x327f00` | 0 |
| 35.3.16 PARTY_MYPAWN_NTC | S2C | handler `0x7cf330` (key 16/3), reader `0x805040` -> `0x771200` | `0x3284a0` | 9 |
| 35.4.2 / 35.4.16 PARTY_RENTED_PAWN | S2C | `0x7cfa20` / `0x7cf910` (keys 2/4, 16/4) | `0x328a10` / `0x328fb0` | 0 |
| 35.5.16 (PS4 CHARACTER_START_BAD_STATUS, I) | C2S | writer `0x8248ff` (`WritePacket(0x23,5,0x10)`) | `Send_C2S_CHARACTER_START_BAD_STATUS_NOTICE` `0x19c88b0` (no. 0x1A7) | 2 |
| 35.7.1 GET_SET_CONTEXT_REQ | C2S | writer `0x8249e0` | `Send_C2S_GET_SET_CONTEXT_REQ` `0x19c7910` (0x1A9) | 223 |
| 35.7.2 GET_SET_CONTEXT_RES | S2C | handler `0x7cfb10` (key 2/7, name string), reader `0x805340` | `OnPacket_S2C_GET_SET_CONTEXT_RES` `0x329520` | 608 |
| 35.8.16 SET_CONTEXT_BASE_NTC | C2S | writer `0x824ba0` (named `Send_C2S_SET_CONTEXT_BASE_NOTICE`) | `Send_C2S_SET_CONTEXT_BASE_NOTICE` `0x19c7ab0` (0x1AA) | 0 (not in brief; server has no id) |
| 35.9.16 SET_CONTEXT_NTC | C2S | writer `0x824c80` (named `Send_C2S_SET_CONTEXT_NOTICE`) | `Send_C2S_SET_CONTEXT_NOTICE` `0x19c7c40` | 763 |
| 35.10.1 MASTER_THROW_REQ | C2S | writer `0x824ac0`, list writer `0x77ff60` | `Send_C2S_MASTER_THROW_REQ` `0x19c8300` (0x1AC) | 0 |
| 35.10.2 MASTER_THROW_RES | S2C | `0x7cfe50` (key 2/10) | `0x32a110` | 0 |
| 35.10.16 MASTER_THROW_NTC | S2C | `0x7cfd60` (key 16/10), reader `0x76ec20` | `0x32a220` | 0 |
| 35.11.16 SET_CONTEXT_BASE_NTC | S2C | `0x7cfee0` (key 16/11), reader `0x760400` | `OnPacket_S2C_SET_CONTEXT_BASE_NOTICE` `0x329630` | 526 |
| 35.12.16 (unnamed) | S2C | `0x7d0060` (key 16/12), reader `0x8054d0` | none found (I: Season 3 addition) | 0 |
| 35.13.16 SET_CONTEXT_NTC | S2C | `0x7cffe0` (key 16/13), reader `0x805460` | `OnPacket_S2C_SET_CONTEXT_NOTICE` `0x329760` | 24 |
| 35.14.16 MASTER_CHANGE_NTC | S2C | `0x7cfba0` (key 16/14), reader `0x76ec20` | `OnPacket_S2C_MASTER_CHANGE_NOTICE` `0x329db0` | 948 |
| 35.15.16 MASTER_INFO_NTC | S2C | `0x7cfc80` (key 16/15), reader `0x76ec20` | `OnPacket_S2C_MASTER_INFO_NOTICE` `0x329f60` | 43 |

Names for 35.14/35.15/35.10.16 come from the PS4 S2C class set (MASTER_CHANGE, MASTER_INFO,
MASTER_THROW_NOTICE all `MtTypedArray<CDataMasterInfo>`) and the server; the PC handlers differ only
in the apply call (`sub_798540` / `sub_7985A0` / `sub_798600`) (V for reader, I for which name).

### 2.2 Shared structures (PC readers/writers, V)

**CDataContextSetBase** (reader `0x760400`, writer `0x77e7e0`; PS4 type `CDataContextSetBase`), 28 B:

| # | Type | PS4 name | PS4 type | Mark |
| --- | --- | --- | --- | --- |
| 1 | u32 | m_unID | u32 | V |
| 2 | **u64** | m_unUniqueID | u32 | V, PC-cap |
| 3 | s32 | m_nStageNo | s32 | V |
| 4 | s32 | m_nEncountArea | s32 | V |
| 5 | s32 | m_nMasterIndex | s32 | V |
| 6 | **u32** (new; server `Unk0`) | — | — | V |

**CDataMasterInfo** (reader in `0x76ec20`, writer in `0x77ff60`): **u64** UniqueId (PS4 u32
m_unUniqueID), u8/s8 MasterIndex (PS4 s8 m_cMasterIndex). V.

**CDataContextSetAdditional** (writer `0x77e2b0`, reader `0x75ff30`; PS4 type of the same name).
Wire order is the PS4 declaration order; only the differences are listed (all V):
ActFreeWork **u64** (PS4 u32); ClimbEnemyID **u64** (u32); TargetUID **u64** (u32); CatchTargetUID
**u64** (u32); **new trailing u32[4]** after QuestID (writer `0x77d0e0`, 4 x u32; server `Unk0`
u32 array). Fixed size apart from the two Ocd lists: 575 B + 2 x (4 + 2n). Full order:
s32 MasterIndex, bool MasterChangeFlag, NetPos Pos, f32 MoveSpeed, f32 MoveAngle, f32 AngleY,
u32 ActNo, u8 ActReqPrio, u16 ActAtkAdjustUniqueID, u64 ActFreeWork, u64 Hp[10], u16 UseRegionBit,
u64 HpWhite, u16 CommonWork, u16 CustomWork, list OcdActive {u8 OcdUID, u8 OcdActiveLv},
list OcdImmuneLv {u8, u8}, f32 EnchantRate, f32 AilmentDamage, NetPos CliffPos, Vec3 CliffNormal,
NetPos CliffStartPos, NetPos CliffStartOldPos, u64 ClimbEnemyID, s32 JointNo, Vec3 JointOffset,
u16 NodeIndex, u16 GeomIndex, u64 TargetUID, NetPos TargetPos, s32 EncountAreaBuff[3],
u32 EnemyStatusGroupNoNum, u32 EnemyStatusGroupNo[16], u32 EnemyStatusSubGroupNo[16],
u64 EnemyBitCtrlCollision, u8 EnemyCtrlRegionSelectNo, u64 Parts, u64 WorkRate, u64 Scale,
u64 Montage, u32 SyncBit, bool IsEnemyWaitting, bool IsEnemyStartWait, u64 AttackParamUIDForDmVec,
NetPos WallClimbPos, Vec3 WallClimbNormal, NetPos WallClimbLandPos, u32 StateLive, u8 CatchType,
u8 CatchJointNo, u64 CatchTargetUID, u32 QuestID, u32[4] new.

**CDataContextBase** (reader `0x75f250`; PS4 `CDataContextBase`), V; differences in bold:
s32 MemberIndex, u32 PawnId, s32 StageNo, s32 StartPosNo, NetPos Pos, f32 AngleY, u8 Sex, u8 Color,
MtString FirstName, MtString LastName, list EquipPerformance, list EquipVisual,
list EquipJobItem {u16 ItemID, u8 SlotNo} (`0x75f5d0`), bool HideEquipHead, bool HideEquipLantern,
u8 HmType, u8 PawnType, u32 CharacterId, bool SetWaitFlag, list NormalSkill {u8 SkillNo}
(`0x75f800`), list Skill {u8 SlotNo, u32 AcquirementNo, u8 AcquirementLv} (`0x75f140`),
list Ability (same), u32 AbilityCostSum, u32 AbilityCostMax, **new list {u8, u16}**
(`0x75f7e0` -> `0x7605e0`; server `EmblemStatList` of CDataEquipStatParam {EffectID, EffectValue}).

EquipData element (`0x75f480`): u16 ItemID, u8 ColorNo, u32 QualityParam (server `PlusValue`),
**list {u8, u32, u16}** (`0x765a90`; server CDataEquipElementParam SlotNo, CrestId, Add) and
**list {u8, u8, u16, u16}** (`0x765ba0`; server CDataAddStatusParam). **PS4 has one list,
CrestData {u16 m_usItemID}** (PS4 `nPacket::Read_CDataContextEquipData_` `0x19f9b70`, V PS4).

**CDataContextPlayerInfo** (reader `0x75f930`), V: same order as PS4 type; CatchTargetUID **u64**
(PS4 u32) and **two new trailing u32** after CustomWork. Lists: JobList {u8 Job, u16 Lv, u64 Exp,
u64 JobPoint} (`0x75f6c0`), ChargeEffectList {u32} (`0x75e8e0`), OcdActiveList {u8, u8}
(`0x76fb30`).

**CDataEditInfo** (reader `0x764550`): 20 x u8 and 51 x u16 in the PS4 order (u8, u8, u16
VoicePitch, 18 x u8, 50 x u16), 122 B; identical to PS4 (V by type sequence).

**Pawn part of 35.3.16** (`0x771200` = Base, PlayerInfo, `0x75f8d0`, `0x75fcc0` Resist, EditInfo):
`0x75f8d0` = list {u8, u32} (`0x772860`; PS4 CDataContextPawnInfo.m_PawnReactionList) +
**u8[64]** + **list {u8, u8}** (`0x772950`); PS4 PawnInfo has only the reaction list (V PS4 type).
Server: PawnReactionList, TrainingStatus[64], SpSkillList: agrees. Resist: 30 x u8 (= PS4
CDataContextResist, V).

### 2.3 Packet bodies

| Packet | Body (PC, wire order) | Diff vs PS4 | Mark |
| --- | --- | --- | --- |
| 35.0.16 / 35.1.16 / 35.2.16 NTC (player) | u32 CharacterID, ContextBase, PlayerInfo, EditInfo | nested widenings and new fields above | V (35.0.16 reader); 35.1/35.2 readers not decompiled (I by PS4 type identity) |
| 35.0.2 RES | s32 Error, [s32 Result, u32 CharacterID, `0x76d6a0` (context, not decompiled)] | — | V / open |
| 35.3.16 MYPAWN NTC | u32 PawnID, ContextBase, PlayerInfo, PawnInfo, Resist, EditInfo | PawnInfo extended | V |
| 35.5.16 | u32 (PS4 m_unStatusID) | none | V body, I name |
| 35.7.1 REQ / 35.8.16 C2S | CDataContextSetBase | widened | V |
| 35.7.2, 35.10.2 RES | s32 Error [, s32 Result] | none | V |
| 35.9.16 C2S, 35.13.16 S2C | SetBase, SetAdditional | widened | V |
| 35.10.1 REQ, 35.10.16, 35.14.16, 35.15.16 | u32 count, {u64 UniqueId, u8 MasterIndex} | u32 -> u64 | V |
| 35.11.16 | CDataContextSetBase | widened | V |
| 35.12.16 | SetBase, then `0x760480`: u64[10], u64 x 5, list {u8,u8} (`0x76fb30`), list (`0x76fc20`, not decompiled), u32, u32, u16, u16, u16, u8, u32 x n (`0x757e60`, count not read) | PC-only packet | V / open |

### 2.4 Walks (PC-cap; all files of the type, body from 0x09)

| Type | Files | OK | Body end (file size) | One capture |
| --- | --- | --- | --- | --- |
| 35.0.16 | 264 | 264 | varies 1206-1463 | `stream1-marked.pcapng_tcp-stream-35/12284_…35_0_16` (1376 B): CharacterID 0x1A0411 to 0x0D; ContextBase 0x0D-0x3B7 (names "Allison" "Alonza", 15 EquipPerformance, 17 entries in the new list); PlayerInfo to 0x4E4 (Job 8, Lv 120); EditInfo to **0x55E** = 1374, pad 2 |
| 35.3.16 | 9 | 9 | 1162/1177/1186 | `stream85…-11/10701_…35_3_16` (1200 B): PawnID to 0x0D, Base to 0x257 ("Helena"), PlayerInfo to 0x38F, PawnInfo to 0x40A (9 reactions, u8[64], 3 sp-skills), Resist to 0x428, EditInfo to **0x4A2** = 1186, pad 14 |
| 35.5.16 | 2 | 2 | 13 (16) | `…38736_…35_5_16`: `00000004` = 4 -> end 13 |
| 35.7.1 | 223 | 223 | 37 (48) | `…100298_…35_7_1`: `00000009` ID 9, `800000002e111ea2` UID, `0000044c` Stage 1100, `00000011` Area 17, `00000000` Master, `00000000` new -> 37 |
| 35.7.2 | 608 | 608 | 17 (32) | `…100299_…35_7_2`: Error 0, Result 0 -> 17 |
| 35.9.16 | 763 | 763 | 612 (757), 614 (6) | `…100314_…35_9_16`: SetBase 0x09-0x25 (= 35.7.1 values), Additional from 0x25: Master 0, Chg 1, Pos (47.28, 196.97, -6927.33), ActNo 0xFFFFFFFF, …, QuestID 30260, new u32[4] = 0 -> 612 (624 B) |
| 35.11.16 | 526 | 526 | 37 (48) | `…100300_…35_11_16`: ID 9, UID 0x8000000026111ea2, 1100, 17, 0, 0 -> 37 |
| 35.13.16 | 24 | 24 | 612/614 | `…116894_…35_13_16`: ID 10, Stage 1103, Area -1; new u32[4] non-zero here -> 612 |
| 35.14.16 | 948 | 948 | 22 (32) | `…100325_…35_14_16`: count 1, UID `8000000026111ea2`, MasterIndex 0 -> 22 |
| 35.15.16 | 43 | 43 | 13 (16) | `stream1…-35/12122_…35_15_16`: count 0 -> 13 (all 43 have count 0) |

The 35.9.16/35.13.16 end differs by 2 bytes = one Ocd list entry. The 35.14.16 UID equals the
35.11.16 UID (`0x8000000026111ea2`) of the same session, which supports u64 beyond the padding
check (I).

### 2.5 Relation to nNetMsg (I unless marked)

SetBase.UniqueId is u64 with the high bit set (`0x80000000_xxxxxxxx`), the same width P2 found for
CtrlBase.mUniqueId and for the u64 appended to SetNormal CREATE_CONTEXT (V for widths). SetBase
carries m_nMasterIndex and CDataMasterInfo maps UniqueId -> MasterIndex, so MASTER_CHANGE/INFO/THROW
transfer ownership of a context object by the same unique id the nNetMsg control messages use.
Not traced in code: who calls `Send_C2S_SET_CONTEXT_NOTICE` and whether the SetInfo comes from a
cNetMsgSetNormal CREATE_CONTEXT object (open).

### 2.6 Server disagreements

- 35.5.16: server `C2S_CONTEXT_35_5_16_NTC { u32 Unk0 }` — agrees on wire; PS4 numbering says it is
  CHARACTER_START_BAD_STATUS (StatusID) (I).
- 35.8.16 C2S SET_CONTEXT_BASE_NTC: the client has a writer; the server has **no PacketId** (C).
- `ReadServerResponse` (server's own reader) reads Result as **u16** when Error != 0; the client
  reads nothing after a non-zero Error, and the server writes u32 Error + u32 Result always (C,
  harmless for S2C).
- All context structures listed in 2.2 match the server serializers field by field (checked:
  CDataContextSetBase, CDataContextSetAdditional, CDataMasterInfo, CDataContextBase,
  CDataContextEquipData, CDataEquipElementParam, CDataAddStatusParam, CDataContextPlayerInfo,
  CDataPartyContextPawn).

## 3. Group 9 BINARY_SAVE

| Packet | PC | PS4 | Body | Captured / walk |
| --- | --- | --- | --- | --- |
| 9.0.1 GET_…_REQ | no writer found (V, by scan) | no `Send_` | — | 0 |
| 9.0.2 GET_…_RES | handler `0x7c68de` (name string "…OnPacket_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES"), reader `0x801530` | `OnPacket_S2C_GET_CHARACTER_BIN_SAVEDATA_RES` `0x2e8e40` | s32 Error [, s32 Result, u8[1024] (`0x757de0`)] | 0 |
| 9.1.1 SET_…_REQ | writer `0x820360` (`WritePacket(9,1,1)` + `0x77d020`: 1024 x u8), sender `0x87edd0` | `Send_C2S_SET_CHARACTER_BIN_SAVEDATA_REQ` `0x19b0650` | **u8[1024], no length prefix** | 47/47 end at 1033 (1040 B) |
| 9.1.2 SET_…_RES | handler `0x7c6a00` (name string), reader `0x8015b0` | `0x2e9060` | s32 Error [, s32 Result] | 47/47 end at 17 (32 B) |

Server `C2SBinarySaveSetCharacterBinSaveDataReq` reads a fixed 1024-byte array: agrees.
Walk `stream1…-35/26530_…9_1_1`: blob starts `00000019 00003040 0000…` (version 0x19, release
version 0x3040) and ends at 1033.

### 3.1 The save blob

Writer: PS4 `cNetGameServer::sendSetCharacterInfo` `0x342950` builds an `MtMemoryStream` of 0x800,
a `BitWriter`, calls **`cCharacterData::serialize`** `0x49740`, `BitWriter::flushBits`, and sends
the first 1024 bytes (V PS4). PC: sender `0x87edd0` calls the serializer **`sub_467790`** (this =
the character data object at `*(this + 3948)`) and flush `0x896a40` (V). Reader: the 9.0.2
handler passes the 1024 bytes on (PS4 `OnPacket_S2C_GET_CHARACTER_BIN_SAVEDATA_RES`, PC
`0x7c68de` -> `sub_466560`); the deserializer itself was not decompiled (open).

Encoding: a **bit stream**. `BitWriter::writeU32_0` (PS4 `0x38c480`) writes 4 bytes BE, or an
Elias-delta code when `mIsEliasDelta` is set; `writeU32(v, 1)` writes 1 bit; `writeU8` 8 bits.
After the first 1-bit field nothing is byte-aligned. The capture's first two u32 read as plain BE
values, so Elias-delta is off at least at the start (PC-cap).

| # | Field (PS4 name) | Bits | PC 03040008 | Mark |
| --- | --- | --- | --- | --- |
| 1 | mVersion | u32 | same | V both |
| 2 | mReleaseVersion | u32 | same | V both |
| 3 | mCheckPawnHistory[16] {u32 mPawnId, u64 mCheckDate} | 16 x 96 | same | V both |
| 4 | mQuestEtcF | u32 | same | V both |
| 5 | stTutorialGuide::writeData: mFinishTutorial[16], mLatestTutorial[5] | 21 x u32 | 16 + 5 u32 | V both |
| 6 | mJobMasterTalked, mJobMasterSkillTalked, mAreaMasterTalked, mEnteredLand | 4 x u32 | same | V both |
| 7 | mIsAppraiseTalked | 1 bit | 1 bit **+ 1 new bit** | V |
| 8 | stOptionData::serialize (`0x1960180`) | 28 bits, 16 u8 writes (12-step loop of 2 u8 for mChatChFilterSE), 1 u32 | `sub_4678F0`: **32 bits, 17 u8 writes** (12-step loop), 1 u32 | V counts; which fields are new: open |
| 9 | mChatCstmCh[2] {17 bytes, u32 mBit} | 2 x (136 + 32) | same | V both |
| 10 | — | — | **u32[16] + u32[16] new** (`this+13508`, `this+13572`) | V |
| 11 | flushBits | | same | V |

Nested classes one level deep: stTutorialGuide (row 5), stOptionData (row 8; deeper fields named
in the PS4 symbols, e.g. mIsCamRevise, mCamRangeMagic, mHeaderNameDispParty {mType, mClanName}).
A bit-level walk of the 47 blobs was not run.

## 4. Character notices (groups 2 and 13)

| Packet | PC writer (how) | PS4 | Body (PC) | Diff | Captured / walk |
| --- | --- | --- | --- | --- | --- |
| 2.13.16 CHARACTER_DOWN | `0x820c60` (`WritePacket(2,13,0x10)`, nothing else) | `Send_C2S_CHARACTER_DOWN_NOTICE` `0x19cb8a0` (0x1D0) | empty | none | 14/14 end 9 (16 B) |
| 2.14.16 CHARACTER_DOWN_CANCEL | `0x820ba0` | `0x19cb9d0` (0x1D1) | empty | none | 0 |
| 2.15.16 CHARACTER_DEAD | call site `0x820b53` (bytes not a function; immediates 2, 15, 16) | `0x19cbb00` (0x1D2) | empty (I: function not decompiled) | none | 7/7 end 9 |
| 2.19.16 PAWN_DOWN | `0x821bb0` | `0x19cbff0` (0x1D6) | u32 PawnId | none | 20/20 end 13; `…110609_…2_19_16`: `00dcb1d3` |
| 2.20.16 PAWN_DOWN_CANCEL | `0x821ad0` | `0x19cc130` (0x1D7) | u32 PawnId | none | 10/10 end 13; `…110750_…`: `00dcb1d3` (same pawn) |
| 2.21.16 PAWN_DEAD | `0x8219f0` | `Send_C2S_PAWN_DEAD_NOTICE` (0x1D8) | u32 | — | not in brief |
| 13.44.16 CHARACTER_START_BAD_STATUS | `0x82c2b0` (`WritePacket(13,44,0x10)` + u32) | not in group 13 on PS4 (PS4 has it as 35.5, see 0.3) | u32 StatusId | new id in S3 (I) | 19/19 end 13; `…102253_…`: `00001004` |
| 13.45.16 CHARACTER_END_BAD_STATUS | `0x82c1d0` (+ u32) | none | u32 StatusId | PC-only | 19/19 end 13; `…102283_…`: `00001004` |
| 13.46.16 ENEMY_BAD_STATUS_START | `0x841200` | none | u32, u8, u32 (server CDataStageLayoutId StageId, LayerNo, GroupId), u32, u32, u32 | PC-only | 31/31 end 30 (32 B); `…103019_…`: `000001ea 00 00000012 00000009 00000000 0000100c` |
| 13.47.16 ENEMY_BAD_STATUS_END | `0x841170` | none | same as 13.46 | PC-only | 30/30 end 30 |

Server: 2.x and 13.44/45 agree. 13.46/47: server names the last three u32 PosId, Unk4, Unk5; the
captures put 0x100c (= 4108, close to the 13.44 StatusId 0x1004) in the third, which suggests a
status id (I). Server PacketSource for 2.19-2.21 is `Server` though the names are C2S and the
client writes them (C, metadata only).

## 5. Open

- 35.0.2 RES context reader `0x76d6a0`, 35.1/35.2/35.4 readers, 35.12.16 lists `0x76fc20` and the
  count in `0x757e60`: not decompiled (no captures).
- 35.12.16 has no PS4 counterpart found and no server structure; name unknown.
- Bin-save blob: PC deserializer, which 4 bits and 1 u8 are new in the option data, the meaning of
  the new bit after mIsAppraiseTalked and of the two u32[16] arrays; no bit-level walk run.
- PS4 numbering offsets are inferred from anchors, not from a numbering table.
- 2.15.16 writer bytes are not a defined function; body inferred empty from its captures and PS4.
- Who builds the SetInfo sent in 35.9.16 and its link to nNetMsg CREATE_CONTEXT: not traced.
- Group number of the handler table (`0x212bc68`…) is from DDON_RE + name strings, not from the
  dispatcher.

## 6. Cross-check against the generated C++ from the PS4 DWARF

Read-only checks with `rg` in `C:/ddon-dwarf-reconstructor-rust/output_2026-11-01_031_o6_a2/` and
`D:/ddon-data-s2/recompilation/src/`, which are generated observations:
- `shared/Context.h:54-58` (reconstructor) and `DD_ONLINE/prog/Protocol/PacketData/Context.h:54-55`
  (S2 recompilation) declare `CDataContextSetBase` as u32 m_unID, **u32 m_unUniqueID**, s32 StageNo,
  s32 EncountArea, s32 MasterIndex. This is the same as the PS4 IDA local type and the PS4 writer
  (`Send_C2S_GET_SET_CONTEXT_REQ` `0x19c7910`). It confirms that the u64 width and the trailing
  u32 are Season 3 changes (V PC).
- `shared/Character.h:351` declares `CDataMasterInfo`. Its field lines were not read there; the
  PS4 IDA type is u32 m_unUniqueID, s8 m_cMasterIndex.
- `shared/cCharacterData.cpp:121` has `cCharacterData::serialize` as a stub only (`DDON_STUB`). The
  blob order in section 3.1 therefore comes from PS4 disassembly (`0x49740`), not from the
  reconstructor. `cCharacterData::deserialize` is at PS4 `0x49880`-`0x49a5c` (not decompiled).
- The other context classes (SetAdditional, ContextBase, PlayerInfo, EditInfo, EquipData) were
  compared with the PS4 IDA DWARF-derived types only, not with the reconstructor files (not run).

## 7. Server structure misplacements

Server checked: `C:/Users/morph/Documents/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Upstream`,
`Arrowgene.Ddon.Shared/...`. Every row compares the client layout (sections 2-4) with the server
text. Paths are relative to `Arrowgene.Ddon.Shared/`.

| # | Server file:line | Server says | Client does | Mark |
| --- | --- | --- | --- | --- |
| 1 | `Network/PacketId.cs:1615` | 35.5.16 = `C2S_CONTEXT_35_5_16_NTC` {u32 Unk0} (`PacketStructure/C2SContext_35_5_16_Ntc.cs:26`) | The wire format matches (PC writer `0x8248ff`: one u32). By PS4 numbering, the packet is `C2S_CHARACTER_START_BAD_STATUS_NOTICE` {u32 m_unStatusID} (PS4 `0x19c88b0`, number 0x1A7). The name is wrong or missing. | wire V; name I |
| 2 | `Network/PacketId.cs` (no entry between lines 1617 and 1618) | No packet 35.8.16 | The client has a writer `WritePacket(0x23, 8, 0x10)` + CDataContextSetBase at `0x824ba0`. PS4 has `Send_C2S_SET_CONTEXT_BASE_NOTICE` (0x1AA). | V |
| 3 | `Network/PacketId.cs:1623` | 35.12.16 has a name only and no structure file | The client reader `0x8054d0` reads SetBase, then `0x760480` (section 2.3) | V, partly |
| 4 | `Network/PacketId.cs:314-316` | 2.19/2.20/2.21 have `PacketSource.Server`, and all three use the alias `"C2S_CHARACTER_2_19_16_NTC"` | The client writes all three (`0x821bb0`, `0x821ad0`, `0x8219f0`). They are client to server, and the aliases should be 2_19, 2_20 and 2_21. | V |
| 5 | `Entity/EntitySerializer.cs:2317` | `ReadServerResponse`: Result is read as **u16** when Error != 0, otherwise u32 | The client reads s32 Error and stops when it is non-zero (`0x805340`, `0x8015b0`, `0x801530`). The server's writer (`:2310-2311`) always writes u32 + u32, so the server's own reader is inconsistent with it. | V (client) |
| 6 | `Entity/Structure/CDataMasterInfo.cs:14,22,29` | MasterIndex `sbyte`, written as one byte | The client reads and writes one byte (`0x76ec20` / `0x77ff60` via `sub_8BC830`). The width matches; whether it is signed is not determinable on the wire. | V |
| 7 | `Entity/Structure/CDataContextEquipData.cs:38,48` | `PlusValue` u32 | The width is right. PS4 calls it m_unQualityParam (PS4 type). Name only. | V |
| 8 | `Entity/Structure/CDataAddStatusParam.cs:39-42` | EnhanceType u8, Unk0 u8, EnhanceId u16, Unk1 u16 | The client reads u8, u8, u16, u16 (`0x765ba0`). This matches. | V |
| 9 | `Entity/Structure/CDataContextBase.cs:113` | trailing `EmblemStatList` of CDataEquipStatParam {u8, u16} | The client reads list {u8, u16} (`0x7605e0`). This matches, but it has no PS4 counterpart, so the name is unverified. | V wire, name I |
| 10 | `Entity/Structure/CDataContextPlayerInfo.cs:173,175-176` | `Unk0` u64 (CatchTargetUID position), `Unk1`/`Unk2` u32 | The client reads u64 CatchTargetUID, then u16 CustomWork, then u32, u32 (`0x75f930`). Widths and order match; the field at :173 is PS4 m_unCatchTargetUID and has no name in the server. | V |
| 11 | `Entity/Structure/CDataPartyContextPawn.cs:45-47` | PawnReactionList, TrainingStatus[64], SpSkillList, as flat fields | The client reads them inside one sub-reader `0x75f8d0` (PS4 CDataContextPawnInfo). Wire order and widths match. | V |
| 12 | `Entity/PacketStructure/C2SInstanceEnemyBadStatusStartNtc.cs:27-29` (and the End file) | LayoutId, PosId, Unk4, Unk5 | The client writes u32, u8, u32, u32, u32, u32 (`0x841200`, `0x841170`). The widths match. In the captures the last u32 is 0x100c, which looks like a status id (13.44 sends 0x1004). Name only. | V wire, I name |
| 13 | `Network/PacketId.cs:906-909` | 13.44-13.47 named | These have no PS4 counterpart in group 13. The PS4 CHARACTER_START_BAD_STATUS is 35.5 (see row 1). | I |
| 14 | (no file) | No structure for 9.0.2 GET_CHARACTER_BIN_SAVEDATA_RES | The client reads s32 Error [, s32 Result, u8[1024]] (`0x801530`, `0x757de0`) | V |
| 15 | `Entity/PacketStructure/C2SBinarySaveSetCharacterBinSaveDataReq.cs:29` | opaque byte[1024] | The width matches. The content is a bit stream (section 3.1) that the server does not model. | V |

Checked and no misplacement found (V, server line ranges read): CDataContextSetBase
(`Structure/CDataContextSetBase.cs:41-46`, including u64 UniqueId and Unk0), CDataContextSetAdditional
(all reads, including the u64 widenings and the Unk0 u32 array), CDataContextBase (`:87-113`),
CDataContextEquipData (`:46-50`), CDataEquipElementParam (`:34-36`), CDataContextPlayerInfo
(`:127-176`), CDataContextJobData (`:53-56`), CDataContextAcquirementData (`:37-39`),
CDataContextNormalSkillData (`:42`), CDataContextEquipJobItemData (`:45-46`), CDataOcdActive,
CDataOcdImmuneLv, CDataCommonU32, CDataPawnReaction (`:21-22`), CDataSpSkill (`:38-39`),
CDataContextResist (30 x u8), CDataEditInfo (2 u8, 1 u16, 18 u8, 50 u16), CDataLobbyContextPlayer
(`:31-33`), and the packet files for 35.0.16, 35.3.16, 35.7.1, 35.7.2, 35.9.16, 35.10.1, 35.11.16,
35.13.16, 35.14.16, 35.15.16, 35.10.16, 9.1.1, 9.1.2, 2.13/14/15/19/20 and 13.44/45.

Not checked: the server files for 35.0.2/35.1/35.2/35.4 RES and NTC beyond the shared CData
classes; CDataStageLayoutId field names; `S2CContextMasterThrowRes.cs`.
