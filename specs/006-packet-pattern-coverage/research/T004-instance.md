# 006 T004: group 13 INSTANCE

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T004-instance.md`; the 32 uncovered group-13 rows of
`research/T001-triage.tsv` (5,617 captures). 13.44-13.47 and 13.3.2 already have patterns and are
not redone. Base `0c8761b812`. Marks: **V** verified in code (or by capture for walk results), **I**
inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t004/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t004/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays, `idautils`,
  `ida_typeinf` for DWARF structs); nothing renamed, retyped, commented, patched or reanalysed.
- PC primitives as T003 § 0, plus `nPacket::Read_f32 0x8bc520`, `Read_f64 0x8bc570` (8-byte read;
  PS4 declares the same fields `f64`), `Write_bool 0x8bcb80`, `Write_u64 0x8bcb40`, `Write_f32 0x8bc970`,
  `Write_f64 0x8bc9d0`. Pattern widths: `double`/`float`/`u64` as named.
- PC handler table (V): directory `0x1bc0110` -> group 13 `{0x212cd30, 39}`, stride 0x18, key
  `(sub<<16)|id` at +0x10; handler pointers from the initializer stores `0x1a2d72d..0x1a2dfd9`. Readers
  are the call the handler makes with the packet:

  | key | handler | reader | | key | handler | reader |
  | --- | --- | --- | --- | --- | --- | --- |
  | 13.0.2 | `0x7db4c0` | `0x80b300` | | 13.22.2 | `0x7dbc50` | `0x80b7a0` |
  | 13.5.2 | `0x7dbb60` | `0x80b710` | | 13.23.2 | `0x7db090` | `0x80b000` |
  | 13.6.2 | `0x7db750` | `0x80b480` | | **13.23.16** | `0x7db000` | `0x80af70` |
  | 13.8.2 | `0x7db8c0` | `0x80b570` | | **13.31.16** | `0x7da9c0` | `0x80ac00` |
  | 13.10.2 | `0x7db2a0` | `0x80b130` | | **13.32.16** | `0x7dab00` | `0x80ac90` |
  | 13.11.2 | `0x7db3c0` | `0x80b1d0` | | 13.39.16 | `0x7dbe30` | `0x80b8c0` |
  | 13.16.2 | `0x7dc450` | `0x80bdc0` | | 13.40.16 | `0x7dad20` | `0x80ada0` |
  | 13.17.2 | `0x7dc590` | `0x80bed0` | | **13.42.16** | `0x7dbe00` | none (reads nothing) |
  | 13.20.2 | `0x7dc1f0` | `0x80bb90` | | **13.20.16** | `0x7dc160` | `0x80bb10` |

  Other table keys, out of scope: 13.3.2, 13.9.2, 13.13-15.2, 13.18.2, 13.21.2, 13.24-27.2,
  13.29/30.16, 13.33-38.16, 13.41.16, 13.43.2. Every RES handler references its
  `cSeedGameSvConnection::OnPacket_INSTANCE_<NAME>` string; the NTC handlers have none (V).
- PC writers (C2S) are the triage `pc_va` column: `WritePacket(p, 13, id, sub, -1)` + body (V each).
- PS4 match: PS4 `CPacket_*::{Read,Write}Packet`, `Send_*` and `OnPacket_*` bodies plus DWARF
  `nUserSession::CPacket_*` members; NTCs by behaviour (callees after the read). Never by PS4 id.
- RES header (V, every RES reader below): `Read_s32` Error at `this+16`; if non-zero, Result := Error
  and return; else `Read_s32` Result, then the body. Pattern form `s32 Error; if (Error == 0) { s32
  Result; ... }`. PS4 reads `u16 m_usError, s32 m_nResult`. **PC NTC readers read no error header**
  (V: 13.20.16, 13.23.16, 13.31.16, 13.32.16, 13.39.16, 13.40.16 start with their first field); the
  PS4 NTC readers all start with `Read_u16 m_usError` (PS4-only framing).
- **Walk**: inline stdlib Python (`python -X utf8 -I - packets/decrypted_raw` heredoc from
  `D:/ddon-data`; not saved): every file under `packets/decrypted_raw/` whose name suffix is one of
  the 32 ids (`.13_<id>_<sub>`). Header check: group 13, u16 id, sub, source (0x00 C2S, 0x34 S2C).
  Body from 0x09; fit = end within the last 15 bytes, no overrun. A second pass decoded the
  Season 2 (PS4) layouts as counter-tests (§ 13). Samples `xxd -g1`; sha256 as first 16 hex digits.
  Totals: 5,617 files, header 5,617/5,617, fit 5,617/5,617, no RES with Error != 0.

Field-name sources: PS4 DWARF member (`m_` prefix dropped in the proposed pattern name) **V**; names
for Season 3 additions are Arrowgene leads, **I**.

## 1. CDataStageLayoutId (shared by 23 of the 32 ids)

PC `0x77a330` (inside RES readers) and the inline triplets of every writer/NTC reader:
`u32, u8, u32` (V). PS4 `CStageLayoutID {u32 m_unStageID, u8 m_ucLayerNo, u32 m_unGroupID}` (V);
Arrowgene `CDataStageLayoutId {StageId, LayerNo, GroupId}` agrees. Pattern: `u32 StageId; u8 LayerNo;
u32 GroupId;` (9 B). It is the struct the 13.46 pattern writes inline (T001c item 3).

## 2. 13.0.1 C2S_INSTANCE_GET_ENEMY_SET_LIST_REQ / 13.0.2 S2C_INSTANCE_GET_ENEMY_SET_LIST_RES

- PC writer `0x8415f0`: `WritePacket(p, 13, 0, 1)`, LayoutId, `Write_u8` (arg 3) (V).
- PC reader `0x80b300` ("OnPacket_INSTANCE_GET_ENEMY_SET_LIST_RES"): RES header, LayoutId (`0x77a330`),
  u8, u32, u32, list `0x76ca20`, list `0x764400`, list `0x76f450` (V).
  - `0x76ca20` element: `Read_u8`, then `0x77a1b0` = u32, u32, u32, u16, u16, u16, 7 x u8, **6 x bool**.
  - `0x764400` element: u8, u8, f64, f32, f64.
  - `0x76f450` element (`0x76f550`): u32, 22 x u16, u8.
- PS4 **V**: `CPacket_C2S_GET_ENEMY_SET_LIST_REQ::WritePacket 0x1a37040` (LayoutId, `m_ucSubGroupId`);
  `CPacket_S2C_GET_ENEMY_SET_LIST_RES::ReadPacket 0x19d7000` (via `OnPacket_S2C_GET_ENEMY_SET_LIST_RES
  0x2f3a30`): `m_LayoutId, u8 m_ucSubGroupId, u32 m_unRandomSeed, u32 m_unQuestId,
  MtTypedArray<CDataLayoutEnemyData> m_EnemyList, MtTypedArray<CDataDropItemSetInfo> m_DropItemSetList,
  MtTypedArray<CDataNamedEnemyParamClient> m_NamedparamList`.
  `CDataLayoutEnemyData {u8 m_ucPositionIndex, CDataStageLayoutEnemyPresetEnemyInfoClient m_EnemyInfo}`;
  enemy info `{u32 m_unEnemyID, u32 m_unNamedEnemyParamsId, u32 m_unRaidBossID, u16 m_usScale, u16 m_usLv,
  u16 m_usHmPresetNo, u8 m_ucStartThinkTblNo, u8 m_ucRepopNum, u8 m_ucRepopCount, u8
  m_ucEnemyTargetTypesId, u8 m_ucMontageFixNo, u8 m_ucSetType, u8 m_ucInfectionType, b8 m_bIsBossGauge,
  b8 m_bIsBossBGM, b8 m_bIsManualSet, b8 m_bIsAreaBoss, b8 m_bIsBloodEnemy}` (5 bools);
  `CDataDropItemSetInfo {u8 m_ucID, u8 m_ucMdlType, f64 m_dX, f32 m_fY, f64 m_dZ}`;
  `CDataNamedEnemyParamClient {u32 m_unId, 22 x u16 m_usRate* (Hp, HpPart, PhyAttackBase, PhyAttackEq,
  PhyDefenceBase, PhyDefenceEq, MagAttackBase, MagAttackEq, MagDefenceBase, MagDefenceEq, Str,
  GuardAtk, GuardDefBase, GuardDefEq, ShrinkDef, BlowDef, DownDef, ShakeDef, ShrinkDefPart,
  BlowDefPart, OcdDef, OcdAtk), u8 m_ucNameTypeId}`.
- **Season 3**: the enemy info gains a **6th bool after m_bIsBloodEnemy** (PC `0x77a1b0`, V; name
  `IsHighOrbEnemy` Arrowgene lead, I). Everything else equal (V).
- Wire: REQ `CDataStageLayoutId LayoutId; u8 SubGroupId;` (10 B). RES `s32 Error; if (Error == 0)
  { s32 Result; CDataStageLayoutId LayoutId; u8 SubGroupId; u32 RandomSeed; u32 QuestId;
  MtTypedArray<CDataLayoutEnemyData> EnemyList; MtTypedArray<CDataDropItemSetInfo> DropItemSetList;
  MtTypedArray<CDataNamedEnemyParamClient> NamedParamList; }` = 38 + 32a + 22b + 49c B.
- Walk: REQ 563/563, slack 13: `stream85-…-11/100295_C2S_INSTANCE_GET_ENEMY_SET_LIST_REQ_…13_0_1`
  (32 B, `eecd7a2f46c3fdb6`): `000001ea 00 00000011 00`, end 0x13. RES 667/667, slack 1-15;
  enemy list up to 10 (455 files non-empty), drop list up to 3 (34), named list **never non-empty**
  (code-only). `stream85-…-11/101607_S2C_INSTANCE_GET_ENEMY_SET_LIST_RES_…13_0_2` (80 B,
  `36bdb46c5da4c28d`): Error 0, Result 0, layout `1ea/00/12`, SubGroupId 0, RandomSeed `454ab1c9`,
  QuestId `00007634`, 1 enemy (PositionIndex 9, EnemyId `00015220`, NamedParamsId `9dc`, RaidBoss 0,
  Scale 100, Lv 100, …, bools `01 01 00 00 00 00` at 0x41), drop 0, named 0, end 0x4f.
  Counter-test with 5 bools (PS4): 654/667 fit — the 13 failures are files with enemies.

## 3. 13.1.16 C2S_INSTANCE_ENEMY_GROUP_ENTRY_NTC / 13.2.16 C2S_INSTANCE_ENEMY_GROUP_LEAVE_NTC (settled)

- PC writers `0x841310` `(13, 1, 0x10)` and `0x841370` `(13, 2, 0x10)`: LayoutId only (V).
- Settled **V by behaviour**: PC senders `0x82b8c0`/`0x82b980` <- `0x85ca70`/`0x85cac0` (connection and
  login-success guards), both called only from `0xaa78b0` (I: PC `cGroupParam::update`), which, when
  the group's kill-area state at `this+162` changes from `this+163`, calls `0x85ca70` (13.1) if the
  new state == 1 and `0x85cac0` (13.2) otherwise, followed by `sub_406F20(this+264, 1)` (list release).
  PS4 `cGroupParam::update 0x698c40` does the same: `if (v17 != mIsKillAreaInside)` it calls
  `cNetGameServer::enemyGroupEnter 0x3516a0` (-> `CPacket_C2S_ENEMY_GROUP_ENTRY_NOTICE::WritePacket 0x1a36e40`)
  when the new state `v16` (stored to `mIsKillAreaInside`) is true, else `enemyGroupLeave 0x351820`
  (-> `CPacket_C2S_ENEMY_GROUP_LEAVE_NOTICE::WritePacket 0x1a36da0`) and releases `mSetInfoList`.
  The LayoutId is built from `convertStageNoToId(stageNo)`, layer, group & 0x1FF on both.
- DWARF `{u16 m_usError, CStageLayoutID m_LayoutId}` for both. The raw-file names agree.
- Wire: `CDataStageLayoutId LayoutId;` (9 B). Season 3: none.
- Walk: 13.1.16 202/202 slack 14, `stream85-…-11/100280_C2S_INSTANCE_ENEMY_GROUP_ENTRY_NTC_…13_1_16`
  (32 B, `916092e49ea91d47`): `000001ea 00 00000011`, end 0x12. 13.2.16 184/184 slack 14,
  `stream85-…-11/101309_C2S_INSTANCE_ENEMY_GROUP_LEAVE_NTC_…13_2_16` (32 B, `6d0197a60b1874b8`):
  `000001ea 00 00000011`, end 0x12. Slack 14 > field widths: the 9-byte body rests on the code.

## 4. 13.3.1 C2S_INSTANCE_ENEMY_KILL_REQ

- PC writer `0x8413d0` (named in the database `nUserSession::CPacket_C2S_INSTANCE_ENEMY_KILL_REQ::WritePacket`;
  sender `Send_C2S_INSTANCE_ENEMY_KILL_REQ 0x82ba40`): LayoutId, u32, u32, f64, f32, f64, **bool, bool**,
  u32 (V).
- PS4 **V**: `CPacket_C2S_ENEMY_KILL_REQ::WritePacket 0x1a36ee0` (from `cNetGameServer::enemyKilled`
  <- `sSetManager::notifyEmKilled`): `m_LayoutId, u32 m_unSetId, u32 m_unInnerId, f64 m_dDropPosX,
  f32 m_fDropPosY, f64 m_dDropPosZ, b8 m_bIsNoBattleReword, u32 m_unRegionFlag`.
- **Season 3**: one bool more. PC chain `0xbfd900` -> `0x85cb10` -> `0x82ba40`: the first bool is
  `a11` = a model byte (`+7034`), the PS4 IsNoBattleReword slot (I); the second is new, `v23` = 1
  unless a live region reports a non-zero value (`sub_478D40`/`sub_475C50`, unnamed; I); RegionFlag =
  the 10-region dead mask (`isDead` loop, V both platforms).
- Wire: `CDataStageLayoutId LayoutId; u32 SetId; u32 InnerId; double DropPosX; float DropPosY; double
  DropPosZ; bool IsNoBattleReword; bool unk_bool; u32 RegionFlag;` (43 B).
- Walk: 391/391, slack 12: `stream85-…-11/100891_C2S_INSTANCE_ENEMY_KILL_REQ_…13_3_1` (64 B,
  `78bed08ad2053a98`): layout `1ea/00/11`, SetId 0x14, InnerId 0, X `c0708f8480000000`, Y `42220780`,
  Z `c0b7f17f00000000`, bools `00 01`, RegionFlag 5, end 0x34. The PS4 layout also fits (slack 13):
  the second bool rests on the PC writer.

## 5. 13.5.1 C2S_INSTANCE_GET_ITEM_SET_LIST_REQ / 13.5.2 …_RES

- PC writer `0x841790` `(13, 5, 1)`: LayoutId (V). Reader `0x80b710`: RES header, LayoutId, list
  `0x76cb40` = {u8, bool, bool, bool, bool} (V).
- PS4 **V**: `CPacket_C2S_GET_ITEM_SET_LIST_REQ::WritePacket 0x1a36c20` (LayoutId);
  `CPacket_S2C_GET_ITEM_SET_LIST_RES::ReadPacket 0x19d7270`: `m_LayoutId,
  MtTypedArray<CDataLayoutItemData> m_SetList`; `CDataLayoutItemData {u8 m_ucPosID, b8 m_bIsEmpty, b8
  m_bIsGathered, b8 m_bIsAppearEnemy, b8 m_bIsTreasurePoint}`.
- Wire: REQ `CDataStageLayoutId LayoutId;` (9 B). RES `… { s32 Result; CDataStageLayoutId LayoutId;
  MtTypedArray<CDataLayoutItemData> SetList; }` = 21 + 5n B. Season 3: none.
- Walk: REQ 118/118 slack 14, `stream85-…-11/100280_C2S_INSTANCE_GET_ITEM_SET_LIST_REQ_…13_5_1` (32 B,
  `aabee7a2bebc7624`): `000001ea 00 000000d6`, end 0x12; the 14 padding bytes hold plain text
  (`llision` + path fragment `job08`): an uncleared send buffer, not body. RES 258/258, slack 0-15, list
  up to 24: `stream85-…-11/100339_S2C_INSTANCE_GET_ITEM_SET_LIST_RES_…13_5_2` (48 B, `b9734696191efb2b`):
  Error 0, Result 0, layout `1ea/00/d4`, count 3: `{00, 00 00 00 01}`, `{01, 00 00 00 01}`,
  `{02, 00 00 00 01}` (PosId, IsEmpty, IsGathered, IsAppearEnemy, IsTreasurePoint), end 0x2d.

## 6. 13.6.1 C2S_INSTANCE_GET_GATHERING_ITEM_LIST_REQ / 13.6.2 …_RES (Season 3 changes)

- PC writer `0x841660` `(13, 6, 1)`: LayoutId, u32, `Write_cstr` (MtString) (V).
- PC reader `0x80b480`: RES header, LayoutId, u32, MtString, **bool, bool**, list `0x773060`, list
  `0x769100` (V).
  - `0x773060` element (alloc 0x34): u32, list `0x77c5a0` = {u8, u32} (**the CDataWalletPoint reader**,
    Character.hexpat), list `0x7731b0` = {u32, u16}.
  - `0x769100` element (alloc 0x18): u32, u32, u32, u32, bool.
- PS4 **V**: `CPacket_C2S_GET_GATHERING_ITEM_LIST_REQ::WritePacket 0x1a36b40` (`m_LayoutId, u32 m_unPosId,
  MT_CSTR m_wstrGatheringItemUID`); `CPacket_S2C_GET_GATHERING_ITEM_LIST_RES::ReadPacket 0x19d7330`:
  `m_LayoutId, u32 m_unPosId, MtString m_wstrGatheringItemUID, b8 m_bIsGatheringItemBreak,
  MtTypedArray<CDataGatheringItemElement> m_ItemList`; `CDataGatheringItemElement {u32 m_ulID, u32
  m_ulItemId, u32 m_ulNum}`.
- **Season 3** (V widths, I names): a second bool after IsGatheringItemBreak (Arrowgene `Unk0`); a new
  list before the item list, element `{u32 RestrictionId (I); MtTypedArray<CDataWalletPoint>;
  MtTypedArray<{u32 ItemId (I), u16 Num (I)}>}` (Arrowgene `CDataGatheringItemRestriction {RestrictionId,
  Unk1, RequiredItems}`); CDataGatheringItemElement grows to `{u32 ID, u32 ItemId, u32 Num, u32 (I:
  Quality), bool (I: IsHidden)}` (17 B).
- Wire: REQ `CDataStageLayoutId LayoutId; u32 PosId; MtString GatheringItemUID;` (15 + len B).
  RES `… { s32 Result; CDataStageLayoutId LayoutId; u32 PosId; MtString GatheringItemUID; bool
  IsGatheringItemBreak; bool unk_bool; MtTypedArray<CDataGatheringItemRestriction> RestrictionList;
  MtTypedArray<CDataGatheringItemElement> ItemList; }`.
- Walk: REQ 155/155, slack 0-8: `stream85-…-11/140024_C2S_INSTANCE_GET_GATHERING_ITEM_LIST_REQ_…13_6_1`
  (32 B, `13fa384cee902a85`): layout `28f/00/c8`, PosId 4, UID length 0, end 0x18. RES 155/155, slack
  3-14; item list up to 3 (53 non-empty); **restriction list never non-empty** (its element is
  code-only). `stream85-…-11/140027_S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES_…13_6_2` (64 B,
  `c0004f66de6b78ae`): layout `28f/00/c8`, PosId 4, UID length 0, bools `00 00`, restriction count 0,
  item count 1: `{0, 0x1d82, 1, 0, 00}`, end 0x3b. Counter-test PS4 layout: 66/155 fit (89 files
  fail, the extra bool shifts every later field).

## 7. 13.8.1 C2S_INSTANCE_GET_GATHERING_ITEM_REQ / 13.8.2 …_RES

- PC writer `0x8416e0` `(13, 8, 1)`: LayoutId, u32, **bool, u32**, list `0x77f9d0` = u32 count +
  {u32, u32} (V). Reader `0x80b570`: RES header, LayoutId, u32, list `0x769240` = {u32, u32} (V).
- PS4 **V**: `CPacket_C2S_GET_GATHERING_ITEM_REQ::WritePacket 0x1a369d0`: `m_LayoutId, u32 m_unPosId,
  MtTypedArray<CDataGatheringItemGetRequest> m_GatheringItemGetRequestList`; `CDataGatheringItemGetRequest
  {u32 m_ulID, u32 m_ulNum}`. `CPacket_S2C_GET_GATHERING_ITEM_RES::ReadPacket 0x19d7490`: `m_LayoutId,
  u32 m_unPosId, MtTypedArray<CDataGatheringItemGetRequest>`.
- **Season 3**: REQ gains `bool` + `u32` after PosId (V widths; Arrowgene `EquipToCharacter`,
  `RestrictionId`, I — RestrictionId pairs with the 13.6.2 restriction list, I). RES unchanged.
- Wire: REQ `CDataStageLayoutId LayoutId; u32 PosId; bool EquipToCharacter; u32 RestrictionId;
  MtTypedArray<CDataGatheringItemGetRequest> GatheringItemGetRequestList;` (22 + 8n B). RES `… { s32
  Result; CDataStageLayoutId LayoutId; u32 PosId; MtTypedArray<CDataGatheringItemGetRequest>
  GatheringItemGetRequestList; }` (25 + 8n B).
- Walk: REQ 51/51, slack 1-9, list up to 3 (51 non-empty):
  `stream85-…-11/140043_C2S_INSTANCE_GET_GATHERING_ITEM_REQ_…13_8_1` (48 B, `af93b9633de35db3`): layout
  `28f/00/c8`, PosId 4, bool 00, RestrictionId 0, count 1 `{Id 0, Num 1}`, end 0x27. PS4 layout: 0/51. RES 51/51, slack 6-14:
  `stream85-…-11/140046_S2C_INSTANCE_GET_GATHERING_ITEM_RES_…13_8_2` (48 B, `d2a9e0e15f5376e9`):
  Error 0, Result 0, layout `28f/00/c8`, PosId 4, count 1 `{Id 0, Num 0}`, end 0x2a.

## 8. 13.10.1 C2S_INSTANCE_GET_DROP_ITEM_LIST_REQ / 13.10.2 …_RES

- PC writer `0x8414f0` `(13, 10, 1)`: LayoutId, u32 (V). Reader `0x80b130`: RES header, LayoutId, u32,
  list `0x769100` (the 17-byte Season 3 CDataGatheringItemElement, § 6) (V).
- PS4 **V**: `CPacket_C2S_GET_DROP_ITEM_LIST_REQ::WritePacket 0x1a367d0` (`m_LayoutId, u32 m_unId`);
  `CPacket_S2C_GET_DROP_ITEM_LIST_RES::ReadPacket 0x19d76f0`: `m_LayoutId, u32 m_unId,
  MtTypedArray<CDataGatheringItemElement> m_ItemList` (12-byte element).
- **Season 3**: element +u32 +bool (as § 6).
- Wire: REQ `CDataStageLayoutId LayoutId; u32 Id;` (13 B). RES `… { s32 Result; CDataStageLayoutId
  LayoutId; u32 Id; MtTypedArray<CDataGatheringItemElement> ItemList; }` (25 + 17n B).
- Walk: REQ 88/88 slack 10, `stream85-…-11/139930_C2S_INSTANCE_GET_DROP_ITEM_LIST_REQ_…13_10_1` (32 B,
  `c9f08350d0b41110`): layout `28f/00/01`, Id 1, end 0x16. RES 88/88, slack 11-14, list up to 3 (44
  non-empty): `stream85-…-11/140492_S2C_INSTANCE_GET_DROP_ITEM_LIST_RES_…13_10_2` (64 B,
  `2711981f49445ea8`): layout `28f/00/03`, Id 2, count 1 `{0, 0x1d82, 1, 0, 00}`, end 0x33. PS4
  element: 44/88 (only the empty lists fit).

## 9. 13.11.1 C2S_INSTANCE_GET_DROP_ITEM_REQ / 13.11.2 …_RES

- PC writer `0x841560` `(13, 11, 1)`: LayoutId, u32, **bool**, list `0x77f9d0` {u32, u32} (V). Reader
  `0x80b1d0`: RES header, LayoutId, u32, list `0x769240` {u32, u32} (V).
- PS4 **V**: `CPacket_C2S_GET_DROP_ITEM_REQ::WritePacket 0x1a36660` (`m_LayoutId, u32 m_unId,
  MtTypedArray<CDataGatheringItemGetRequest>`); `CPacket_S2C_GET_DROP_ITEM_RES::ReadPacket 0x19d77a0`
  (`m_LayoutId, u32 m_unId, MtTypedArray<CDataGatheringItemGetRequest>`).
- **Season 3**: REQ gains a bool after Id (V width; name unknown, Arrowgene `Unk0`). RES unchanged.
- Wire: REQ `CDataStageLayoutId LayoutId; u32 Id; bool unk_bool; MtTypedArray<CDataGatheringItemGetRequest>
  GatheringItemGetRequestList;` (18 + 8n B). RES as 13.8.2 with `Id` for `PosId` (25 + 8n B).
- Walk: REQ 44/44, slack 5-13, list up to 3 (44 non-empty), PS4 layout 0/44:
  `stream85-…-11/139938_C2S_INSTANCE_GET_DROP_ITEM_REQ_…13_11_1` (48 B, `8e030434c883f476`): layout `28f/00/01`, Id 1, bool 00, count 2 `{0, 1}`, `{1, 1}`, end 0x2b.
  RES 44/44, slack 6-14: `stream85-…-11/140497_S2C_INSTANCE_GET_DROP_ITEM_RES_…13_11_2` (48 B,
  `bb875df115d3b17b`): layout `28f/00/03`, Id 2, end 0x2a.

## 10. 13.16.1/13.16.2 TREASURE_POINT_GET_CATEGORY_LIST and 13.17.1/13.17.2 TREASURE_POINT_GET_LIST (Season 3-exclusive, confirmed)

- No PS4 counterpart (V, by code): no PS4 symbol with `TREASURE_POINT`/`TreasurePoint` (only
  `cpOmTreasureBox`, `cSetInfoOmTreasureBox`, `cMenuTreasuresLot*`), no DWARF type of that name, and none
  of the 363 PS4 `nPacket::Read_CData*` readers has the sequence u32 count + {u32, MtString, u8|bool}
  (the two near misses, `CDataMatchingProfile` and `CDataEquipPreset`, carry other fields). The PC
  caller is a clan-dungeon GUI: the 13.16.1 sender `0x8723a0` and the 13.17.1 sender `0x872440` are both
  called from `0x987d6d`, which references `ui\uGUIClanDungeonClue`, `ui\ClanDungeonClue` and
  `clan_dungeon_clue\c%04d_n%02d` (V). No PS4 names below.
- PC writers: 13.16.1 at `0x82c710` (the IDA function starts at `0x82c70d` with 3 stray bytes; caller
  `0x8723ef`): `WritePacket(13, 16, 1)`, `Write_u32` (V). 13.17.1 `0x82c7f0`: `(13, 17, 1)`, `Write_u32`
  (`a2` = `*(obj+36)` in `0x5f49b0`) (V).
- PC readers: 13.16.2 `0x80bdc0` ("OnPacket_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES"): RES header,
  list `0x77b470` = {u32, MtString, u8} (V). 13.17.2 `0x80bed0`
  ("OnPacket_INSTANCE_TREASURE_POINT_GET_LIST_RES"): RES header, u32, list `0x77b580` = {u32, MtString,
  bool} (V).
- Wire (Season 3-exclusive; names I from Arrowgene): 13.16.1 `u32 unk_u32;` (4 B). 13.16.2 `… { s32
  Result; MtTypedArray<CDataTreasurePointCategory> CategoryList; }` with `{u32 CategoryId; MtString
  CategoryName; u8 EntryCount;}`. 13.17.1 `u32 CategoryId;` (4 B). 13.17.2 `… { s32 Result; u32
  CategoryId; MtTypedArray<CDataTreasurePoint> TreasurePointList; }` with `{u32 Index; MtString Name;
  bool unk_bool;}`.
- Walk (1 capture each, all fit): 13.16.1 `stream3-party-experiments-…-47/13359_…13_16_1` (16 B,
  `c1c9c20d13eb2b10`): `00000002`, end 0x0d. 13.16.2 `…-47/13361_…13_16_2` (160 B, `1aa31945db42fab6`):
  4 categories, ids 0x0b, 0x0d, 0x0c, 0x0e, 27-byte UTF-8 names ending 解き明かし手がかり, counts 5, 5, 5,
  3, end 0x9d. 13.17.1 `…-47/13376_…13_17_1` (16 B, `204c068feb7da4c8`): CategoryId 0x0d (one of the
  13.16.2 ids), end 0x0d. 13.17.2 `…-47/13377_…13_17_2` (240 B, `f2fb6cb14cd7c909`): CategoryId 0x0d, 5
  points, indices 0-4, names `古墳解き明かし手がかり《n》`, bools 01, end 0xe6.

## 11. 13.20.1 SET_OM_INSTANT_KEY_VALUE_REQ / 13.20.2 …_RES / 13.20.16 …_NTC (Season 3: u64 key)

- PC writer `0x82c460` `(13, 20, 1)`: `Write_u64 [a2+8]`, `Write_u32 [a2+16]` (V). Reader `0x80bb90`:
  RES header, u32 (+24), `0x76fe10` = u64 (+8), u32 (+16) (V).
- **13.20.16 settled**: PC handler `0x7dc160` -> reader `0x80bb10`: u32 (+16), u64 (+32), u32 (+40), no
  error header; then calls `sub_BBF470(&COmData)` (one argument; called only from here; a protected
  thunk into `sub_BC0B60`). PS4 `OnPacket_S2C_SET_OM_INSTANT_KEY_VALUE_NOTICE 0x2f65b0`: u16 error, u32,
  `COmData` (key, value), then `sOmManager::callBackInsSync(&data)` (called only from this handler).
  PC 13.20.2's handler, like PS4 `OnPacket_S2C_SET_OM_INSTANT_KEY_VALUE_RES 0x2f64b0`, makes no OM
  callback. Same id 20 as the SET RES, same reader shape, same one-COmData callback: **V =
  `S2C_SET_OM_INSTANT_KEY_VALUE_NOTICE`**. DWARF `{u16 m_usError, u32 m_unStageId, COmData m_Value}`.
  The triage candidate `OnPacket_S2C_GP_COURSE_START_NTC 0x30c0a0` is **rejected**: its u32/u64/u32
  feeds `sGame::setChargeCourse` (a GP course), and its shape matches only because Season 3 widened
  the OM key to u64.
- PS4 **V**: `Send_C2S_SET_OM_INSTANT_KEY_VALUE_REQ 0x19bb710` (`u32 m_ulKey, u32 m_ulValue`);
  `CPacket_S2C_SET_OM_INSTANT_KEY_VALUE_RES::ReadPacket 0x19d97a0` (`u32 m_unStageId, COmData m_Value`);
  `COmData`/`CDataOmData {u32 m_ulKey, u32 m_ulValue}`.
- **Season 3**: **Key is u64** in all OM packets (PC `Read_u64`/`Write_u64`, V). Capture values carry
  the high bit (`0x80000000_001415b3`).
- Wire: REQ `CDataOmData Data;` = `u64 Key; u32 Value;` (12 B). RES `… { s32 Result; u32 StageId;
  CDataOmData Value; }` (24 B). NTC `u32 StageId; CDataOmData Value;` (16 B).
- Walk: REQ 542/542 slack 11, `stream3-party-experiments-…-47/13207_…13_20_1` (32 B, `5c0390c9edc27ee7`):
  Key `80000000001415b3`, Value 0x2a, end 0x15. RES 559/559 slack 15, `…-47/13211_…13_20_2` (48 B,
  `6e1e33a8be8f13e1`): StageId 0x15b, same Key, Value 0x2a, end 0x21 — the u32-key (PS4) layout fits
  0/559. NTC 571/571 slack 7, `…-47/13210_…13_20_16` (32 B, `5129aa42feb7d5b0`): StageId 0x15b, same Key,
  Value 0x2a, end 0x19 (the PS4 width also fits: slack 11; the u64 rests on the PC reader and the RES).

## 12. 13.22.1 GET_OM_INSTANT_KEY_VALUE_ALL_REQ / 13.22.2 …_RES

- PC writer `0x82c110` `(13, 22, 1)`, no body (V). Reader `0x80b7a0`: RES header, u32, list `0x76fd10`
  = {u64, u32} (V); handler calls `sub_BBF4C0` (I: callBackInsSyncAll).
- PS4 **V**: `Send_C2S_GET_OM_INSTANT_KEY_VALUE_ALL_REQ 0x19bb870` (header only);
  `OnPacket_S2C_Get_OM_INSTANT_KEY_VALUE_ALL_RES 0x2f67a0`: u16, s32, u32, `Read_CDataOmData_` list ->
  `sOmManager::callBackInsSyncAll`; DWARF `{u32 m_unStageId, MtTypedArray<CDataOmData> m_Values}`.
- Wire: REQ empty. RES `… { s32 Result; u32 StageId; MtTypedArray<CDataOmData> Values; }` (16 + 12n B).
  Season 3: u64 key (§ 11).
- Walk: REQ 150/150 slack 7, `stream1-marked.pcapng_tcp-stream-35/12136_…13_22_1` (16 B,
  `73b62266a562a212`), end 0x09. RES 150/150, slack 7-15, list up to 6 (6 non-empty; PS4 width 147/150):
  `stream85-…-11/77463_…13_22_2` (48 B, `4fb9f259735820e9`): StageId 0x22f, count 1, Key
  `80000000008022f3`, Value 0x8004, end 0x25.

## 13. 13.23.1 EXCHANGE_OM_INSTANT_KEY_VALUE_REQ / 13.23.2 …_RES / 13.23.16 …_NTC

- PC writer `0x82bb40` `(13, 23, 1)`: u64, u32 (V). Reader `0x80b000`: RES header, u32, `0x76fe10`
  (u64, u32), u32 (V); handler calls `sub_BBF530(&COmData, valueOld)`.
- PS4 **V** (REQ/RES): `Send_C2S_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ 0x19bb9a0` (`COmData m_Data`);
  `CPacket_S2C_EXCHANGE_OM_INSTANT_KEY_VALUE_RES::ReadPacket 0x19d9910` (`u32 m_unStageId, COmData
  m_Value, u32 m_ulValueOld`) -> `sOmManager::callBackInsSyncExchange(&m_Value, m_ulValueOld)`.
- **13.23.16: no PS4 counterpart (V, by code)**: PS4 has no `EXCHANGE…NOTICE/NTC` handler (the full
  `OnPacket_*` list around the OM handlers `0x2f3040..0x2f7190` was read), and
  `callBackInsSyncExchange` has one caller, the RES. PC handler `0x7db000` -> reader `0x80af70`: u32,
  u64, u32, u32, no error header, then `sub_BC2220(&COmData, valueOld)`, a different thunk from the
  RES's `sub_BBF530`, same argument shape. Season 3 addition (the exchange broadcast to other
  clients). Names I by analogy with the RES (StageId, Value, ValueOld); the raw-file name is the
  server's.
- Wire: REQ `CDataOmData Data;` (12 B). RES `… { s32 Result; u32 StageId; CDataOmData Value; u32
  ValueOld; }` (28 B). NTC (Season 3-exclusive) `u32 StageId; CDataOmData Value; u32 ValueOld;` (20 B).
- Walk: REQ 44/44 slack 11, `stream3-party-experiments-…-47/13213_…13_23_1` (32 B, `55bb982e16d468c3`):
  Key `80000000001415b3`, Value 0x0c, end 0x15. RES 46/46 slack 11, `…-47/13216_…13_23_2` (48 B,
  `031591a88d100fbb`): StageId 0x15b, Key, Value 0x0c, ValueOld 0x2a, end 0x25. NTC 46/46 slack 3,
  `…-47/13215_…13_23_16` (32 B, `ef0c8c40df920efe`): identical body, end 0x1d.

## 14. 13.31.16 S2C_INSTANCE_ENEMY_GROUP_DESTROY_NTC (settled)

- PC handler `0x7da9c0` -> reader `0x80ac00`: u32, u8, u32, bool (V); then, if the stage is current,
  `sub_BFAC50(sSetManager, layout)` and, if the bool is set, `sub_B68090(…, 0, 0xA, 0xC, …)` (an
  announce).
- PS4 **V by behaviour**: `OnPacket_S2C_ENEMY_GROUP_DESTROY_NTC 0x2f41f0` reads u16, LayoutId, bool and
  calls `sSetManager::destroyEnemySetList(layout)`, then `sGUIExt::addQueueAnnounce_0(…, 0, 7, 0xC, …)`
  if the bool is set; DWARF `{u16 m_usError, CStageLayoutID m_LayoutId, b8 m_bIsAreaBoss}`. The
  announce argument differs (7 vs 0xA): Season 3 message id.
- Wire: `CDataStageLayoutId LayoutId; bool IsAreaBoss;` (10 B). Walk: 81/81 slack 13,
  `stream85-…-11/101163_…13_31_16` (32 B, `a3264e1a33b59553`): layout `1ea/00/11`, bool 00, end 0x13.
  Slack 13 > 1: the bool rests on the code.

## 15. 13.32.16 S2C_INSTANCE_ENEMY_GROUP_RESET_NTC (settled)

- PC handler `0x7dab00` -> reader `0x80ac90`: u32, u8, u32 (V); current stage -> `sub_BFE580(sSetManager,
  layout)`; other stage -> `sub_B2C150`/`sub_B2CF70` on a list (I: context enemy list get/remove).
- PS4 **V by behaviour**: `OnPacket_S2C_ENEMY_GROUP_RESET_NOTICE 0x2f43b0` reads u16, LayoutId ->
  `sSetManager::resetEnemySetList`, `sContextManager::getContextEnemytList` /
  `removeContextEnemytList`; DWARF `{u16 m_usError, CStageLayoutID m_LayoutId}`.
- Wire: `CDataStageLayoutId LayoutId;` (9 B). Walk: 130/130 slack 14, `stream85-…-11/101175_…13_32_16`
  (32 B, `e9c072c44bfaa0c6`): layout `1ea/00/11`, end 0x12.

## 16. 13.39.16 S2C_INSTANCE_POP_DROP_ITEM_NTC

- PC reader `0x80b8c0`: LayoutId, u32, u8, f64, f32, f64 (V). PS4 **V**:
  `CPacket_S2C_POP_DROP_ITEM_NOTICE::ReadPacket 0x19d7870` `{m_LayoutId, u32 m_unId, u8 m_ucMdlType, f64
  m_dPosX, f32 m_fPosY, f64 m_dPosZ}`.
- Wire: `CDataStageLayoutId LayoutId; u32 Id; u8 MdlType; double PosX; float PosY; double PosZ;`
  (34 B). Season 3: none. Walk: 74/74 slack 5, `stream85-…-11/105219_…13_39_16` (48 B,
  `b700492a0b62dd59`): layout `1ea/00/0a`, Id 1, MdlType 0, end 0x2b.

## 17. 13.40.16 S2C_INSTANCE_ENEMY_REPOP_NTC

- PC reader `0x80ada0`: LayoutId, u8, `0x77a1b0` (enemy info, 6 bools), u32 (V). PS4 **V**:
  `CPacket_S2C_ENEMY_REPOP_NOTICE::ReadPacket 0x19d7950` `{m_LayoutId, CLayoutEnemyData m_EnemyData
  (u8 m_ucPositionIndex + enemy info, 5 bools), u32 m_unWaitSecond}`.
- Season 3: enemy-info 6th bool (§ 2). Wire: `CDataStageLayoutId LayoutId; CDataLayoutEnemyData
  EnemyData; u32 WaitSecond;` (45 B).
- Walk: 41/41 slack 10, `stream85-…-11/114838_…13_40_16` (64 B, `167cf13a51434842`): layout
  `247/00/02`, PositionIndex 0, EnemyId 0x30107, NamedParamsId 0xa51, Scale 100, Lv 100, StartThinkTblNo
  1, RepopNum 0x1f, RepopCount 1, bools `00 00 01 00 00 00`, WaitSecond 0, end 0x36. The 5-bool layout
  also fits (slack 11): the 6th bool rests on the PC reader and on 13.0.2.

## 18. 13.42.16 S2C_INSTANCE_AREA_RESET_NTC (settled)

- PC handler `0x7dbe00` reads nothing: sets `*(conn+41812) = 1` and calls `sub_BD72D0(sQuestManagerExt)`
  then `sub_847390` (V). PS4 **V by behaviour**: `OnPacket_S2C_INSTANCE_AREA_RESET_NTC 0x30a350` reads
  only `u16 m_usError` (PS4 NTC framing), sets `mpManager->mIsResetInstanceArea = true` and calls
  `sQuestManagerExt::callbackInstanceAreaReset`; DWARF `{u16 m_usError}` (DTI size 16 in the
  recompilation too).
- Wire: empty body. Walk: 120/120 slack 7, `stream1-marked.pcapng_tcp-stream-35/12129_…13_42_16` (16 B,
  `159c672b34db0ab9`), end 0x09.

## 19. Summary

PS4 mark: V = confirmed by code (symbol + body, or behaviour); X = no PS4 counterpart (confirmed by
code). Body bytes for Error == 0.

| id | name (file) | PS4 match | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 13.0.1 | C2S_INSTANCE_GET_ENEMY_SET_LIST_REQ | V | 10 | 100295 | 563/563 |
| 13.0.2 | S2C_INSTANCE_GET_ENEMY_SET_LIST_RES | V (S3 enemy bool) | 38+32a+22b+49c | 101607 | 667/667 |
| 13.1.16 | C2S_INSTANCE_ENEMY_GROUP_ENTRY_NTC | V behaviour `ENEMY_GROUP_ENTRY_NOTICE` | 9 | 100280 | 202/202 |
| 13.2.16 | C2S_INSTANCE_ENEMY_GROUP_LEAVE_NTC | V behaviour `ENEMY_GROUP_LEAVE_NOTICE` | 9 | 101309 | 184/184 |
| 13.3.1 | C2S_INSTANCE_ENEMY_KILL_REQ | V (S3 bool) | 43 | 100891 | 391/391 |
| 13.5.1 | C2S_INSTANCE_GET_ITEM_SET_LIST_REQ | V | 9 | 100280 | 118/118 |
| 13.5.2 | S2C_INSTANCE_GET_ITEM_SET_LIST_RES | V | 21+5n | 100339 | 258/258 |
| 13.6.1 | C2S_INSTANCE_GET_GATHERING_ITEM_LIST_REQ | V | var (15+len) | 140024 | 155/155 |
| 13.6.2 | S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES | V (S3 bool, list, element) | var | 140027 | 155/155 |
| 13.8.1 | C2S_INSTANCE_GET_GATHERING_ITEM_REQ | V (S3 bool + u32) | 22+8n | 140043 | 51/51 |
| 13.8.2 | S2C_INSTANCE_GET_GATHERING_ITEM_RES | V | 25+8n | 140046 | 51/51 |
| 13.10.1 | C2S_INSTANCE_GET_DROP_ITEM_LIST_REQ | V | 13 | 139930 | 88/88 |
| 13.10.2 | S2C_INSTANCE_GET_DROP_ITEM_LIST_RES | V (S3 element) | 25+17n | 140492 | 88/88 |
| 13.11.1 | C2S_INSTANCE_GET_DROP_ITEM_REQ | V (S3 bool) | 18+8n | 139938 | 44/44 |
| 13.11.2 | S2C_INSTANCE_GET_DROP_ITEM_RES | V | 25+8n | 140497 | 44/44 |
| 13.16.1 | C2S_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_REQ | X (S3-exclusive) | 4 | 13359 | 1/1 |
| 13.16.2 | S2C_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES | X (S3-exclusive) | var (148) | 13361 | 1/1 |
| 13.17.1 | C2S_INSTANCE_TREASURE_POINT_GET_LIST_REQ | X (S3-exclusive) | 4 | 13376 | 1/1 |
| 13.17.2 | S2C_INSTANCE_TREASURE_POINT_GET_LIST_RES | X (S3-exclusive) | var (221) | 13377 | 1/1 |
| 13.20.1 | C2S_INSTANCE_SET_OM_INSTANT_KEY_VALUE_REQ | V (S3 u64 key) | 12 | 13207 | 542/542 |
| 13.20.2 | S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_RES | V (S3 u64 key) | 24 | 13211 | 559/559 |
| 13.20.16 | S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_NTC | V behaviour `SET_OM_INSTANT_KEY_VALUE_NOTICE` | 16 | 13210 | 571/571 |
| 13.22.1 | C2S_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_REQ | V | 0 | 12136 | 150/150 |
| 13.22.2 | S2C_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_RES | V (S3 u64 key) | 16+12n | 77463 | 150/150 |
| 13.23.1 | C2S_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ | V (S3 u64 key) | 12 | 13213 | 44/44 |
| 13.23.2 | S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_RES | V (S3 u64 key) | 28 | 13216 | 46/46 |
| 13.23.16 | S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC | X (S3-exclusive) | 20 | 13215 | 46/46 |
| 13.31.16 | S2C_INSTANCE_ENEMY_GROUP_DESTROY_NTC | V behaviour | 10 | 101163 | 81/81 |
| 13.32.16 | S2C_INSTANCE_ENEMY_GROUP_RESET_NTC | V behaviour `ENEMY_GROUP_RESET_NOTICE` | 9 | 101175 | 130/130 |
| 13.39.16 | S2C_INSTANCE_POP_DROP_ITEM_NTC | V | 34 | 105219 | 74/74 |
| 13.40.16 | S2C_INSTANCE_ENEMY_REPOP_NTC | V (S3 enemy bool) | 45 | 114838 | 41/41 |
| 13.42.16 | S2C_INSTANCE_AREA_RESET_NTC | V behaviour | 0 | 12129 | 120/120 |

Triage corrections: the seven unresolved ids are settled (13.1.16, 13.2.16, 13.20.16, 13.31.16,
13.32.16, 13.42.16 matched; 13.23.16 Season 3-exclusive); 13.20.16's candidate GP_COURSE_START_NTC is
rejected (C). 13.16.x/13.17.x stay exclusive. Capture-tested discrimination (counter-tests): PS4
layouts fail 13 of 667 (13.0.2), 89 of 155 (13.6.2), 44 of 88 (13.10.2), 51 of 51 (13.8.1), 44 of 44
(13.11.1), 559 of 559 (13.20.2), 3 of 150 (13.22.2). Code-only (fixed slack absorbs the difference):
the 13.3.1 second bool, the 13.40.16 sixth bool, the 13.20.16 u64. Never seen non-empty: the 13.0.2
NamedParamList, the 13.6.2 restriction list (and its two sub-lists). No RES with Error != 0 captured.

Recompilation (`D:/ddon-data-s2/recompilation/.../UserSession/{C2S,S2C}.cpp`): only
`CPacket_S2C_SET_OM_INSTANT_KEY_VALUE_RES::ReadPacket` (S2C.cpp:11169) and
`CPacket_S2C_EXCHANGE_OM_INSTANT_KEY_VALUE_RES::ReadPacket` (S2C.cpp:3286) have bodies; both agree with
PS4 (u32 key: Season 2). T001's `recompiled_body yes` for 13.1.16, 13.2.16, 13.10.1, 13.11.1 is a
signature on a `DDON_STUB` (C2S.cpp:92, 97, 147, 152) and for 13.10.2 a weak stub (S2C.cpp:4487):
overstated. `PacketData/Stage.h` declares the structs (members = DWARF) without reader bodies.

## 20. Shared types for pattern authors

Reuse: `Packet.hexpat` `CPacket`, `MtString`, `MtTypedArray<T>`; `Character.hexpat` `CDataWalletPoint`
(same PC reader `0x77c5a0`, V). Framing as T003 § 18 (inline RES header, `sourceOk`, fit block). The
13.46/13.47 patterns may switch their inline triplet to `CDataStageLayoutId`.

Add (V from the PC readers named; names PS4 DWARF unless marked I). Proposal: new `Instance.hexpat`
(includes Packet, Character):

| Struct | PC reader/writer | Wire |
| --- | --- | --- |
| `CDataStageLayoutId` | `0x77a330` | u32 StageId, u8 LayerNo, u32 GroupId |
| `CDataStageLayoutEnemyPresetEnemyInfoClient` | `0x77a1b0` | u32 EnemyId, u32 NamedEnemyParamsId, u32 RaidBossId, u16 Scale, u16 Lv, u16 HmPresetNo, u8 StartThinkTblNo, u8 RepopNum, u8 RepopCount, u8 EnemyTargetTypesId, u8 MontageFixNo, u8 SetType, u8 InfectionType, bool IsBossGauge, bool IsBossBGM, bool IsManualSet, bool IsAreaBoss, bool IsBloodEnemy, bool IsHighOrbEnemy (S3, I name) — 31 B |
| `CDataLayoutEnemyData` | `0x76ca20` element | u8 PositionIndex, CDataStageLayoutEnemyPresetEnemyInfoClient EnemyInfo |
| `CDataDropItemSetInfo` | `0x764400` element | u8 Id, u8 MdlType, double X, float Y, double Z |
| `CDataNamedEnemyParamClient` | `0x76f550` | u32 Id, 22 x u16 Rate* (§ 2 order), u8 NameTypeId |
| `CDataLayoutItemData` | `0x76cb40` element | u8 PosId, bool IsEmpty, bool IsGathered, bool IsAppearEnemy, bool IsTreasurePoint |
| `CDataGatheringItemElement` | `0x769100` element | u32 Id, u32 ItemId, u32 Num, u32 Quality (S3, I), bool IsHidden (S3, I) — 17 B |
| `CDataGatheringItemGetRequest` | `0x769240` / writer `0x77f9d0` | u32 Id, u32 Num |
| `CDataGatheringItemRestriction` (I name) | `0x773060` element | u32 RestrictionId (I), MtTypedArray<CDataWalletPoint>, MtTypedArray<CDataItemAmount> |
| `CDataItemAmount` (I name) | `0x7731b0` element | u32 ItemId (I), u16 Num (I); same shape as Quest `CDataRewardItem` but another reader (`0x7771b0`) |
| `CDataOmData` | `0x76fe10` / list `0x76fd10` | u64 Key (S3 width), u32 Value |
| `CDataTreasurePointCategory` (S3, I name) | `0x77b470` element | u32 CategoryId, MtString CategoryName, u8 EntryCount |
| `CDataTreasurePoint` (S3, I name) | `0x77b580` element | u32 Index, MtString Name, bool unk_bool |

## 21. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`,
`Arrowgene.Ddon.Shared/Entity/`:

