# 006 T007: groups 8 PAWN, 58 PAWN_EXPEDITION, 53 PARTNER_PAWN

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T007-pawn-partner.md`; the 43 rows of groups 8, 58 and 53 in
`research/T001-triage.tsv` (20 + 14 + 9 ids). Base `51b6a268d6`. Marks: **V** verified in code (or by
capture for walk results), **I** inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t007/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t007/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays, `ida_ua.decode_insn`
  for linear decoding, `ida_typeinf` for DWARF structs); nothing renamed, retyped, commented, patched
  or reanalysed.
- PC primitives as T003/T005/T006 § 0 (`nPacket::Read_u8 0x8bc410`, `Read_u16 0x8bc440`, `Read_s32
  0x8bc480`, `Read_u32 0x8bc4d0`, `Read_f32 0x8bc520`, `Read_MtString 0x8bc5b0`, `Read_bool 0x8bc6e0`,
  `Read_u64 0x8bc6a0`; `Write_* 0x8bc790-0x8bcb80`; `WritePacket 0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` -> group 8 `{0x212df00, 48}`, group 53 `{0x212dab0, 10}`,
  group 58 `{0x212e380, 10}`; stride 0x18, key `(sub<<16)|id` at +0x10, handler from the initializer
  store `mov [esp], offset handler` before each entry. Every S2C `pc_va` of the triage equals its table
  handler (V, all 24).
- **Not functions in the PC database** (decoded linearly, no database change): handler `0x7ea0a0`
  (58.0.2; IDA holds it as data `dword_7EA0A0`: packet object `0x78a7e0`, reader `0x811c80`); list
  reader `0x759f80` (58.5.2: Hex-Rays shows it as `loc_759F7F+1`). 8.37.16's handler `0x7ebeb0`
  decompiles only to its first call (Hex-Rays marks `sub_407AC0` noreturn): read linearly.
- PC writers (C2S): the triage `pc_va`; `WritePacket(p, group, id, 1, -1)` with group/id read from the
  decompiled call (V each, 19/19).
- PS4 match by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, or behaviour), never
  by PS4 id.
- RES header (V, every PC RES reader here): `Read_s32` Error (+16); non-zero -> return; else `Read_s32`
  Result, body. PS4 reads `u16 m_usError, s32 m_nResult`. PC NTC readers read **no** header (V: 8.33.16
  `0x812820`, 8.34.16 `0x8126a0`, 8.35.16 `0x8128a0`, 8.36.16 `0x8127a0`, 8.37.16 `0x771580`, 53.9.16
  inline in `0x7e6d50`); PS4 NTCs start with `Read_u16 m_usError`.
- **Walk**: `specs/006-packet-pattern-coverage/research/T007-walk.py` (stdlib; run from `D:/ddon-data`
  with `python -X utf8 -I specs/006-packet-pattern-coverage/research/T007-walk.py`; it holds every PC
  layout below and the PS4 counter-test variants). Input `packets/decrypted_raw/*/`, every file whose
  suffix is `.<g>_<id>_<sub>` of the 43 ids **and** whose name contains `PAWN` or `PARTNER` (the
  suffix-only count is identical for every id: no login-server collision here). Header check: group,
  u16 id, sub, source (0x00 C2S, 0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no
  overrun. **Totals: 1,569 files, header 1,569/1,569, fit 1,569/1,569, no RES with Error != 0.**
  Samples: file number, size, sha256 first 16 hex digits, body end offset (the walk prints the largest
  fitting capture per id).

Field-name sources: PS4 DWARF member (`m_` prefix dropped) **V**; Season 3 additions carry Arrowgene
names, **I**.

**PS4 class sharing (asked by the brief).** Groups 8 and 58 share **no** PS4 class: group 58 reuses the
Instance/Common types (`CDataCommonU32`, `CDataCommonU8`, `CDataAreaSpotSet`, `CDataGatheringItemElement`,
`CDataGatheringItemGetRequest`). Groups 8 and 53 share `CDataPartnerPawnData` (8.2.2 and 53.8.2, the
same PC reader `0x7710a0`, V). Within group 8, 8.3.2/8.9.2 share `CDataPawnInfo` (PC `0x772180`), 8.28.2/
8.34.16 share the `CDataPawnHistory` list (PC `0x772020`), and 8.2.2/8.8.2/8.20.2 share
`CDataPawnListData` (PC `0x772750`, Pawn.hexpat) (V).

## 1. Shared Season 3 structures

### 1.1 CDataPawnInfo (PC `0x772180`; PS4 `Read_CDataPawnInfo_ 0x1a2bfc0`)

Users: 8.3.2, 8.9.2. PC wire order (V, Hex-Rays; element readers named), PS4 DWARF `CDataPawnInfo`:

| # | PC | Wire | PS4 02020005 |
| --- | --- | --- | --- |
| 1 | inline | u32 | `u32 m_unVersion` (V) |
| 2 | inline | MtString | `m_wstrName` |
| 3 | `0x764550` | CDataEditInfo (122 B; Context.hexpat) | `CEditInfo m_EditInfo` (identical, V) |
| 4-7 | inline | u8, u32, u32, u8 | `m_ucState, m_unMaxHp, m_unMaxStamina, m_ucJob` |
| 8 | `0x75c660` -> `0x75c770` | list CDataCharacterJobData {u8, u32, u32, u32, u16 x10, u8 x30} | `m_CharacterJobDataList` {u8 m_ucJob, u32 m_unExp, u32 m_unJobPoint, u32 m_unLv, u16 m_usAtk..m_usGuts, u8 m_ucFireResist..m_ucMDefDownResist} (same widths, V) |
| 9, 10 | `0x75c190` -> `0x765fb0` -> `0x766070` | 2 x list CDataCharacterEquipData {list CDataEquipItemInfo} | `m_CharacterEquipDataList`, `m_CharacterEquipViewDataList`; **element differs (Season 3 CDataEquipItemInfo, Login.hexpat)** |
| 11 | `0x766120` | list {u32, u8} | `m_CharacterEquipJobItemList` CDataEquipJobItem {u32 m_unJobItemID, u8 m_ucEquipSlotNo} (V) |
| 12 | inline | u8 | `m_ucJewelrySlotNum` |
| 13 | `0x766210` | **list {u8, u16}** | none: **Season 3** (Arrowgene `CharacterItemSlotInfoList` {StorageType, SlotMax}, I) |
| 14 | `0x771c10` | u32 x4, list `0x771c80` {u8, u32} | `CPawnCraftData m_CraftData` {u32 m_unCraftExp, m_unCraftRank, m_unCraftRankLimit, m_unCraftPoint, m_PawnCraftSkillList} (V) |
| 15 | `0x772860` | list {u8, u32} | `m_PawnReactionList` (Context.hexpat `CDataPawnReaction`) |
| 16-21 | inline | bool, bool, u8 x4 | `m_bHideEquipHead, m_bHideEquipLantern, m_ucAdventureCount, m_ucCraftCount, m_ucMaxAdventureCount, m_ucMaxCraftCount` |
| 22 | `0x75f800` | list {u8} | `m_ContextNormalSkillList` |
| 23, 24 | `0x75f140` | 2 x list {u8, u32, u8} | `m_ContextSkillList`, `m_ContextAbilityList` |
| 25 | inline | u32 | `m_unAbilityCostMax` |
| 26 | `0x7701c0` | u16 x13 | `COrbGainExtendParam m_ExtendParam` {m_usHpMax .. m_usSupportPawnSlot} (V) |
| 27-29 | inline | u8, u8, u32 | `m_ucPawnType, m_ucShareRange, m_unLikability` |
| 30 | `0x772aa0` | **u8[64]** (fixed, no count) | none: **Season 3** (Arrowgene `TrainingStatus`, I) |
| 31 | `0x772e80` | **u32 x5** | none: **Season 3** (Arrowgene `CDataPawnTrainingProfile` {TrainingExp, DialogCount, DialogCountMax, AttackFrequencyAndDistance, TrainingLv}, I) |
| 32 | `0x772950` | **list {u8, u8}** | none: **Season 3** (Context.hexpat `SpSkill`, Arrowgene `SpSkillList`, I) |

Items 30-32 are the same three Season 3 additions as `CDataContextPawnInfo` (Context.hexpat, PC
`0x75f8d0`), read by the same element readers (`0x772950`, V). Counter-test (PS4 body: no item 13, no
items 30-32, PS4 `CDataEquipItemInfo`): fails **72/72** (8.3.2) and **2/2** (8.9.2).

### 1.2 Pawn list elements

| Struct | PC | Wire (PC) | PS4 02020005 |
| --- | --- | --- | --- |
| CDataPawnList (8.2.2) | list `0x7725c0`, element `0x772680` | s32, u32, MtString, u8, u8, u8, CDataPawnListData (`0x772750`), **u32, u32, u32** | `Read_CDataPawnList__0 0x1a2ca80`: `s32 m_nPawnId, u32 m_unSlotNo, m_wstrName, u8 m_ucSex, u8 m_ucPawnState, u8 m_ucShareRange, CPawnListData m_PawnListData` (V); **three u32 Season 3** (Arrowgene `Unk0, TrainingExp, Unk2`, I) |
| CDataRentedPawnList (8.8.2) | list `0x776ce0`, element `0x776da0` | s32, u32, MtString, u8 x4, CDataPawnListData, u8 | `0x1a2b780`: `m_nPawnId, m_unSlotNo, m_wstrName, m_ucSex, m_ucPawnState, m_ucCraftCount, m_ucAdventureCount, m_PawnListData, u8 m_ucPawnType` (same, V) |
| CDataLostPawnList (8.20.2) | list `0x76d980`, element `0x76da40` | s32, u32, MtString, u8 x3, u32, CDataPawnListData | `0x1a2ae70`: `…, m_ucShareRange, u32 m_unReviveCost, m_PawnListData` (same, V) |
| CDataPawnHistory (8.28.2, 8.34.16) | list `0x772020`, element `0x7720e0` | u32, CDataCommunityCharacterBaseInfo (`0x75ecf0`), u64, u64, u8, u8, u32, CDataPawnFeedback (`0x771fd0` u8 x3) | `0x1a2a530`: `u32 m_unPawnID, m_DebtorBaseInfo, u64 m_ullReturnDate, u64 m_ullAdventureTime, u8 m_ucAdventureCount, u8 m_ucCraftCount, u32 m_unKillEnemyNum, CPawnFeedback {u8 m_ucType, u8 m_ucValue, u8 m_ucCommentNo}` (same, V) |

Counter-test 8.2.2 (PS4 element): fails **119/119**.

### 1.3 Other readers

| Struct | PC | Wire | PS4 02020005 |
| --- | --- | --- | --- |
| CDataPartnerPawnData | `0x7710a0` | u32, u32, u8 | `u32 m_unPawnId, u32 m_unLikability, u8 m_ucPersonality` (V) |
| CDataPawnProfile | `0x7727d0` | CDataCommunityCharacterBaseInfo, CDataArisenProfile (`0x7596f0` {u8, u32, u32, u16, u32}), MtString, u32 | `m_OwnerBaseInfo, CArisenProfile {u8 m_ucBackgroundID, CAchievementIdentifier m_Title {u32 m_unUid, u32 m_unIndex}, u16 m_usMotionID, u32 m_unMotionFrameNo}, m_wstrComment, u32 m_unRentalCost` (V) |
| CDataPawnTotalScore | `0x772a40` | u32, u32, u32, list `0x771ed0` {u8, u8, u8} | `u32 m_unRentalCount, m_unBattleCount, m_unCraftCount, MtTypedArray<CDataPawnFeedback> m_AveragePawnFeedbackList` (V) |
| CDataOrbPageStatus | list `0x7702d0` | u8, list `0x76fe50` {u8, u8} | `u8 m_ucPageNo, OrbCategoryStatusVec {u8 m_ucCategoryID, u8 m_ucReleaseNum}` (V) |
| CDataJobOrbTreeStatus | list `0x76c270` | u8, bool, f32 | `u8 m_ucJobID, b8 m_bIsReleased, f32 m_fRate` (V) |
| CDataPartyMember | `0x771580` | CDataCharacterListElement (`nPacket::Read_CDataCharacterListElement_ 0x75ccf0`, Season 3 trailing u8), u8, s32, u32, bool x3, u8, u8[8] (`0x757ce0`), u8 | `Read_CDataPartyMember_ 0x1a2b2f0`: `m_CharacterListElement, u8 m_ucMemberType, s32 m_nMemberIndex, u32 m_unPawnId, b8 m_bIsLeader, b8 m_bIsPawn, b8 m_bIsPlayEntry, u8 m_ucJoinState, u8[8] m_ucAnyValueList, u8 m_ucSessionStatus` (V; differs only by the list element's u8) |
| CDataPartnerPawnReward | list `0x7710f0` | u8, u32, u32 | `u8 m_ucType, CPartnerPawnRewardParam {u32 m_unParamTypeId, u32 m_unUID}` (V) |

## 2. Group 8 PAWN

### 2.1 8.2.1 C2S_PAWN_GET_MYPAWN_LIST_REQ / 8.2.2 S2C_…_RES

- PC writer `0x833320` (8,2,1): no body (V). PS4 `Send_C2S_GET_MYPAWN_LIST_REQ 0x19b43a0`: none (V).
- PC handler `0x7eab80`, reader `0x8123e0`: RES header, list `0x7725c0` (CDataPawnList, § 1.2),
  `0x7710a0` CDataPartnerPawnData (V). PS4 `CPacket_S2C_GET_MYPAWN_LIST_RES::ReadPacket 0x19d5460`:
  `m_PawnList`, `CPartnerPawnData m_PartnerInfo` (V).
- Season 3: three trailing u32 per CDataPawnList element (V). Counter-test fails 119/119.
- Wire REQ empty. RES `s32 Error; if (Error == 0) { s32 Result; MtTypedArray<CDataPawnList> PawnList;
  CDataPartnerPawnData PartnerInfo; }`.
- Walk REQ 119/119 slack 7 (`stream1-…-35/12011_…8_2_1`, 16 B, `53fa6f1da38ce99b`, end 0x9). RES 119/119
  slack 1-11, up to 3 pawns, craft-skill lists up to 10; `stream21-failedlogin-marked.pcapng_tcp-stream-48/
  12270_S2C_PAWN_GET_MYPAWN_LIST_RES_…8_2_2` (352 B, `925891444c7a0580`), end 0x15c: pawns 14310734
  "Serelia" (tail 1, 30000, 3), 14313101 "Azula", 14332659 "Seelix" (tail 5, 1422, 0); PartnerInfo
  {14332659, 5, 7}.

### 2.2 8.3.1 GET_MYPAWN_DATA_REQ / 8.3.2 …_RES and 8.9.1 GET_RENTED_PAWN_DATA_REQ / 8.9.2 …_RES

- PC writers `0x833230` (8,3,1) and `0x833ad0` (8,9,1): u8, s32 (V). PS4 `Send_C2S_GET_MYPAWN_DATA_REQ
  0x19b44d0` / `Send_C2S_GET_RENTED_PAWN_DATA_REQ 0x19b4ea0`: `u8 in_SlotNo, s32 in_PawnId` (V).
- PC handlers `0x7ea9d0` / `0x7eb9f0`, readers `0x812350` / `0x812b40`: RES header, u32, CDataPawnInfo
  `0x772180` (V, § 1.1). PS4 `OnPacket_S2C_GET_MYPAWN_DATA_RES 0x2e3350` / `…GET_RENTED_PAWN_DATA_RES
  0x2e4860`: `u32 m_unPawnID, CPawnInfo m_PawnInfo` (V).
- Season 3: CDataPawnInfo (§ 1.1). Counter-test fails 72/72 and 2/2.
- Wire REQ `u8 SlotNo; s32 PawnId;` (5 B). RES `… s32 Result; u32 PawnId; CDataPawnInfo PawnInfo; }`.
- Walk 8.3.1 72/72 slack 2 (`stream21-…-48/13030_…8_3_1`, 16 B, `0714830b169e8dc6`, end 0xe); 8.3.2
  72/72 slack 9-15; `stream21-…-48/13039_S2C_PAWN_GET_MYPAWN_DATA_RES_…8_3_2` (1520 B,
  `6870504a38b2330e`), end 0x5e3: PawnId 14332659 "Seelix", 6 job entries, 14 equipment / 5 view
  items, item 13 = 17 entries (first {2, 1}, {3, 10}), craft {466369, 70, 71, 0}, Likability 157,
  training u32 x5 {1422, 0, 3, 6, 5}, SpSkill {3,3},{4,3},{9,2}. 8.9.1 2/2 slack 2
  (`stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/3269_…8_9_1`, 16 B, `de84c8ebe1301945`);
  8.9.2 2/2 slack 11 (`stream86-…-9/3275_…8_9_2`, 1104 B, `85118698aebd9b7a`, end 0x445: "Iris", item 13
  empty, equipment items with non-empty EquipElement and AddStatus lists).
- Capture coverage of § 1.1 lists: all non-empty in some capture (max: jobs 6, equip items 14, the
  third CDataEquipItemInfo list 17, item 13 17, craft skills 10, reactions 11, SpSkill 3).

### 2.3 8.8.1 GET_RENTED_PAWN_LIST_REQ / 8.8.2 …_RES

- PC writer `0x833bc0` (8,8,1): no body (V). PS4 `Send_C2S_GET_RENTED_PAWN_LIST_REQ 0x19b4d70`: none.
- PC handler `0x7ebb00`, reader `0x812bd0`: RES header, list `0x776ce0` (CDataRentedPawnList, § 1.2) (V).
  PS4 `OnPacket_S2C_GET_RENTED_PAWN_LIST_RES 0x2e45c0`: `m_RentedPawnList` (V). No Season 3 change.
- Wire REQ empty. RES `… s32 Result; MtTypedArray<CDataRentedPawnList> RentedPawnList; }`.
- Walk REQ 54/54 slack 7 (`stream1-…-35/12015_…8_8_1`, 16 B, `272e8204e5f1ddf8`). RES 54/54 slack 9-13,
  up to 3 elements; `stream21-…-48/12277_…8_8_2` (320 B, `a1a29cac5c683fac`), end 0x137: 10535107
  "Satsuki", 12178450 "Dessault", 12770599 "Mugen".

### 2.4 8.12.1 JOIN_PARTY_MYPAWN_REQ / 8.12.2 …_RES

- PC writer `0x833c80` (8,12,1): u8 (V). PS4 `Send_C2S_JOIN_PARTY_MYPAWN_REQ 0x19b5170`: `u8 in_SlotNo` (V).
- PC handler `0x7ebd40`, reader `0x812cc0`: RES header only (V). PS4 `OnPacket_S2C_JOIN_PARTY_MYPAWN_RES
  0x2e5ff0`: header only (V).
- Wire REQ `u8 SlotNo;` (1 B). RES header only.
- Walk REQ 7/7 slack 6 (`stream85-marked.pcapng_tcp-stream-11/10697_…8_12_1`, 16 B, `322876154113bd35`,
  end 0xa). RES 9/9 slack 15 (`stream85-…-11/10700_…8_12_2`, 32 B, `fb62ad49184e408a`, end 0x11).

### 2.5 8.20.1 GET_LOST_PAWN_LIST_REQ / 8.20.2 …_RES

- PC writer `0x833170` (8,20,1): no body (V). PS4 `Send_C2S_GET_LOST_PAWN_LIST_REQ 0x19b5900`: none.
- PC handler `0x7ea870`, reader `0x8122d0`: RES header, list `0x76d980` (CDataLostPawnList, § 1.2) (V).
  PS4 `OnPacket_S2C_GET_LOST_PAWN_LIST_RES 0x2e7470`: `m_PawnList` (V). No Season 3 change.
- Wire REQ empty. RES `… s32 Result; MtTypedArray<CDataLostPawnList> PawnList; }`.
- Walk REQ 20/20 slack 7 (`stream21-…-48/12975_…8_20_1`, 16 B, `bcfbce0e17a9ffbe`). RES 20/20 slack 11,
  **list always empty** (element code-only); `stream21-…-48/12991_…8_20_2` (32 B, `e797a6a93c9362b4`),
  end 0x15.

### 2.6 8.28.1 GET_PAWN_HISTORY_LIST_REQ / 8.28.2 …_RES

- PC writer `0x833670` (8,28,1): u32 (V). PS4 `Send_C2S_GET_PAWN_HISTORY_LIST_REQ 0x19b6090`: `u32
  in_PawnID` (V).
- PC handler `0x7eb1c0`, reader `0x812720`: RES header, list `0x772020` (CDataPawnHistory, § 1.2) (V). PS4
  `OnPacket_S2C_GET_PAWN_HISTORY_LIST_RES 0x2e8620`: `m_PawnHistoryList` (V). No Season 3 change.
- Wire REQ `u32 PawnId;` (4 B). RES `… s32 Result; MtTypedArray<CDataPawnHistory> PawnHistoryList; }`.
- Walk REQ 20/20 slack 3 (`stream21-…-48/12995_…8_28_1`, 16 B, `94e7f06b810816c1`, end 0xd). RES 20/20
  slack 3-6, up to 2 elements; `stream51-marked.pcapng_tcp-stream-11/24589_…8_28_2` (128 B,
  `63cb2fc0fe398c0f`), end 0x7d: PawnID 14332659, debtors 1534864 "Claire Tawara" and 546408 "Greenapple
  Star", ReturnDate 1565708665 / 1562611119, feedback {2,2,1} / {2,2,4}.

### 2.7 8.30.1 C2S_PAWN_GET_NORA_PAWN_LIST_REQ

- PC writer `0x8333e0` (8,30,1): no body (V). PS4 `Send_C2S_GET_NORA_PAWN_LIST_REQ 0x19b49d0`: none (V).
  The RES 8.30.2 already has a pattern.
- Walk 41/41 slack 7; `stream1-…-35/12145_…8_30_1` (16 B, `18041ee19ce35b00`), end 0x9.

### 2.8 8.33.16 S2C_PAWN_GET_PAWN_PROFILE_NTC

- PC handler `0x7eb470`, reader `0x812820`: u32, u32, CDataPawnProfile `0x7727d0` (V). PS4
  `OnPacket_S2C_GET_PAWN_PROFILE_NOTICE 0x2e53b0`: `u16 m_usError, u32 m_unCharacterId, u32 m_unPawnId,
  CPawnProfile m_PawnProfile` (V; same body).
- Wire `u32 CharacterId; u32 PawnId; CDataPawnProfile PawnProfile;`.
- Walk 74/74 slack 1-4; PS4 framing fails 74/74. `stream86-…-9/3272_…8_33_16` (80 B, `c0af3255bec20732`),
  end 0x4c: CharacterId 2144504, PawnId 11950249, owner 855048 "Nanja Rahoi", profile {44, {0, 0}, 1724,
  35135}, comment "おう、覚者様", RentalCost 8526.

### 2.9 8.34.16 S2C_PAWN_GET_PAWN_HISTORY_INFO_NTC

- PC handler `0x7eafc0`, reader `0x8126a0`: u32, u32, list `0x772020` (V). PS4
  `OnPacket_S2C_GET_PAWN_HISTORY_INFO_NTC 0x2e5740`: `u16, u32 m_unCharacterId, u32 m_unPawnId,
  m_PawnHistoryList` (V; same body).
- Wire `u32 CharacterId; u32 PawnId; MtTypedArray<CDataPawnHistory> PawnHistoryList;`.
- Walk 74/74 slack 3-13, up to 20 elements; PS4 framing fails 73/74. `stream86-…-9/3273_…8_34_16`
  (1008 B, `a0febde1de3fdf24`), end 0x3e3.

### 2.10 8.35.16 S2C_PAWN_GET_PAWN_TOTAL_SCORE_INFO_NTC

- PC handler `0x7eb510`, reader `0x8128a0`: u32, u32, CDataPawnTotalScore `0x772a40` (V). PS4
  `CPacket_S2C_GET_PAWN_TOTAL_SCORE_INFO_NTC::ReadPacket 0x19d57b0`: `u16, u32 m_unCharacterId,
  u32 m_unPawnId, CPawnTotalScore m_TotalScore` (V; same body).
- Wire `u32 CharacterId; u32 PawnId; CDataPawnTotalScore TotalScore;`.
- Walk 74/74 slack 6-15; PS4 framing fails 74/74. `stream86-…-9/3273_…8_35_16` (48 B,
  `02efe9f1779834c6`), end 0x2a: 2144504, 0, {293, 332072, 4286, [{0,4,4}, {2,5,3}, {1,5,1}]}.

### 2.11 8.36.16 S2C_PAWN_GET_PAWN_ORB_DEVOTE_INFO_NTC

- PC handler `0x7eb2c0`, reader `0x8127a0`: u32, u32, list `0x7702d0` (CDataOrbPageStatus), list `0x76c270`
  (CDataJobOrbTreeStatus), **list `0x76c270` again** (V). PS4 `CPacket_S2C_GET_PAWN_ORB_DEVOTE_INFO_NTC::
  ReadPacket 0x19d5890`: `u16, u32 m_unCharacterId, u32 m_unPawnId, m_OrbStatusList, m_JobOrbStatusList` (V).
- **Season 3: a second CDataJobOrbTreeStatus list (V)** (Arrowgene `JobOrbHiBOStatusList`, I).
  Counter-tests: PS4 body fails **72/74**; PS4 framing fails 74/74.
- Wire `u32 CharacterId; u32 PawnId; MtTypedArray<CDataOrbPageStatus> OrbStatusList;
  MtTypedArray<CDataJobOrbTreeStatus> JobOrbStatusList; MtTypedArray<CDataJobOrbTreeStatus> unk_JobOrbStatusList;`.
- Walk 74/74 slack 3-11 (lists up to 4 pages x 5 categories, 11 + 11 job entries);
  `stream21-…-48/13036_…8_36_16` (224 B, `37f41adae6401675`), end 0xdd: 2117592, 14332659, pages 1-4 each
  {0:5, 1:8, 2:8, 3:8, 4:8}; list 1 jobs 1-11 (5, 6, 8 released; rates 1.0, 0.28, 0.59); list 2 jobs 1-11 all released
  (rates 0.0-0.8).

### 2.12 8.37.16 S2C_PAWN_JOIN_PARTY_PAWN_NTC (unresolved -> matched `JOIN_PARTY_PAWN_NOTICE`, V)

- PC handler `0x7ebeb0` (linear): `sub_407AC0(conn)` and `byte [conn+0x467a] == 0` -> return 1 (ignored);
  else builds a packet object with group 8, id `0x25` (37), sub `0x10`, reads it with `0x771580`
  (CDataPartyMember, § 1.3; first call `nPacket::Read_CDataCharacterListElement_ 0x75ccf0`), then
  `0x7ebdd0` (party-member update: looks the member up by MemberIndex, `sub_85C3A0`, `sub_B5C880`) (V).
- PS4 `cSeedGameSvConnection::OnPacket_S2C_JOIN_PARTY_PAWN_NOTICE 0x2e63b0`: same guard
  (`mLoginData.mIsReturnPrepare && !mIsJoinParty` -> return true), then `u16 m_usError,
  Read_CDataPartyMember_` (V). It is the **only** PS4 function that reads a single CDataPartyMember (xrefs
  to `Read_CDataPartyMember_`: this handler and the list reader `Read_CDataPartyMember__0`), so the match
  rests on the body and the guard (V). Triage's "read-seq ratio 0.00 (0/20)" came from the handler not
  being decompilable.
- Season 3: CDataCharacterListElement's trailing u8 (Character.hexpat). Counter-tests: PS4 body fits 9/9
  (slack 4-7 > 1: not discriminating; the u8 rests on the PC reader `0x75ccf0`, V); PS4 framing fails 9/9.
- Wire `CDataPartyMember PartyMember;` (no header).
- Walk 9/9 slack 4-7; `stream85-…-11/10701_…8_37_16` (64 B, `1d23c17ee649cb20`), end 0x39:

```
00000000: 0800 2510 3400 0000 6000 2155 9b00 0648  ..%.4...`.!U...H
00000010: 656c 656e 6100 0000 0000 0000 0663 0000  elena........c..
00000020: 0000 0002 0000 0001 00dc 8fee 0001 0002  ................
00000030: 0000 0000 0000 0000 00a0 8c90 2f00 0000  ............/...
```

  CharacterID 2184603 "Helena", ServerID 0, OnlineStatus 0, CurrentJob {6, 99}, EntryJob {0, 0},
  MatchingProfile "", u8 0; MemberType 2, MemberIndex 1, PawnId 14454766, IsLeader 0, IsPawn 1,
  IsPlayEntry 0, JoinState 2, AnyValueList 0 x8, SessionStatus 0.

## 3. Group 53 PARTNER_PAWN

### 3.1 53.4.1 PAWN_LIKABILITY_REWARD_LIST_GET_REQ / 53.4.2 …_RES; 53.6.1 …RELEASED_REWARD_LIST_GET_REQ / 53.6.2 …_RES

- PC writers `0x831550` (53,4,1), `0x8313a0` (53,6,1): no body (V). PS4 `Send_C2S_PAWN_LIKABILITY_REWARD_
  LIST_GET_REQ 0x19ce590`, `Send_C2S_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_REQ 0x19ce820`: none (V).
- PC handlers `0x7e6c60` / `0x7e6a80`, readers `0x810610` / `0x810510`: RES header, list `0x7710f0`
  (CDataPartnerPawnReward, § 1.3) (V). PS4 `OnPacket_S2C_PAWN_LIKABILITY_REWARD_LIST_GET_RES 0x335a80`
  (`m_RewardList`) / `…RELEASED_REWARD_LIST_GET_RES 0x335e80` (`m_ReleasedRewardList`) (V). No change.
- Wire REQ empty. RES `… s32 Result; MtTypedArray<CDataPartnerPawnReward> RewardList; }` (53.6.2:
  `ReleasedRewardList`).
- Walk 53.4.1 40/40 slack 7 (`stream21-…-48/12990_…53_4_1`, 16 B, `9dbd4148f3a72f38`); 53.4.2 40/40 slack
  11, **list always empty** (`12993_…53_4_2`, 32 B, `4590c0df49d22499`, end 0x15). 53.6.1 41/41 slack 7
  (`stream1-…-35/12102_…53_6_1`, 16 B, `79b0db66827a7fd6`); 53.6.2 41/41 slack 0-11, up to 19 elements;
  `stream51-…-11/10333_…53_6_2` (192 B, `d496502e684b4373`), end 0xc0: {3, 0, 45}, {4, 0, 441}, … {1, 2, 72}.

### 3.2 53.7.1 PARTNER_PAWN_NEXT_PRESENT_TIME_GET_REQ / 53.7.2 …_RES

- PC writer `0x831200` (53,7,1): no body (V). PS4 `Send_C2S_PARTNER_PAWN_NEXT_PRESENT_TIME_GET_REQ
  0x19ce160`: none (V).
- PC handler `0x7e68e0`, reader `0x810400`: RES header, u32, bool (V). PS4 `0x336090`: `u32 m_unRemainSec,
  b8 m_bIsMax` (V).
- Wire REQ empty. RES `… s32 Result; u32 RemainSec; bool IsMax; }` (5 B).
- Walk REQ 20/20 slack 7 (`stream21-…-48/13105_…53_7_1`, 16 B, `6bd7ab8d80371e7b`); RES 20/20 slack 10
  (`13106_…53_7_2`, 32 B, `bef02e0edc59da02`, end 0x16: 0, false).

### 3.3 53.8.1 PRESENT_FOR_PARTNER_PAWN_REQ / 53.8.2 …_RES

- PC writer `0x831610` (53,8,1): list writer `0x77fd30` {Write_MtString, Write_u32} (V). PS4
  `Send_C2S_PRESENT_FOR_PARTNER_PAWN_REQ 0x19ce290`: `MtTypedArray<CDataItemUIDList> m_ItemUIDList`
  {MtString m_wstrUID, u32 m_unNum} (V).
- PC handler `0x7e6e40`, reader `0x810690`: RES header, `0x7710a0` CDataPartnerPawnData (V). PS4
  `0x336220`: `CPartnerPawnData m_PartnerInfo` (V).
- Wire REQ `MtTypedArray<CDataItemUIDList> ItemUIDList;` (Quest.hexpat type, same PC writer). RES
  `… s32 Result; CDataPartnerPawnData PartnerInfo; }` (9 B).
- Walk REQ 20/20 slack 5, 1 element each; `stream21-…-48/13113_…53_8_1` (32 B, `900949f50b3bb276`), end
  0x1b: {"9A0B4E10", 2}. RES 20/20 slack 6 (`13119_…53_8_2`, 32 B, `7b339f99ade05a19`, end 0x1a: {14332659,
  5, 7}).

### 3.4 53.9.16 S2C_PARTNER_PAWN_LIKABILITY_UP_NTC (unresolved -> matched `PAWN_LIKABILITY_UP_NTC`, V by behaviour)

- PC handler `0x7e6d50` (table 9.16): packet object group `0x35`, id 9, sub `0x10`; inline `Read_u32`; on
  success `sGUIExt::getMsgFromIdxInfo(…, 0x1CC)` -> `sGUIExt::requestAnnounce`, plus `sChat::addMessage`
  of the same message (V). The u32 is not used.
- PS4 `OnPacket_S2C_PAWN_LIKABILITY_UP_NTC 0x3363a0`: `u16 m_usError, u32 m_unPawnId`, then
  `getMsgFromIdxInfo(…, 0x1CE)` -> `requestAnnounce` (V). Among the 27 PS4 `cSeedGameSvConnection`
  NTC/NOTICE handlers whose only reads are `u16, u32` (scan of all 250 such handlers), it is the only one
  that announces (V). The message index differs (PC 0x1CC, PS4 0x1CE): the message tables were not
  compared (I: shifted table).
- Wire `u32 PawnId;` (4 B, no header).
- Walk 23/23 slack 3; PS4 framing also fits 23/23 (slack 3 > 2: not discriminating; no-header framing
  rests on the PC handler, V). `stream21-…-48/13117_…53_9_16` (16 B, `665511b7426b5eda`), end 0xd:

```
00000000: 3500 0910 3400 0000 5300 dab2 f300 0100  5...4...S.......
```

  PawnId 14332659 (the partner pawn of 8.2.2/53.8.2 in the same stream).

## 4. Group 58 PAWN_EXPEDITION

### 4.1 58.0.1 GET_SALLY_INFO_REQ / 58.0.2 …_RES

- PC writer `0x832cc0` (58,0,1): no body (V). PS4 `Send_C2S_PAWN_EXPEDITION_GET_SALLY_INFO_REQ 0x19cf800`: none.
- PC handler `0x7ea0a0` (data in IDA, linear), reader `0x811c80`: RES header, u8, list `0x75e8e0`
  (CDataCommonU32), list `0x7594b0` {u32, u32}, list `0x75e8e0`, list `0x771d70` {u32, u32, u32} (V). PS4
  `CPacket_S2C_PAWN_EXPEDITION_GET_SALLY_INFO_RES::ReadPacket 0x19e0200`: `u8 m_ucSallyCount,
  m_AreaIdList (CDataCommonU32), m_HotSpotInfoList (CDataAreaSpotSet {u32 m_unAreaId, u32 m_unSpotId}),
  m_ActiveBuffLineupList (CDataCommonU32), m_ClanSallySpotInfoList (CDataPawnExpeditionClanSallySpotInfo
  {u32 m_unAreaID, u32 m_unSpotID, u32 m_unSallyNum})` (V). No change.
- Wire REQ empty. RES `… s32 Result; u8 SallyCount; MtTypedArray<CDataCommonU32> AreaIdList;
  MtTypedArray<CDataAreaSpotSet> HotSpotInfoList; MtTypedArray<CDataCommonU32> ActiveBuffLineupList;
  MtTypedArray<CDataPawnExpeditionClanSallySpotInfo> ClanSallySpotInfoList; }`.
- Walk REQ 30/30 slack 7 (`stream21-…-48/13527_…58_0_1`, 16 B, `39707b3396962231`). RES 30/30 slack 2-10;
  AreaIdList up to 17, HotSpot up to 1, **ActiveBuffLineup and ClanSallySpot always empty**;
  `stream3-party-experiments-marked.pcapng_tcp-stream-47/13121_…58_0_2` (112 B, `7979d50fd74a08d7`), end
  0x6e: SallyCount 1, 17 area ids, HotSpot {17, 916}.

### 4.2 58.3.1 SALLY_REQ / 58.3.2 …_RES

- PC writer `0x832e40` (58,3,1): u32, u32 (V). PS4 `Send_C2S_PAWN_EXPEDITION_SALLY_REQ 0x19cfbb0`: `u32
  in_AreaId, u32 in_SpotId` (V).
- PC handler `0x7ea200`, reader `0x811e00`: RES header only (V). PS4 `0x339370`: header only (V).
- Wire REQ `u32 AreaId; u32 SpotId;` (8 B). RES header only.
- Walk REQ 25/25 slack 15 (`stream21-…-48/13742_…58_3_1`, 32 B, `1c9a13772a713ea3`, end 0x11). RES 25/25
  slack 15 (`13744_…58_3_2`, 32 B, `f396e2d384e6c241`, end 0x11).

### 4.3 58.4.1 CHANGE_GOLDEN_SALLY_REQ / 58.4.2 …_RES

- PC writer `0x8327b0` (58,4,1): u8 (V). PS4 `Send_C2S_PAWN_EXPEDITION_CHANGE_GOLDEN_SALLY_REQ 0x19cfd10`:
  `u8 in_Price` (V).
- PC handler `0x7e9bd0`, reader `0x8118e0`: RES header only (V). PS4 `0x3394a0`: header only (V).
- Wire REQ `u8 Price;`. RES header only.
- Walk REQ 4/4 slack 6 (`stream59-epi-1-2-party-hobo1-marked.pcapng_tcp-stream-11/11077_…58_4_1`, 16 B,
  `fad26a00b545ce7f`, end 0xa). RES 4/4 slack 15 (`11080_…58_4_2`, 32 B, `5a4d1e55ef70ac6b`).

### 4.4 58.5.1 GET_SALLY_REWARD_REQ / 58.5.2 …_RES

- PC writer `0x832d80` (58,5,1): no body (V). PS4 `Send_C2S_PAWN_EXPEDITION_GET_SALLY_REWARD_REQ 0x19cfe60`: none.
- PC handler `0x7ea150`, reader `0x811d40`: RES header, `0x7595a0` {u32, u32}, u8, list `0x759f80`
  (linear: `Read_u32` count, grow `0x85e320`, alloc, `Read_u32` x3 per element), bool, bool (V). PS4
  `CPacket_S2C_PAWN_EXPEDITION_GET_SALLY_REWARD_RES::ReadPacket 0x19e0390`: `CAreaSpotSet m_SallySpotInfo,
  u8 m_ucSearchSpotType, CBattleResultInfo m_BattleResult {u32 m_unEnemyId, u32 m_unEnemyNum, u32
  m_unEnemyLevel}, b8 m_bIsGoldenSally` (V); the PS4 recompilation (S2C.cpp:8724) has the same body.
- **Season 3: BattleResult becomes a list, and a bool is appended (V by code).** Counter-test: the PS4
  body fits 25/25 (every capture's list holds exactly 1 element, so the PS4 body is 5 B shorter and the
  slack 4 becomes 9: not discriminating); the list and the second bool rest on the PC reader.
- Wire REQ empty. RES `… s32 Result; CDataAreaSpotSet SallySpotInfo; u8 SearchSpotType;
  MtTypedArray<CDataBattleResultInfo> BattleResultList; bool IsGoldenSally; bool unk_bool; }` (the bool
  order: first bool at the PS4 position = IsGoldenSally, I).
- Walk REQ 25/25 slack 7 (`stream21-…-48/13475_…58_5_1`, 16 B, `96e35d09b7c9d93b`). RES 25/25 slack 4;
  `stream21-…-48/13478_…58_5_2` (48 B, `43a94b3cedabc113`), end 0x2c:

```
00000000: 3a00 0502 3400 0000 0000 0000 0000 0000  :...4...........
00000010: 0000 0000 1000 0003 8e01 0000 0001 0000  ................
00000020: 00e5 0000 0001 0000 004e 0001 2100 0101  .........N..!...
```

  SallySpot {16, 910}, SearchSpotType 1, BattleResult [{229, 1, 78}], false, true.

### 4.5 58.7.1 GET_REWARD_DROP_REQ / 58.7.2 …_RES

- PC writer `0x832c00` (58,7,1): no body (V). PS4 `Send_C2S_PAWN_EXPEDITION_GET_REWARD_DROP_REQ 0x19cf590`: none.
- PC handler `0x7e9fe0`, reader `0x811be0`: RES header, u32, list `0x75e8e0` (CDataCommonU32), list
  `0x75e9b0` (CDataCommonU8) (V). PS4 `…GET_REWARD_DROP_RES::ReadPacket 0x19e0470`: `u32 m_unRewardDropNum,
  m_BoxIdVec (CDataCommonU32), m_MdlTypeVec (CDataCommonU8)` (V). No change.
- Wire REQ empty. RES `… s32 Result; u32 RewardDropNum; MtTypedArray<CDataCommonU32> BoxIdVec;
  MtTypedArray<CDataCommonU8> MdlTypeVec; }`.
- Walk REQ 25/25 slack 7 (`13492_…58_7_1`, 16 B, `542e209c6f9eda88`). RES 25/25 slack 14, lists up to 1;
  `stream21-…-48/13493_…58_7_2` (48 B, `247f55305fa2ebf0`), end 0x22: 1, [0], [0].

### 4.6 58.8.1 GET_REWARD_DROP_ITEM_LIST_REQ / 58.8.2 …_RES

- PC writer `0x832a30` (58,8,1): u32 (V). PS4 `Send_C2S_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_REQ
  0x19cf6c0`: `u32 in_PawnRewardBoxId` (V).
- PC handler `0x7e9de0`, reader `0x811ab0`: RES header, u32, list `0x769100` {u32, u32, u32, u32, bool}
  (the Instance.hexpat CDataGatheringItemElement reader, V). PS4 `OnPacket_…GET_REWARD_DROP_ITEM_LIST_RES
  0x339b40`: `u32 m_unPawnRewardBoxId, MtTypedArray<CDataGatheringItemElement> m_GatheringItemList`
  {u32 m_ulID, u32 m_ulItemId, u32 m_ulNum} (V).
- Season 3: the Season 3 CDataGatheringItemElement (+u32, +bool). Counter-test: PS4 element fails
  **10/50** (the 40 others have empty lists).
- Wire REQ `u32 PawnRewardBoxId;`. RES `… s32 Result; u32 PawnRewardBoxId;
  MtTypedArray<CDataGatheringItemElement> GatheringItemList; }`.
- Walk REQ 50/50 slack 3 (`13507_…58_8_1`, 16 B, `5e617958d21963b5`, end 0xd). RES 50/50 slack 2-7, up to
  5 elements; `stream60-exchange-apprasial-cashshop-treasurelot-marked.pcapng_tcp-stream-11/10996_…58_8_2`
  (112 B, `10fd8754c9b84703`), end 0x6e: box 0, {0, 7888, 2, 0, 0}, {1, 15991, 1, 0, 0}, … {4, 16020, 3, 0, 0}.

### 4.7 58.9.1 GET_REWARD_DROP_ITEM_REQ / 58.9.2 …_RES

- PC writer `0x832b10` (58,9,1): u32, list writer `0x77f9d0` {u32, u32} (the Instance.hexpat
  CDataGatheringItemGetRequest writer, V). PS4 `CPacket_C2S_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_REQ::
  WritePacket 0x1a32010`: `u32 m_unPawnRewardBoxId, MtTypedArray<CDataGatheringItemGetRequest>
  m_GatheringItemGetRequestList` (V).
- PC handler `0x7e9ef0`, reader `0x811b40`: RES header, u32, list `0x769240` {u32, u32}, u8 (V). PS4
  `…GET_REWARD_DROP_ITEM_RES::ReadPacket 0x19e0560`: `u32 m_unPawnRewardBoxId,
  m_GatheringItemListAfterRequest (CDataGatheringItemGetRequest), u8 m_ucPawnExpeditionStatus` (V). No change.
- Wire REQ `u32 PawnRewardBoxId; MtTypedArray<CDataGatheringItemGetRequest> GatheringItemGetRequestList;`.
  RES `… s32 Result; u32 PawnRewardBoxId; MtTypedArray<CDataGatheringItemGetRequest>
  GatheringItemListAfterRequest; u8 PawnExpeditionStatus; }`.
- Walk REQ 25/25 slack 7-15, up to 5 elements; `stream60-…-11/11002_…58_9_1` (64 B, `e24cf49ec6df90b0`),
  end 0x39: box 0, {0,2}, {1,1}, {2,1}, {3,3}, {4,3}. RES 25/25 slack 6, **list always empty**
  (`stream21-…-48/13516_…58_9_2`, 32 B, `585972b59ac91074`, end 0x1a).

## 5. Summary

PS4 mark: V = confirmed by code (symbol + body, or behaviour). Body bytes for Error == 0 (lists `+kn`;
var = strings or nested lists).

| id | name (file) | PS4 | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 8.2.1 | C2S_PAWN_GET_MYPAWN_LIST_REQ | V | 0 | 12011 | 119/119 |
| 8.2.2 | S2C_PAWN_GET_MYPAWN_LIST_RES | V (S3 +3 u32 per pawn) | var | 12270 | 119/119 |
| 8.3.1 | C2S_PAWN_GET_MYPAWN_DATA_REQ | V | 5 | 13030 | 72/72 |
| 8.3.2 | S2C_PAWN_GET_MYPAWN_DATA_RES | V (S3 CDataPawnInfo) | var | 13039 | 72/72 |
| 8.8.1 | C2S_PAWN_GET_RENTED_PAWN_LIST_REQ | V | 0 | 12015 | 54/54 |
| 8.8.2 | S2C_PAWN_GET_RENTED_PAWN_LIST_RES | V | var | 12277 | 54/54 |
| 8.9.1 | C2S_PAWN_GET_RENTED_PAWN_DATA_REQ | V | 5 | 3269 | 2/2 |
| 8.9.2 | S2C_PAWN_GET_RENTED_PAWN_DATA_RES | V (S3 CDataPawnInfo) | var | 3275 | 2/2 |
| 8.12.1 | C2S_PAWN_JOIN_PARTY_MYPAWN_REQ | V | 1 | 10697 | 7/7 |
| 8.12.2 | S2C_PAWN_JOIN_PARTY_MYPAWN_RES | V | 8 | 10700 | 9/9 |
| 8.20.1 | C2S_PAWN_GET_LOST_PAWN_LIST_REQ | V | 0 | 12975 | 20/20 |
| 8.20.2 | S2C_PAWN_GET_LOST_PAWN_LIST_RES | V | var (12 seen) | 12991 | 20/20 |
| 8.28.1 | C2S_PAWN_GET_PAWN_HISTORY_LIST_REQ | V | 4 | 12995 | 20/20 |
| 8.28.2 | S2C_PAWN_GET_PAWN_HISTORY_LIST_RES | V | var | 24589 | 20/20 |
| 8.30.1 | C2S_PAWN_GET_NORA_PAWN_LIST_REQ | V | 0 | 12145 | 41/41 |
| 8.33.16 | S2C_PAWN_GET_PAWN_PROFILE_NTC | V | var | 3272 | 74/74 |
| 8.34.16 | S2C_PAWN_GET_PAWN_HISTORY_INFO_NTC | V | var | 3273 | 74/74 |
| 8.35.16 | S2C_PAWN_GET_PAWN_TOTAL_SCORE_INFO_NTC | V | 24+3n | 3273 | 74/74 |
| 8.36.16 | S2C_PAWN_GET_PAWN_ORB_DEVOTE_INFO_NTC | V (S3 second JobOrbTree list) | var | 13036 | 74/74 |
| 8.37.16 | S2C_PAWN_JOIN_PARTY_PAWN_NTC | V body + guard `JOIN_PARTY_PAWN_NOTICE` | var | 10701 | 9/9 |
| 53.4.1 | C2S_PARTNER_PAWN_PAWN_LIKABILITY_REWARD_LIST_GET_REQ | V | 0 | 12990 | 40/40 |
| 53.4.2 | S2C_PARTNER_PAWN_PAWN_LIKABILITY_REWARD_LIST_GET_RES | V | 12+9n | 12993 | 40/40 |
| 53.6.1 | C2S_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_REQ | V | 0 | 12102 | 41/41 |
| 53.6.2 | S2C_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_RES | V | 12+9n | 10333 | 41/41 |
| 53.7.1 | C2S_PARTNER_PAWN_PARTNER_PAWN_NEXT_PRESENT_TIME_GET_REQ | V | 0 | 13105 | 20/20 |
| 53.7.2 | S2C_PARTNER_PAWN_PARTNER_PAWN_NEXT_PRESENT_TIME_GET_RES | V | 13 | 13106 | 20/20 |
| 53.8.1 | C2S_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_REQ | V | var | 13113 | 20/20 |
| 53.8.2 | S2C_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_RES | V | 17 | 13119 | 20/20 |
| 53.9.16 | S2C_PARTNER_PAWN_LIKABILITY_UP_NTC | V behaviour `PAWN_LIKABILITY_UP_NTC` | 4 | 13117 | 23/23 |
| 58.0.1 | C2S_PAWN_EXPEDITION_…_GET_SALLY_INFO_REQ | V | 0 | 13527 | 30/30 |
| 58.0.2 | S2C_PAWN_EXPEDITION_…_GET_SALLY_INFO_RES | V | 25+4a+8b+4c+12d | 13121 | 30/30 |
| 58.3.1 | C2S_PAWN_EXPEDITION_…_SALLY_REQ | V | 8 | 13742 | 25/25 |
| 58.3.2 | S2C_PAWN_EXPEDITION_…_SALLY_RES | V | 8 | 13744 | 25/25 |
| 58.4.1 | C2S_PAWN_EXPEDITION_…_CHANGE_GOLDEN_SALLY_REQ | V | 1 | 11077 | 4/4 |
| 58.4.2 | S2C_PAWN_EXPEDITION_…_CHANGE_GOLDEN_SALLY_RES | V | 8 | 11080 | 4/4 |
| 58.5.1 | C2S_PAWN_EXPEDITION_…_GET_SALLY_REWARD_REQ | V | 0 | 13475 | 25/25 |
| 58.5.2 | S2C_PAWN_EXPEDITION_…_GET_SALLY_REWARD_RES | V (S3 list + bool; code-only) | 23+12n | 13478 | 25/25 |
| 58.7.1 | C2S_PAWN_EXPEDITION_…_GET_REWARD_DROP_REQ | V | 0 | 13492 | 25/25 |
| 58.7.2 | S2C_PAWN_EXPEDITION_…_GET_REWARD_DROP_RES | V | 20+4n+m | 13493 | 25/25 |
| 58.8.1 | C2S_PAWN_EXPEDITION_…_GET_REWARD_DROP_ITEM_LIST_REQ | V | 4 | 13507 | 50/50 |
| 58.8.2 | S2C_PAWN_EXPEDITION_…_GET_REWARD_DROP_ITEM_LIST_RES | V (S3 element) | 16+17n | 10996 | 50/50 |
| 58.9.1 | C2S_PAWN_EXPEDITION_…_GET_REWARD_DROP_ITEM_REQ | V | 8+8n | 11002 | 25/25 |
| 58.9.2 | S2C_PAWN_EXPEDITION_…_GET_REWARD_DROP_ITEM_RES | V | 17+8n | 13516 | 25/25 |

Triage corrections: 8.37.16 unresolved -> matched `JOIN_PARTY_PAWN_NOTICE` (V: unique PS4 single
CDataPartyMember reader + same guard); 53.9.16 unresolved -> matched `PAWN_LIKABILITY_UP_NTC` (V by
behaviour: unique announcing u16+u32 PS4 notice). Neither is Season 3-exclusive. 58.0.2's handler is
data in the PC database.

Capture-tested discrimination (PS4 body, PC framing): fails 119/119 (8.2.2), 72/72 (8.3.2), 2/2 (8.9.2),
72/74 (8.36.16), 10/50 (58.8.2). PS4 framing on PC NTCs fails 74/74 (8.33.16, 8.35.16, 8.36.16), 73/74
(8.34.16), 9/9 (8.37.16); it fits 23/23 on 53.9.16 (not discriminating). Code-only: the 8.37.16 trailing
CharacterListElement u8 (PS4 body fits 9/9) and the 58.5.2 list/second bool (PS4 body fits 25/25). No RES
with Error != 0 captured.

Recompilation (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp`):
one body, `CPacket_S2C_PAWN_EXPEDITION_GET_SALLY_REWARD_RES::ReadPacket` (S2C.cpp:8724), equal to PS4 and
**contradicted for Season 3** by PC (§ 4.4). T001's `recompiled_body yes` is a `DDON_STUB` for 58.0.2
(S2C.cpp:8694) and 58.9.1 (C2S.cpp:242): overstated. `PacketData/Pawn.cpp` holds no reader bodies.

## 6. Shared types for pattern authors

Reuse: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`, `CDataCommonU8`);
`Pawn.hexpat` (`CDataPawnCraftSkill`, `CDataPawnListData` = PC `0x772750`, V here too); `Character.hexpat`
(`CDataCommunityCharacterBaseInfo` = `0x75ecf0`, `CDataJobBaseInfo`, `CDataCharacterListElement` =
`0x75ccf0` with its Season 3 u8); `Context.hexpat` (`CDataEditInfo` `0x764550`, `CDataPawnReaction`
`0x772860`, `SpSkill` `0x772950`, `CDataContextNormalSkillData` `0x75f800`, `CDataContextAcquirementData`
`0x75f140`, `EquipStatParam` shape {u8, u16}); `Login.hexpat` (`CDataEquipItemInfo` `0x766070`);
`Instance.hexpat` (`CDataGatheringItemElement` `0x769100`, `CDataGatheringItemGetRequest` `0x769240` /
writer `0x77f9d0`); `Quest.hexpat` (`CDataItemUIDList`, writer `0x77fd30`). Framing as T003 § 18 (inline
RES header; NTCs without header).

Add (V from the PC readers named; names PS4 DWARF unless marked I):

| Include | Struct | PC reader | Wire |
| --- | --- | --- | --- |
| `Pawn.hexpat` | `CDataPartnerPawnData` | `0x7710a0` | u32 PawnId, u32 Likability, u8 Personality |
| `Pawn.hexpat` | `CDataPawnList` | `0x772680` | s32 PawnId, u32 SlotNo, MtString Name, u8 Sex, u8 PawnState, u8 ShareRange, CDataPawnListData, u32 unk x3 (S3; I names Unk0, TrainingExp, Unk2) |
| `Pawn.hexpat` | `CDataRentedPawnList` | `0x776da0` | s32 PawnId, u32 SlotNo, MtString Name, u8 Sex, u8 PawnState, u8 CraftCount, u8 AdventureCount, CDataPawnListData, u8 PawnType |
| `Pawn.hexpat` | `CDataLostPawnList` | `0x76da40` | s32 PawnId, u32 SlotNo, MtString Name, u8 Sex, u8 PawnState, u8 ShareRange, u32 ReviveCost, CDataPawnListData |
| `Pawn.hexpat` | `CDataPawnFeedback` | `0x771fd0` / list `0x771ed0` | u8 Type, u8 Value, u8 CommentNo |
| `Pawn.hexpat` | `CDataPawnHistory` | `0x7720e0` | u32 PawnID, CDataCommunityCharacterBaseInfo DebtorBaseInfo, u64 ReturnDate, u64 AdventureTime, u8 AdventureCount, u8 CraftCount, u32 KillEnemyNum, CDataPawnFeedback |
| `Pawn.hexpat` | `CDataArisenProfile` (+ `CDataAchievementIdentifier`) | `0x7596f0` | u8 BackgroundID, {u32 Uid, u32 Index} Title, u16 MotionID, u32 MotionFrameNo |
| `Pawn.hexpat` | `CDataPawnProfile` | `0x7727d0` | CDataCommunityCharacterBaseInfo OwnerBaseInfo, CDataArisenProfile ProfileInfo, MtString Comment, u32 RentalCost |
| `Pawn.hexpat` | `CDataPawnTotalScore` | `0x772a40` | u32 RentalCount, u32 BattleCount, u32 CraftCount, MtTypedArray<CDataPawnFeedback> AveragePawnFeedbackList |
| `Pawn.hexpat` | `CDataOrbCategoryStatus` / `CDataOrbPageStatus` / `CDataJobOrbTreeStatus` | `0x76fe50` / `0x7702d0` / `0x76c270` | {u8 CategoryID, u8 ReleaseNum} / {u8 PageNo, MtTypedArray<CDataOrbCategoryStatus>} / {u8 JobID, bool IsReleased, float Rate} |
| `Pawn.hexpat` (includes Context, Login) | `CDataCharacterJobData` | `0x75c770` | u8 Job, u32 Exp, u32 JobPoint, u32 Lv, u16 Atk..Guts (10), u8 FireResist..MDefDownResist (30) |
| `Pawn.hexpat` | `CDataCharacterEquipData` | `0x765fb0` | MtTypedArray<CDataEquipItemInfo> EquipList |
| `Pawn.hexpat` | `CDataEquipJobItem` | `0x766120` element | u32 JobItemID, u8 EquipSlotNo |
| `Pawn.hexpat` | `CDataPawnCraftData` | `0x771c10` | u32 CraftExp, CraftRank, CraftRankLimit, CraftPoint, MtTypedArray<CDataPawnCraftSkill> |
| `Pawn.hexpat` | `CDataOrbGainExtendParam` | `0x7701c0` | u16 HpMax, StaminaMax, Attack, Defence, MagicAttack, MagicDefence, AbilityCost, JewerlySlot, UseItemSlot, MaterialItemSlot, EquipItemSlot, MainPawnSlot, SupportPawnSlot |
| `Pawn.hexpat` | `CDataPawnInfo` | `0x772180` | § 1.1 (item 13 element {u8, u16}: reader `0x766210`, the Login.hexpat third-list reader; Arrowgene `CDataCharacterItemSlotInfo` {StorageType, SlotMax}, I) |
| `Pawn.hexpat` | `CDataPartnerPawnRewardParam` / `CDataPartnerPawnReward` | `0x7710f0` element | {u32 ParamTypeId, u32 UID} / {u8 Type, CDataPartnerPawnRewardParam Value} |
| `Character.hexpat` (or Party) | `CDataPartyMember` | `0x771580` | § 1.3 |
| new `PawnExpedition.hexpat` (or `Area.hexpat`) | `CDataAreaSpotSet` | `0x7594b0` element / `0x7595a0` | u32 AreaId, u32 SpotId |
| same | `CDataPawnExpeditionClanSallySpotInfo` | `0x771d70` element | u32 AreaID, u32 SpotID, u32 SallyNum |
| same | `CDataBattleResultInfo` | `0x759f80` element (linear) | u32 EnemyId, u32 EnemyNum, u32 EnemyLevel |

## 7. Arrowgene leads

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`.
No misplacement in order or width: `CDataPawnInfo` (CharacterItemSlotInfoList, TrainingStatus[64],
CDataPawnTrainingProfile, SpSkillList at the PC positions), `CDataPawnList` (Unk0, TrainingExp, Unk2),
`CDataRentedPawnList`, `CDataLostPawnList`, `CDataPawnHistory`, `CDataPawnTotalScore`, `CDataPartnerPawnData`,
`CDataPartnerPawnReward(Param)`, `CDataArisenProfile`, `CDataPawnCraftData`, `CDataJobOrbTreeStatus`,
`CDataOrbPageStatus`, `CDataPartyMember`, `CDataPawnExpeditionClanSallySpotInfo`, `S2CPawnGetMyPawnListRes`,
`S2CPawnGetMypawnDataRes`, `S2CPawnGetRentedPawnDataRes`, `S2CPawnGetPawnOrbDevoteInfoNtc` (two JobOrbTree
lists), `S2CPawnJoinPartyPawnNtc`, `S2CPartnerPawnLikabilityUpNtc`, the profile/history/total-score NTCs,
the partner REQ/RES and `S2CPawnExpeditionGetSallyInfoRes` agree with PC 03040008. Notes only:
`CDataRentedPawnList.PawnId` is written `UInt32` (PC reads s32; same width); `C2SPawnJoinPartyMypawnReq`
calls the u8 `PawnNumber` (PS4 `in_SlotNo`). Absent (no structure to check): 58.3.1, 58.4.1, 58.5.2,
58.7.2, 58.8.1/2, 58.9.1/2.

## 8. Open items and checks not run

- Names without code backing (I): the three 8.2.2 tail u32, CDataPawnInfo items 13 and 30-32, the second
  8.36.16 list, the 58.5.2 second bool (and which bool is IsGoldenSally).
- 53.9.16 message index PC 0x1CC vs PS4 0x1CE: message tables not compared.
- Never non-empty in captures (code-only): 8.20.2 list (CDataLostPawnList element), 53.4.2 list (its
  element is exercised by 53.6.2), 58.0.2 ActiveBuffLineup and ClanSallySpot lists, 58.9.2 list (element
  exercised by 58.9.1). 58.5.2's list always holds exactly 1 element (the list prefix is code-only).
- PC code read linearly only: `0x7ea0a0`, `0x7ebeb0`, `0x759f80`.
- ImHex not run (not on `PATH`); no pattern written (outside this package).

## Errata (R2, 2026-11-02)

- § 1.1 (after the item table): "Items 30-32 are the same three Season 3 additions as
  `CDataContextPawnInfo`" is wrong. `CDataContextPawnInfo` (Context.hexpat, PC `0x75f8d0`) has the
  reaction list, `unk_u8[64]` and the {u8, u8} list (`0x772950`) only, no u32 x5 (the 35.3.16 export
  fits with those). Two of the three additions are shared (items 30 and 32); item 31, the u32 x5,
  has only the `CDataPawnInfo` reader behind it (`0x772e80`). Fixed in `include/Pawn.hexpat` (R2b),
  where the member is now `unk_u32x5` of type `CDataPawnInfo_unk_0`.