1. `CDataStageLayoutEnemyPresetEnemyInfoClient`: reads/writes `RepopCount` then `RepopNum`; PS4 DWARF
   and reader order is `m_ucRepopNum` (+27) then `m_ucRepopCount` (+28). Widths agree; the two u8
   names are swapped.
2. `S2CInstanceTreasurePointGetCategoryListRes.Read`: calls `ReadEntityList<CDataTreasurePointCategory>`
   without assigning the result (the list is dropped). Wire agrees.
3. `C2SInstanceGetGatheringItemReq.EquipToCharacter`: read as `byte`; the client writes `Write_bool`
   (PC `0x8416e0`). Width agrees.
4. Not misplacements (agree with PC 03040008): `CDataStageLayoutId`, the ENEMY_GROUP entry/leave/destroy
   /reset NTCs, `C2SInstanceEnemyKillReq` (incl. `Unk0` as the second bool), `C2SInstanceGetEnemySetListReq`,
   `S2CInstanceGetEnemySetListRes` + `CDataLayoutEnemyData`, `CDataDropItemSetInfo`,
   `CDataNamedEnemyParamClient`, the 6-bool enemy info, the ITEM_SET pair + `CDataLayoutItemData`, the
   GATHERING_ITEM_LIST pair (incl. `Unk0`, `CDataGatheringItemRestriction`, 5-field
   `CDataGatheringItemElement`), the GATHERING_ITEM and DROP_ITEM pairs, the four TREASURE_POINT
   packets + their element structs, every OM packet (u64 `Key`, NTC without header), the POP_DROP_ITEM,
   ENEMY_REPOP and AREA_RESET NTCs.

## 22. Open items and checks not run

- Names without code backing (I): the Season 3 bools (13.3.1 second bool, 13.6.2 `unk_bool`, 13.11.1
  `unk_bool`, enemy-info `IsHighOrbEnemy`), the 13.8.1 `EquipToCharacter`/`RestrictionId`, the
  CDataGatheringItemElement `Quality`/`IsHidden`, the restriction element fields, the TREASURE_POINT
  field names, the 13.23.16 field names (from the RES).
- Which 13.6.2 bool is the PS4 `IsGatheringItemBreak` is I (the first, by position).
- PC sOmManager callbacks `sub_BBF470`, `sub_BBF530`, `sub_BC2220`, `sub_BBF4C0` are protected thunks
  (`sub_BC0B60`); their identity rests on call shape and the single caller each.
- ImHex not run (not on `PATH`); no pattern written (outside this package).
