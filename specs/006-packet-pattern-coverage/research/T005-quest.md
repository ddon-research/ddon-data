# 006 T005: group 11 QUEST

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T005-quest.md`; the 79 group-11 rows of
`research/T001-triage.tsv` (4,352 captures). Base `b7db8e0551`. Marks: **V** verified in code (or by
capture for walk results), **I** inferred, **C** contradicted. All addresses are VAs. Both parts
(A: 11.0-11.60, B: the rest) are done in this one report.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t005/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t005/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays, `idautils`,
  `ida_ua.decode_insn` for linear decoding, `ida_typeinf` for DWARF structs); nothing renamed,
  retyped, commented, patched or reanalysed.
- PC primitives as T003/T004 § 0 (`nPacket::Read_u8 0x8bc410` … `Read_bool 0x8bc6e0`, `Read_s64
  0x8bc660`, `Read_MtString 0x8bc5b0`, `Write_* 0x8bc790-0x8bcb80`, `WritePacket 0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` -> group 11 `{0x212e638, 146}`, stride 0x18, key
  `(sub<<16)|id` at +0x10; handler pointers from the initializer `0x1a32060` (stores of `offset sub_X`
  into entry +0). Every S2C `pc_va` of the triage equals its table handler (V; 34 entries were
  resolved through the second store form, e.g. 11.7.16 -> `0x7f2db0`, 11.95.16 -> `0x7f0480`,
  11.103.16 -> `0x7f3fa0`). The reader is the call the handler makes with the packet.
- **Not functions in the PC database** (decoded linearly with `ida_ua.decode_insn`, no database
  change): handlers `0x7f13d0` (11.0.2), `0x7f1690`, `0x7f14b0`, `0x7f4850`, `0x7f1df0`, `0x7ef6c0`,
  `0x7f1d40`, `0x7f3270`; readers `0x816300`, `0x8169c0`, `0x814e10`, `0x816940`, `0x817a10`, list
  readers `0x7783d0`, `0x77b690`, `0x773ba0`, `0x773710`; the 11.62.1 writer at `0x838858-0x8388cf`.
- PC writers (C2S): the triage `pc_va`, `WritePacket(p, 11, id, sub, -1)` + body (V each, sub/id
  read from the decompiled call).
- PS4 match: by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, or behaviour), never
  by PS4 id. Notices: the PC handler pushes a `cQuestSvNot*` notice whose MtDTI name string sits in
  the DTI initializer (PC `dti__NNNN` -> string pushed before the init call); PS4 has exactly one
  `OnPacket_*` per notice class (`<class>::MyDTI::newInstance` xrefs).
- RES header (V, every PC RES reader below): `Read_s32` Error (+16); if non-zero return; else
  `Read_s32` Result, body. PS4 reads `u16 m_usError, s32 m_nResult`. PC NTC readers read **no**
  header (V for every NTC here except 11.45.16, which reads an s32 first, § 25). PS4 NTCs start with
  `Read_u16 m_usError` (PS4-only framing).
- **Walk**: stdlib Python (scratch scripts `wlib.py`/`wlay.py`/`wrun.py` in the session scratchpad,
  not saved in the repo), run from `D:/ddon-data` over `packets/decrypted_raw/`, every file whose
  suffix is `.11_<id>_<sub>` of the 79 ids. Header check: group 11, u16 id, sub, source (0x00 C2S,
  0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no overrun. Totals: **4,352 files,
  header 4,352/4,352, fit 4,352/4,352, no RES with Error != 0.** Counter-test: PS4 02020005 body
  with PC framing (and a second pass with PS4 framing: u16 error). Samples: file number, size,
  sha256 first 16 hex digits, body end offset.

Field-name sources: PS4 DWARF member (`m_` prefix dropped) **V**; names of Season 3 additions are
Arrowgene leads, **I**.

## 1. Shared Season 3 structures (used by many ids)

### 1.1 CDataQuestList (PC `0x774530`; PS4 `Read_CDataQuestList_ 0x1a249a0`)

Not the `CDataQuestOrderList` (`0x774a70`) of `Quest.hexpat`: a different, smaller reader. PC wire
(V order and widths):

| # | PC | PS4 02020005 | Pattern name |
| --- | --- | --- | --- |
| 1-4 | u32 x4 | u32 KeyId, QuestScheduleId, QuestId, BaseLevel | same (V) |
| 5 | u16 | u16 ContentJoinItemRank | V |
| 6 | list `0x77c5a0` CDataWalletPoint | u32 BaseGold | `BaseWalletPoint` (S3, I; replaces BaseGold/BaseRim) |
| 7 | list `0x76c780` {u8,u8,u32} | u32 BaseExp | `BaseExp` (S3 list `CDataQuestExp`, I) |
| 8-10 | u32 x3 | (u32 BaseRim), OrderNpcId, NameMsgId, DetailMsgId | OrderNpcId, NameMsgId, DetailMsgId (I by position) |
| 11-12 | u64 x2 | u64 EndDistributionDate (one) | `DistributionStartDate`, `EndDistributionDate` (which is new: I; Arrowgene start/end) |
| 13-14 | list `0x7771b0` {u32,u16} x2 | FixedRewardItemList, FixedRewardSelectItemList | V |
| 15 | list `0x75eec0` {u32} | — | `unk_u32_list` (S3; Arrowgene `ContentsReleaseList`, I) |
| 16 | list `0x774890` {u32,s32,s32} | QuestOrderConditionParamList | V |
| 17 | `0x774850` = list `0x773820` {u32} + list `0x7757e0` {u32,u32,u16,bool} | CQuestLog (TalkInfo {u32,u16,b8}) | `CDataQuestLog` of Quest.hexpat (V) |
| 18-19 | list u32 `0x773eb0`, `0x774350` | QuestFlagList, QuestLayoutFlagList | V |
| 20 | list `0x775310` | QuestProcessStateList | `CDataQuestProcessState` (V) |
| 21 | list `0x773d90` {u32,u32,u16,bool} | QuestEnemyInfoList {u32,u16,b8} | `CDataQuestEnemyInfo` of Quest.hexpat (V) |
| 22 | list `0x774420` {u32, list `0x7756f0` {u32,u32}} | QuestLayoutFlagSetInfoList | V |
| 23 | list `0x762fb0` {u32,u16,u16,u16} | DeliveryItemList {u32 ItemId, u16 Num} | `CDataQuestDeliveryItem` of Quest.hexpat (S3 shape, V) |
| 24 | bool | b8 IsClientOrder | V |

Capture discrimination: a PS4-body counter-test fails on every capture with a non-empty quest list
(11.1.2: 58 of 179, 11.3.2: 66 of 146, 11.2.2: 23 of 44, 11.4.2: 3 of 20, 11.0.2: 1 of 1).

### 1.2 Other shared readers

| Struct | PC | PS4 | Wire (PC 03040008) |
| --- | --- | --- | --- |
| `CDataQuestContents` | `0x773a20` | `CQuestContents` {u8 Type, s32 Param01-04} | u8 Type, s32 Param01..04, **u16 unk_u16, u16 unk_u16_2** (S3, V; Arrowgene Unk0/Unk1) |
| `CDataLightQuestDetail` | `0x76d1c0` | {u32 AreaId, BaseAreaPoint, GetCP, OrderLimit, ClearNum, BoardType} | **7 x u32** (S3 +1, V); order I: Arrowgene `AreaId, BoardId, GetAp, GetCp, OrderLimit, ClearNum, BoardType` |
| `CDataSetQuestDetail` | `0x778040` | `0x1a23b80` {u32 ImageId, ClearCount, ClearCharacterNum, BaseAreaPoint, u16 UndiscoveryGold/Exp/RimRatio, u16 LeaderCompleteNum, u16 RepeatRewardType, u8 RepeatRewardValue, RepeatRewardCompleteNum, RandomRewardNum, ChargeRewardNum, ProgressBonusNum, b8 IsDiscovery} | u32 x4, **list CDataWalletPoint, list CDataQuestExp** (replace the three u16 ratios; S3, V shape, names I), u16 LeaderCompleteNum, u16 RepeatRewardType, u8 x5, bool IsDiscovery |
| `CDataQuestIdScheduleId` | list `0x774050` | `0x1a1b3e0` {u32 QuestId, u32 QuestScheduleId} | same (V) |
| `CDataQuestId` | list `0x773f80` | `0x1a1ef20` | u32 QuestId (V) |
| `CDataPriorityQuest` | list `0x7735b0` | `0x1a1e9e0` {u32 QuestScheduleId, u32 QuestId, list Announce, list ProgressWork} | same (V) |
| `CDataQuestContentsSituationInfo` | list `0x773ab0` | `0x1a19940` {u32 QuestScheduleId, u32 QuestId} | same (V) |
| `CDataRewardItemDetail` | list `0x7772a0` | `0x1a24bb0` {u32 ItemId, u16 Num, u8 Type} | same (V) |
| `CDataQuestPartyBonusInfo` | `0x774de0` | `0x1a2d3e0` {u32 QuestScheduleId, QuestId, u16 Gold/Exp/Rim/AreaPointRatio, u32 Dorb, b8 IsReceived} | same (V) |

## 2. 11.0.1 C2S_QUEST_GET_LIGHT_QUEST_LIST_REQ / 11.0.2 S2C_…_RES

- PC writer `0x837850` (11,0,1): u32 (V). PS4 `Send_C2S_GET_LIGHT_QUEST_LIST_REQ 0x19b78b0`: u32 `m_unBaseID` (V).
- PC handler `0x7f13d0` (not a function), reader `0x816240`: RES header, u32, list `0x76d250` of
  {CDataQuestList, CDataLightQuestDetail (7 u32), CDataQuestContents (S3 +2 u16)}, u8, u8, bool (V).
  PS4 `CPacket_S2C_GET_LIGHT_QUEST_LIST_RES::ReadPacket 0x19d6170` (`Read_CDataLightQuestList_ 0x1a282a0`):
  `u32 m_unBaseID, MtTypedArray<CDataLightQuestList> m_LightQuestList {m_Param, m_Detail, m_Contents},
  u8 m_ucNotCompleteQuestNum, u8 m_ucGpCompletePriceGp, b8 m_bGpCompleteEnable` (V).
- Wire REQ `u32 BaseId;` (4 B). RES `s32 Error; if (Error == 0) { s32 Result; u32 BaseId;
  MtTypedArray<CDataLightQuestList> LightQuestList; u8 NotCompleteQuestNum; u8 GpCompletePriceGp; bool
  GpCompleteEnable; }`.
- Walk: REQ 1/1 slack 3, `11307` (16 B, `69316e7a7c5f0a63`) BaseId `0x1c`, end 0xd. RES 1/1 slack 6,
  `stream85-…-11/11308_S2C_QUEST_GET_LIGHT_QUEST_LIST_RES` (192 B, `c420b09f86676f7a`): Error 0,
  Result 0, BaseId `0x1c`, 1 element (KeyId 0, ScheduleId `0x0006091e`, QuestId `0x0266ee3a`, …), end
  0xba. PS4 body counter-test 0/1.

## 3. 11.1.1 C2S_QUEST_GET_SET_QUEST_LIST_REQ / 11.1.2 S2C_…_RES

- PC writer `0x8389b0` (11,1,1): u32 (V); PS4 `Send_… 0x19b79f0`: u32 `m_unDistributeID` (V).
- PC handler `0x7f2560`, reader `0x816fa0` ("OnPacket_QUEST_GET_SET_QUEST_LIST_RES"): RES header,
  u32, list `0x7783d0` of {CDataQuestList, CDataSetQuestDetail `0x778040`} (V). PS4
  `OnPacket_S2C_GET_SET_QUEST_LIST_RES 0x2ea7d0` (inline read): `u32 m_unDistributeID,
  MtTypedArray<CDataSetQuestList> {CQuestList m_Param, CSetQuestDetail m_Detail}` (V).
- Season 3: QuestList (§ 1.1) and SetQuestDetail ratios -> two lists (§ 1.2).
- Wire RES `… s32 Result; u32 DistributeId; MtTypedArray<CDataSetQuestList> SetQuestList; }`.
- Walk: REQ 179/179 slack 3 (`12178`, 16 B, `ab76b0428b13a4c7`, DistributeId 1). RES 179/179 slack
  4-14, up to 15 elements (58 non-empty); `stream1-…-35/12185_S2C_QUEST_GET_SET_QUEST_LIST_RES` (5712 B,
  `42803eee0eda2c04`): DistributeId 1, 14 elements (first KeyId `0x2b`, ScheduleId `0x00058fbd`, QuestId `0x01312d00`, BaseLevel 25;
  see the file), end 0x1644. PS4 body counter-test 121/179 (all 58 non-empty fail).

## 4. 11.2.1 GET_MAIN_QUEST_LIST_REQ / 11.2.2 …_RES

- PC writer `0x837ad0` (11,2,1): no body (V); PS4 `0x19b7b30` none (V).
- PC handler `0x7f1690` (not a function), reader `0x816470`: RES header, list `0x76ea60` of CDataQuestList
  (V). PS4 `OnPacket_S2C_GET_MAIN_QUEST_LIST_RES 0x2eaa90`: `MtTypedArray<CDataMainQuestList> {CQuestList
  m_Param}` (V).
- Wire REQ empty; RES `… s32 Result; MtTypedArray<CDataQuestList> MainQuestList; }`.
- Walk: REQ 44/44 slack 7 (`12166`, `ef3e40db208eba31`). RES 44/44 slack 0-11, max 1 element (23
  non-empty); `stream1-…-35/12167_…_11_2_2` (464 B, `8a428c22a5c721b5`), end 0x1d0. PS4 body 21/44.

## 5. 11.3.1 GET_TUTORIAL_QUEST_LIST_REQ / 11.3.2 …_RES

- PC writer `0x838c10`: u32 (V); PS4 `0x19b7c60`: u32 `m_unStageNo` (V).
- PC handler `0x7f2770`, reader `0x817130`: RES header, u32, list `0x77b690` {CDataQuestList, u8} (V).
  PS4 `0x2ead90`: `u32 m_unStageNo, MtTypedArray<CDataTutorialQuestList> {m_Param, u8 m_ucEnableCancel}` (V).
- Wire RES `… s32 Result; u32 StageNo; MtTypedArray<CDataTutorialQuestList> TutorialQuestList; }`.
- Walk: REQ 146/146 slack 3 (`12238`, `f1d10fce576ffc38`, StageNo 200). RES 146/146 slack 0-14, up to
  43 elements; `12257` (16192 B, `9f9a059fc422a9ec`), end 0x3f36. PS4 body 80/146.

## 6. 11.4.1 GET_LOT_QUEST_LIST_REQ / 11.4.2 …_RES

- PC writer `0x837930`: u32 (V); PS4 `0x19b8000`: u32 `m_unLotQuestType` (V).
- PC handler `0x7f14b0` (not a function), reader `0x816300` (not a function): RES header, u32, list
  `0x76dae0` {CDataQuestList, CDataQuestContents (S3)} (V). PS4 `0x2eaf30`: `u32 m_unLotQuestType,
  MtTypedArray<CDataLotQuestList> {m_Param, CQuestContents m_Contents}` (V).
- Walk: REQ 20/20 slack 3 (`13011`, `005f711b403d0418`). RES 20/20 slack 5-11; `stream62-…-11/11248`
  (256 B, `a345eaad53d4df94`), end 0xf5. PS4 body 17/20 (3 non-empty fail).

## 7. 11.5.1 GET_PACKAGE_QUEST_LIST_REQ / 11.5.2 …_RES (Season 3-exclusive, confirmed)

- No PS4 counterpart (V): no PS4 symbol, string or DWARF type containing `PACKAGE_QUEST`/`PackageQuest`
  (42,357 named types scanned); PS4 has no `cQuestSvNotPackageQuest*` class (PC has
  `cQuestSvNotPackageQuestComplete`/`…SequenceBegin`).
- PC writer `0x837fc0` (11,5,1): u32 (V). PC handler `0x7f1bb0`, reader `0x816830`: RES header, u32,
  list `0x7704d0` of {u32, list `0x770d30` of `0x770e50` {u32, s32, s32, list u32 `0x75e8e0`, bool,
  bool, list `0x7708c0` of CDataQuestList}} (V).
- Wire RES `… s32 Result; u32 unk_u32; MtTypedArray<CDataPackageQuestList> PackageQuestList; }` with
  `CDataPackageQuestList {u32 unk_u32; MtTypedArray<CDataPackageQuestDetail> Details;}` and detail
  `{u32; s32; s32; MtTypedArray<CDataCommonU32>; bool; bool; MtTypedArray<CDataQuestList>;}` (names I;
  Arrowgene `CDataPackageQuestList {Unk0, Details}`, `CDataPackageQuestDetail {Unk0..Unk6}` agrees).
- Walk: REQ 146/146 slack 3 (`12260`, `02b1f9b0dd1032b7`, value 200). RES 146/146 slack 7, **list never
  non-empty** (elements code-only); `12261` (32 B, `c6130f89cd9441cd`): Error 0, Result 0, u32 200,
  count 0, end 0x19.

## 8. 11.7.16 S2C_QUEST_11_7_16_NTC (unresolved -> Season 3-exclusive, V)

- PC handler `0x7f2db0` builds a packet object (group 11, id 7, sub 16), reader `0x8176e0` = list
  `0x76eee0` of {u32, u8} (no header), then pushes notice **`cQuestSvNotQuestMobHuntQuestListNum`**
  (DTI init string, V). PS4 has 33 `cQuestSvNot*` classes, none MobHunt; no PS4 name/string with
  `MobHunt`/`MOB_HUNT` (V) -> Season 3-exclusive.
- Triage candidate `OnPacket_S2C_GET_CHARACTER_BINARY_STATUS_NTC 0x3088f0` **rejected (C)**: reads `u16,
  u32, u32 count, u8 x n` (list of u8, not of {u32,u8}) and is unrelated behaviour.
- Wire: `MtTypedArray<{u32 unk_u32; u8 unk_u8;}> MobHuntQuestListNum` (names I).
- Walk: 43/43 slack 14, every capture 1 element; `stream21-…-48/12236` (32 B, `ff3d5a6df90ff1ba`):
  `00000001 00000001 09`, end 0x12. The rejected PS4 shape also fits (43/43, short body): the
  rejection rests on code.

## 9. 11.9.1 GET_WORLD_MANAGE_QUEST_LIST_REQ / 11.9.2 …_RES

- PC writer `0x838cf0`: empty (V); PS4 `0x19b7ed0` empty.
- PC handler `0x7f28c0`, reader `0x817220`: RES header, list `0x77cd60` {CDataQuestList, u8} (V). PS4
  `0x2eb250`: `MtTypedArray<CDataWorldManageQuestList> {m_Param, u8 m_ucIsTutorialGuide}` (V).
- Walk: REQ 42/42 slack 7 (`12163`, `4e2bc3aac691e758`). RES 42/42 slack 11, **list never non-empty**;
  `12164` (32 B, `e93f33fa906f4e23`) count 0, end 0x15. PS4 body fits 42/42 (empty lists): the
  Season 3 element is code-only.

## 10. 11.10.1 GET_END_CONTENTS_GROUP_REQ / 11.10.2 …_RES

- PC writer `0x8375f0`: u32 (V); PS4 `0x19baf70`: u32 `m_unGroupID` (V).
- PC handler `0x7f1180`, reader `0x816090`: RES header, u32, u32, `0x764fa0` -> list `0x77afb0` of
  `0x77b080` (V). PS4 `ReadPacket 0x19d6230`: `u32 m_unGroupID, u32 m_unEndContentsType,
  CEndContentsGroup {MtTypedArray<CDataTimeGainQuestList>}`; element `0x1a248e0` `{m_Param, u32
  m_unPlayTimeSec, b8 m_bIsNoTimeup, b8 m_bIsJoinCharacter, b8 m_bIsJoinPawn, b8 m_bIsJoinSupportPawn,
  u8 m_ucJoinPawnNum, MtTypedArray<CDataRewardItemDetail>}` (V).
- PC element `0x77b080` (V): CDataQuestList, u32, **5 x bool** (PS4 4), u8, list `0x7772a0`
  CDataRewardItemDetail, **`0x75ed50`** {u32, list u32, list `0x75edd0` {u32, bool}, bool, bool, list
  u8 `0x75e9b0`}, **list `0x772ef0`** of {list CDataWalletPoint, list `0x7731b0` {u32,u16}} (S3).
  Which bool is new: I (Arrowgene order `IsNoTimeup, Unk0, IsJoinCharacter, IsJoinPawn, Unk1`).
  Arrowgene names the two new members `Restrictions` and `RequiredItemsList` (I).
- Walk: REQ 3/3 slack 3 (`138772`, `1c6f92d961a25d08`, GroupId 10). RES 3/3 slack 10;
  `stream85-…-11/138774` (288 B, `3d6139a629e377b4`): GroupId 10, type 4, 1 element, end 0x116. PS4
  body counter-test 0/3.

## 11. 11.14.1 GET_SET_QUEST_INFO_LIST_REQ / 11.14.2 …_RES

- PC writer `0x8388d0`: u32 (V); PS4 `0x19b98d0`: u32 `m_unDistributeID`.
- PC handler `0x7f2430`, reader `0x816e70`: RES header, u32, list `0x778160` of `0x778230`, u16, u16 (V).
  PS4 `ReadPacket 0x19d6490`: `u32 m_unDistributeID, MtTypedArray<CDataSetQuestInfoList>, u16
  m_usAreaBaseMinLevel, u16 m_usAreaBaseMaxLevel` (V).
- Element (PC `0x778230`, V) vs PS4 `0x1a1e150`:
  `u32 QuestScheduleId; u32 QuestId; u64 unk_u64 (S3, Arrowgene OrderDate, I); u64 EndDistributionDate;
  u32 ImageId; u32 BaseLevel; u16 ContentJoinItemRank; u32 DiscoverRewardItemId;
  MtTypedArray<CDataWalletPoint> DiscoverRewardWalletPoint (S3, replaces BonusGold/BonusRim, I);
  MtTypedArray<CDataQuestExp> DiscoverRewardExp (S3, replaces BonusExp, I); u32 QuickPartyPopularity;
  MtTypedArray<CDataCommonU32> SelectRewardItemIdList; u8 RandomRewardNum; u8 ChargeRewardNum; u16
  CompleteNum; bool IsDiscovery; MtTypedArray<CDataQuestEnemyInfo> (S3 4-field); MtTypedArray
  <CDataQuestLayoutFlagSetInfo>; MtTypedArray<CDataQuestDeliveryItem> (S3 shape);
  MtTypedArray<CDataQuestOrderConditionParam> (S3, new);` Which u64 is new: I.
- Walk: REQ 2/2 slack 3 (`11569`, `c7ae10bb491e1207`). RES 2/2 slack 4; `stream76-…-11/11572` (1984 B,
  `80b84c9713a8a4a5`), 15 elements, end 0x7bc. PS4 body 0/2.

## 12. Empty or u32/u8 requests 11.15.1, 11.19.1, 11.20.1, 11.23.1, 11.31.1, 11.32.1, 11.34.1, 11.37.1, 11.38.1, 11.39.1, 11.41.1, 11.42.1, 11.45.1, 11.56.1, 11.57.1, 11.62.1, 11.71.1

PC writer (all `WritePacket(p, 11, id, 1)`, V) and PS4 `Send_*` (V) agree; DWARF names:

| id | PC writer | PS4 writer | body | walk (fit, slack, sample, sha) |
| --- | --- | --- | --- | --- |
| 11.15.1 GET_CYCLE_CONTENTS_NEWS_LIST_REQ | `0x8370f0` | `0x19b9a10` | empty | 6/6, 7, `11553`, `0a34c153ffd49a14` |
| 11.19.1 GET_AREA_BONUS_LIST_REQ | `0x836e90` | `0x19b9c70` | empty | 182/182, 7, `12191`, `b1e0b013b8520057` |
| 11.20.1 QUEST_ORDER_REQ | `0x839900` | `0x19b83a0` | u32 QuestScheduleId | 1/1, 3, `11321`, `1250d3f3741ed97d` (`00024f85`) |
| 11.23.1 LIGHT_QUEST_GP_COMPLETE_REQ | `0x838f40` | `0x19b8d90` | u32 BaseId | 1/1, 3, `11354`, `9b1d90824c319bb3` |
| 11.31.1 GET_QUEST_COMPLETE_LIST_REQ | `0x838220` | `0x19b89d0` | u8 QuestType | 86/86, 6, `12169`, `3d6e2f204ea86d77` (`09`) |
| 11.32.1 SET_PRIORITY_QUEST_REQ | `0x839d50` | `0x19b12d0` | u32 QuestScheduleId | 3/3, 3, `11328`, `382593d93054643a` |
| 11.34.1 GET_PRIORITY_QUEST_REQ | `0x838160` | `0x19b1550` | empty | 45/45, 7, `12217`, `1e2e7e0f6e324118` |
| 11.37.1 GET_CYCLE_CONTENTS_STATE_LIST_REQ | `0x837530` | `0x19ba1e0` | empty | 41/41, 7, `11980`, `a37017daabed2883` |
| 11.38.1 GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_REQ | `0x837450` | `0x19ba310` | u32 CycleContentsScheduleId | 2/2, 3, `11664`, `b75086c0648a8cad` |
| 11.39.1 PLAY_ENTRY_REQ | `0x8391a0` | `0x19b2df0` | empty | 1/1, 7, `139304`, `570307925bc35f04` |
| 11.41.1 PLAY_START_REQ | `0x839400` | `0x19b3050` | u32 QuestScheduleId | 1/1, 3, `139313`, `77a570dc4fbab312` |
| 11.42.1 PLAY_START_TIMER_REQ | `0x8394e0` | `0x19ba810` | empty | 1/1, 7, `139435`, `fb4e7797ee8d21ad` |
| 11.45.1 PLAY_END_REQ | `0x839020` | `0x19b3190` | empty | 1/1, 7, `154698`, `b709800ce40f0785` |
| 11.56.1 GET_AREA_INFO_LIST_REQ | `0x836f50` | `0x19b9b40` | empty | 1/1, 7, `11563`, `73cc87d8683e39dd` |
| 11.57.1 GET_QUEST_PARTY_BONUS_LIST_REQ | `0x8384c0` | `0x19b9da0` | empty | 84/84, 7, `12175`, `8611d79fe782711f` |
| 11.62.1 GET_REWARD_BOX_LIST_REQ | `0x838858` (call `0x838883`, not a function) | `0x19b92a0` | empty | 8/8, 7, `25963`, `ae7ab3264cd7cb83` |
| 11.71.1 GET_PARTY_QUEST_PROGRESS_INFO_REQ | `0x8380a0` | `0x19b9660` | empty | 43/43, 7, `12199`, `f769932c611258f0` |

(Samples are under `packets/decrypted_raw/<stream>/<number>_…`; empty bodies end at 0x09.) The triage
`pc_va 0x838883` of 11.62.1 is the `WritePacket` call itself, inside an undefined code range.

## 13. 11.20.2 QUEST_ORDER_RES

PC handler `0x7f4650`, reader `0x818310`: RES header, list `0x775310` CDataQuestProcessState (V). PS4
`0x2ec290`: `MtTypedArray<CDataQuestProcessState> m_QuestProcessStateList` (V). No Season 3 change.
Walk 1/1 slack 3, `stream62-…-11/11322` (64 B, `1064df823c1b5fcf`), 1 state, end 0x3d.

## 14. 11.21.1 QUEST_PROGRESS_REQ / 11.21.2 …_RES

- PC writer `0x841fe0` (11,21,1): u32, u32, u32, u16 (V). PS4 `CPacket_C2S_QUEST_PROGRESS_REQ::WritePacket
  0x1a376a0`: `u32 m_unKeyId, u32 m_unProgressCharacterId, u32 m_unQuestScheduleId, u16 m_usProcessNo` (V).
- PC handler `0x7f4850` (not a function), reader `0x818490`: RES header, u8, u32, list CDataQuestProcessState
  (V). PS4 `ReadPacket 0x19d6530`: `u8 m_ucQuestProgressResult, u32 m_unQuestScheduleId,
  MtTypedArray<CDataQuestProcessState>` (V). No Season 3 change.
- Walk: REQ 705/705 slack 9 (`12275`, 32 B, `0610f68d8a4662e2`: KeyId 1, CharId 0, Schedule `0x61f5`,
  ProcessNo 0x10, end 0x17). RES 705/705 slack 0-14, up to 4 states; `12344` (368 B, `8bb5fbc864dc1a93`),
  end 0x16e.

## 15. 11.23.2 LIGHT_QUEST_GP_COMPLETE_RES

PC handler `0x7f2d00`, reader `0x817650`: RES header, u32, list CDataQuestIdScheduleId (V). PS4
`0x2eca50`: `u32 m_unBaseID, MtTypedArray<CDataQuestIdScheduleId> m_CompleteQuestList` (V). Walk 1/1
slack 15, `stream85-…-11/11371` (48 B, `4f129b40d879c217`): BaseId `0x1c`, 1 x {`0266ee3a`,
`0006091e`}, end 0x21.

## 16. 11.31.2 GET_QUEST_COMPLETE_LIST_RES

PC handler `0x7f1df0` (not a function), reader `0x8169c0`: RES header, u8, list u32 (V). PS4 `0x2ed580`:
`u8 m_ucQuestType, MtTypedArray<CDataQuestId>` (V). Walk 86/86 slack 2-14, up to 82 ids;
`stream85-…-11/121462` (352 B, `c28000f13211ae7f`), end 0x15a.

## 17. 11.32.2 SET_PRIORITY_QUEST_RES, 11.33.2 CANCEL_PRIORITY_QUEST_RES

PC readers `0x818c10` (handler `0x7f5630`) and `0x814e10` (handler `0x7ef6c0`, both not functions for
11.33.2): RES header, u32 (V). PS4 `0x2ed720`/`0x2ed880`: `u32 m_unQuestScheduleId` (V). Walk 3/3 and
2/2, slack 11; `stream62-…-11/11330` (`8e0851ac8ea03c94`) and `…/11714` (`826105916ccea1a1`):
`00024f85`, end 0x15.

## 18. 11.32.16 SET_PRIORITY_QUEST_NTC

PC handler `0x7f5570`, reader `0x818ba0`: **no header**, u32, list CDataPriorityQuest (V). PS4
`OnPacket_S2C_SET_PRIORITY_QUEST_NOTICE 0x2ed9e0`: `u16 m_usError, CPriorityQuestSetting {u32
m_unCharacterId, MtTypedArray<CDataPriorityQuest>}` (V). Wire `u32 CharacterId;
MtTypedArray<CDataPriorityQuest> PriorityQuestList;`. Walk 5/5 slack 3-15, up to 3 quests;
`stream62-…-11/11332` (80 B, `cc2992a47b8cb24a`), CharacterId `0x00204fd8`, end 0x4d. PS4 framing
(u16 first) 0/5.

## 19. 11.34.2 GET_PRIORITY_QUEST_RES

PC handler `0x7f1d40`, reader `0x816940` (both not functions): RES header, list `0x773710` of {u32, list
CDataPriorityQuest} (V). PS4 `0x2edba0`: `MtTypedArray<CDataPriorityQuestSetting>` (V). Walk 45/45 slack
3-15; `stream85-…-11/139075` (144 B, `7b0076819aafc2c1`), end 0x81.

## 20. 11.38.2 GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_RES

PC handler `0x7f0f60`, reader `0x815f80`: RES header, u32, list {u32, u32} (V). PS4 `0x2ee590`: `u32
m_unCycleContentsScheduleId, MtTypedArray<CDataQuestContentsSituationInfo>` (V). Walk 2/2 slack 7;
`stream76-…-11/11666` (48 B, `7bf1aff4b212366e`): `50b1`, 2 x {schedule, quest}, end 0x29.

## 21. 11.39.2 PLAY_ENTRY_RES, 11.41.2 PLAY_START_RES, 11.42.2 PLAY_START_TIMER_RES, 11.45.2 PLAY_END_RES

PC readers `0x817ba0`, `0x817e10`, `0x817f00`, `0x817a80` (handlers `0x7f3610`, `0x7f3db0`, `0x7f3f10`,
`0x7f3300`): RES header only (V). PS4 `0x2ee960`, `0x2eeea0` (`s32 m_nResult`), `0x2ef5e0`, `0x2f0580`
(`u32 m_unResult`: PS4 declares Result unsigned for the TIMER and END pair; PC reads `Read_s32` for all
four, V). Walks 1/1 each, slack 15, samples `139308` (`5b8c3dc04281b5b2`), `139317`
(`56660cef51894316`), `139445` (`10033d1c0464979a`), `154701` (`815f91215f6eb8e0`), all `00000000
00000000`, end 0x11.

## 22. 11.39.16 S2C_QUEST_PLAY_ENTRY_NTC (unresolved -> matched, V by behaviour)

- PC handler `0x7f3530` reads `u32` inline (no header), looks the id up in the party manager
  (`sub_5C4F30`), sets member byte +77 = 1, finds the member index (`sub_40B4C0`) and calls a GUI vfunc
  `(index, 1)`. PS4 `OnPacket_S2C_PLAY_ENTRY_NOTICE 0x2eeab0`: `Read_u16 m_usError, Read_u32
  m_unCharacterID`, finds the party member with that CharacterID, sets its entry byte = 1, then calls
  the same GUI vfunc with `(index, 1)` (V, same behaviour).
- Wire `u32 CharacterId;` (4 B). Walk 1/1 slack 3, `stream85-…-11/139309` (16 B, `d7248b70be2896bf`):
  `0021559b`, end 0xd.

## 23. 11.45.16 S2C_QUEST_PLAY_END_NTC

- PC handler `0x7f3270` (not a function), reader `0x817a10` (not a function): **`Read_s32` into +16** (the
  slot RES readers use for Error), read unconditionally, then `0x75ef90` = **7 x u32** + list CDataRewardItemDetail
  (V). Handler pushes `cQuestSvNotEndContentsPlayEnd` (`dti__1498`, V) and requests the quest complete
  list (`sub_BE8890`, I), as PS4 `OnPacket_S2C_PLAY_END_NOTICE 0x2f0690` (`u16 m_usError,
  CContentsPlayEnd {u32 m_unGold, m_unExp, m_unRim, m_unPlayTimeMillSec, MtTypedArray<CDataRewardItemDetail>}`,
  pushes `cQuestSvNotEndContentsPlayEnd`, `requestGetQuestCompleteList(TIME_GAIN)`) (V).
- Season 3: s32 lead field and 3 more u32. **Field order (I, capture)**: the only capture has the 7th u32 =
  `0x000ff3d5` = 1,045,461 and the others 0; PLAY_START (`139317`, 13:33:43) to this NTC (13:51:21) is
  1,058 s, so the 7th u32 is the play time in ms. Proposed: `s32 unk_s32; u32 Gold; u32 Exp; u32 Rim;
  u32 unk_u32_0; u32 unk_u32_1; u32 unk_u32_2; u32 PlayTimeMillSec; MtTypedArray<CDataRewardItemDetail>`
  (the three middle names I).
- Walk 1/1 slack 12, `stream85-…-11/154701_S2C_QUEST_PLAY_END_NTC` (64 B, `e81eb0f19ce8748f`), 1 reward
  {`00006098`, …}, end 0x34. PS4 body 0/1.

## 24. 11.57.2 GET_QUEST_PARTY_BONUS_LIST_RES

PC handler `0x7f1ff0`, reader `0x816b50`: RES header, list `0x774cf0` CDataQuestPartyBonusInfo, u64 (V).
PS4 `0x2f2b90`: `MtTypedArray<CDataQuestPartyBonusInfo>, u64 m_ullNextReloadTime` (V). No change. Walk
84/84 slack 4, up to 19 elements; `12176` (432 B, `3242435d19345ac4`), end 0x1ac.

## 25. 11.60.16 C2S_QUEST_11_60_16_NTC = C2S PRT_READY_SET_RETURN_SESSION (unresolved -> matched, V by behaviour)

- PC writer `0x8395a0` (11,60,16): `Write_bool` (V); only sender `sub_883B30` checks connection + login,
  stores the flag at `this+40294`, sends. Callers: `cPRTManager::updatePRT` (x2, PC name in the database)
  and `0x9b1a60` (stores `+2064`, sends if `a3 == 1`).
- PS4: `cNetGameServer::setReturnSessionForPRT 0x350630` checks connection + login, stores
  `mReqReturnSession = isReturnSession`, calls `Send_C2S_PRT_READY_SET_RETURN_SESSION 0x19ba090` (header +
  `Write_bool`); callers `cPRTManager::updatePRT 0x529ca0` (x2) and `cPRTManager::setReturnSession 0x52a3e0`
  (V, same shape and callers). DWARF `CPacket_C2S_PRT_READY_SET_RETURN_SESSION {u16 m_usError, b8
  m_bIsReturnSession}`.
- Wire `bool IsReturnSession;` (1 B). Walk 7/7 slack 6, `stream85-…-11/106978` (16 B,
  `82eddbe58163ae2f`): `00`, end 0xa.

## 26. 11.62.2 GET_REWARD_BOX_LIST_RES

PC handler `0x7f2370`, reader `0x816df0`: RES header, list `0x777080` of {u32, u32, list `0x776f20` of
`0x777000` {u32, u16, MtString, u8, bool, bool}} (V). PS4 `0x3120b0`: `MtTypedArray<CDataRewardBoxRecord>
{u32 m_unListNo, u32 m_unQuestId, MtTypedArray<CDataRewardBoxItem> {u32 m_unItemId, u16 m_usNum, MtString
m_wstrUID, u8 m_ucType, b8 m_bIsCharge, b8 m_bIsHelp}}` (V). No change. Walk 8/8 slack 4-15, up to 91
records; `stream1-…-35/25965` (528 B, `0b9bb1e54c1c94d4`), end 0x204.

## 27. 11.64.1 GET_REWARD_BOX_ITEM_REQ / 11.64.2 …_RES

- PC writer `0x838720` (11,64,1): u32, `0x77faf0` = u32 count + `Write_MtString` each (V). PS4
  `CPacket_C2S_GET_REWARD_BOX_ITEM_REQ::WritePacket 0x1a37500`: `u32 m_unListNo,
  MtTypedArray<CDataGetRewardBoxItem {MtString m_wstrUID}>` (V).
- PC handler `0x7f2230`, reader `0x816ce0`: RES header only (V); PS4 `0x312650` same.
- Walk: REQ 6/6 slack 1-7, up to 4 UIDs; `stream85-…-11/159022` (64 B, `7cff62874753f5ff`): ListNo
  `0x5a`, 4 x 8-char UID, end 0x39. RES 6/6 slack 15 (`26145`, `1824a9ce08b9706a`).

## 28. 11.68.16 S2C_QUEST_QUEST_BOARD_RELOAD_NTC (unresolved -> Season 3-exclusive, I)

- PC handler `0x7f2be0` (packet object 11/68/16), reader `0x8175d0`: bool, bool, u32 (V, no header). If
  the first bool is set it adds chat message 0x132; if the second is set, message 0x133 with `%d` of the
  u32 (V). No notice class.
- No PS4 counterpart found: no PS4 `OnPacket_*` (781 decompiled) reads `u16, bool, bool, u32`; the only
  three that both read a bool and call `sChat::addMessage` are PLAY_INTERRUPT_RESULT, APPLY_FRIEND and
  APPROVE_FRIEND notices (unrelated). Exclusive by absence, **I** (the PC messages could not be compared
  to PS4 text ids).
- Wire `bool unk_bool0; bool unk_bool1; u32 Count;` (names: Arrowgene `Unk0, Unk1, Count`, I). Walk 1/1
  slack 1, `stream85-…-11/11369` (16 B, `1effab9a2551313d`): `01 01 00000001`, end 0xf.

## 29. 11.69.1 DELIVER_ITEM_REQ / 11.69.2 …_RES / 11.69.16 …_NTC

- PC writer `0x836b40` (11,69,1): u32, u16, `0x77fd30` = u32 count + {MtString, u32} (V). PS4
  `CPacket_C2S_DELIVER_ITEM_REQ::WritePacket 0x1a372b0`: `u32 m_unQuestScheduleId, u16 m_usProcessNo,
  MtTypedArray<CDataItemUIDList {MtString m_wstrUID, u32 m_unNum}>` (V).
- RES: PC handler `0x7f0330`, reader `0x815750`: header, u32, u16 (V); PS4 `0x312ca0` `u32
  m_unQuestScheduleId, u16 m_usProcessNo` (V).
- NTC: PC handler `0x7f0260`, reader `0x8156c0`: **no header**, u32, u32, u16, list `0x762d80` {u32, u16,
  u16} (V). PS4 `0x312de0`: `u16 m_usError, CDeliveredItemRecord {u32 m_unCharacterId, u32
  m_unQuestScheduleId, u16 m_usProcessNo, MtTypedArray<CDataDeliveredItem>}` (V). = Quest.hexpat
  `CDataDeliveredItemRecord`.
- Walks 1/1 each: REQ slack 15 (`11658`, 48 B, `a4957cca54f51906`: `00024f85 0000`, 1 x {"79AC3B12", 1},
  end 0x21); RES slack 9 (`11661`, `6fc85e916c984df1`); NTC slack 1 (`11663`, 32 B, `29f3117807a87382`:
  `00204fd8 00024f85 0000`, 1 x {`0547`, 1, 1}, end 0x1f). PS4 framing on the NTC 0/1.

## 30. 11.70.1 DECIDE_DELIVERY_ITEM_REQ / 11.70.2 …_RES / 11.70.16 …_NTC (NTC: unresolved -> matched, V)

- REQ: PC `0x836a50` u32, u16 (V); PS4 `0x19b9500` `u32 m_unQuestScheduleId, u16 m_usProcessNo` (V).
- RES: PC handler `0x7f01c0`, reader `0x815630`: header, u32, u16 (V); PS4 `0x313000` same (V).
- NTC: PC handler `0x7f0130`, reader `0x8155c0`: u32, u32, no header (V); pushes
  `cQuestSvNotDecideDeliveryItem` (`dti__1497`). PS4: the class's only `OnPacket` is
  `OnPacket_S2C_DECIDE_DELIVERY_ITEM_NOTICE 0x313140` (`u16 m_usError, u32 m_unQuestScheduleId, u32
  m_unProcessNo`) (V). Wire `u32 QuestScheduleId; u32 ProcessNo;`.
- Walks 1/1 each: REQ slack 1 (`11706`, `5b6bbd9a95ee43aa`), RES slack 9 (`11707`, `cdcb14b93ccdb5ab`),
  NTC slack 15 (`11708`, 32 B, `55ab7eef6cad1470`: `00024f85 00000000`, end 0x11).

## 31. 11.83.16 S2C_QUEST_11_83_16_NTC = SET_QUEST_UNRELEASED_AREA_NOTICE (unresolved -> matched, V)

PC handler `0x7f56d0`, reader `0x818c90` = list u32 `0x75e8e0` (no header) (V); pushes
`cQuestSvNotSetQuestUnreleasedArea` (`dti__1524`). PS4 only user of that class:
`OnPacket_S2C_SET_QUEST_UNRELEASED_AREA_NOTICE 0x2ea270`: `u16 m_usError, MtTypedArray<CDataCommonU32>
m_AreaIdList` (V). Wire `MtTypedArray<CDataCommonU32> AreaIdList;`. Walk 20/20 slack 15, up to 9 ids;
`stream1-…-35/12006` (64 B, `a0b8d36dce9f4d86`): 9 x area id `0d..15`, end 0x31. PS4 framing 0/20.

## 32. 11.88.16 S2C_QUEST_11_88_16_NTC (unresolved; reason)

PC handler `0x7f15e0` is `return 1;` (8 bytes): it reads nothing and does nothing (V). Wire: empty body.
Walk 20/20 slack 7, `stream21-…-48/12482` (16 B, `d214e8b4e919e4c3`), end 0x09. **Not settled**: with
no read and no behaviour on PC, neither the shape (45 PS4 bodies read nothing past the error) nor
behaviour can select a PS4 counterpart.

## 33. 11.90.16 QUEST_PROGRESS_WORK_SAVE_NTC

PC handler `0x7f4910`, reader `0x818530`: u32, u16, u16, u16, list CDataQuestProgressWork (no header, V);
pushes `cQuestSvNotQuestProgressWorkSave` (`dti__1516`). PS4 `ReadPacket 0x19d6700`: `u16 m_usError, u32
m_unQuestScheduleId, u16 m_usProcessNo, u16 m_usSequenceNo, u16 m_usBlockNo,
MtTypedArray<CDataQuestProgressWork> m_WorkList` (V). Walk 11/11 slack 5; `stream85-…-11/101161` (48 B,
`59fecc930c8ac3df`), end 0x2b. PS4 framing 0/11.

## 34. 11.91.16 QUEST_COMPLETE_NTC

PC handler `0x7f4310`, reader `0x818100`: u32, 7 x u8 (no header, V); pushes `cQuestSvNotQuestComplete`
(`dti__1512`). PS4 `ReadPacket 0x19d67c0`: `u16 m_usError, u32 m_unQuestScheduleId, u8
m_ucRandomRewardNum, m_ucChargeRewardNum, m_ucProgressBonusNum, m_ucIsRepeatReward, m_ucIsUndiscoverReward,
m_ucIsHelpReward, m_ucIsPartyBonus` (V; recompilation S2C.cpp:9520 has the same body). Walk 4/4 slack 12,
`stream62-…-11/11714` (32 B, `34515d3820112993`), end 0x14.

## 35. 11.95.16 S2C_QUEST_11_95_16_NTC = FORT_DEFENSE_NOTICE (unresolved -> matched, V)

- PC handler `0x7f0480`, reader `0x815860` (no header): list `0x766c00` of `0x761970` {u32, u32, u32, u32,
  **u64, u64**, u8, u8, u8, bool, bool, list CDataQuestProcessState}, list `0x773ba0` of `0x773c60` {u32,
  u32, u32, u16, u8, list CondParam, list CDataRewardItem, u32, **list `0x77c780` {u32, u32}**, bool} (V);
  pushes `cQuestSvNotCycle01Phase` (`dti__1492`).
- PS4 only user of `cQuestSvNotCycle01Phase`: `OnPacket_S2C_FORT_DEFENSE_NOTICE 0x2edea0`: `u16 m_usError,
  MtTypedArray<CDataFortDefenseNoticeData {CCycleContentsNoticeData m_Common}>,
  MtTypedArray<CDataQuestContentsSituationInfoDetail>`; `CDataCycleContentsNoticeData {u32
  m_unCycleContentsScheduleId, u32 m_unQuestScheduleId, u32 m_unQuestId, u32 m_unCategoryType, u64 m_ullEnd,
  u8 m_ucNoticeType, u8 m_ucIsSystemNotice, u8 m_ucPartyMemberNum, b8 m_bIsPlay, b8 m_bIsGetReward,
  MtTypedArray<CDataQuestProcessState>}`; detail `{u32 m_unQuestScheduleId, u32 m_unQuestId, u32
  m_unBaseLevel, u16 m_usContentJoinItemRank, u8 m_ucNoticeType, MtTypedArray<CDataQuestOrderConditionParam>,
  MtTypedArray<CDataRewardItem> m_RewardItemList, u32 m_unClearTimePointBonus, b8 m_bIsEnable}` (V).
- Season 3: a second u64 in the notice data (which one is new: I) and a list {u32, u32} before IsEnable
  (S3, names I).
- Walk 48/48 slack 1-11, up to 2 + 3 elements; `stream1-…-35/12009` (544 B, `a442e82cfcf2bd4e`), end
  0x21f. PS4 body counter-test 0/48.

## 36. 11.101.16 TIME_GAIN_QUEST_PLAY_START_NTC

PC handler `0x7f5830`, reader `0x75f030` (no header, V): `u32 KeyId; u32 QuestScheduleId; u32 QuestId; u32
BaseLevel; u8 StartPos; bool x3 (S3); MtTypedArray<CDataQuestProcessState>;
MtTypedArray<CDataQuestEnemyInfo> (S3 4-field); MtTypedArray<CDataQuestLayoutFlagSetInfo>;
MtTypedArray<CDataCommonU32> QuestPhaseGroupIdList; MtTypedArray<u8> (S3, `0x75e9b0`)`. PS4 `0x2eeff0`:
`u16 m_usError, CTimeGainQuestPlayStartData` = `CDataContentsPlayStartData` (`0x1a2df70`) without the 3
bools and the u8 list (V). Walk 1/1 slack 2, `stream85-…-11/139317_…_11_101_16` (448 B,
`b26fd282c5e7edf9`), end 0x1be. PS4 body 0/1.

## 37. 11.103.16 S2C_QUEST_11_103_16_NTC = PLAY_STOP_TIMER_NOTICE (unresolved -> matched, V)

PC handler `0x7f3fa0` reads nothing, builds a packet object (11/103/16) and pushes `cQuestSvNotStopTimer`
(`dti__1525`) (V). PS4 only user: `OnPacket_S2C_PLAY_STOP_TIMER_NOTICE 0x2ef890` (`u16 m_usError` only)
(V). Wire: empty. Walk 1/1 slack 7, `stream85-…-11/154682` (16 B, `c0254f7f774e32d9`), end 0x09.

## 38. 11.117.16 S2C_QUEST_11_117_16_NTC = REWARD_BOX_LIST_NUM_NOTICE (unresolved -> matched, V by behaviour; Season 3 fields)

- PC handler `0x7f4e10` (11/117/16), reader `0x818760`: u16, u16, u8 (no header, V). It stores the u8 in
  the manager (`+40272`), and, once per session (GUI flag), adds chat message 0xCA when it is non-zero;
  then announces 0xDA (u8 >= 100) or 0x34 (u8 >= 80), and 0x12C (first u16 >= second u16) or 0x12D
  (first >= 80 % of second).
- PS4 `OnPacket_S2C_REWARD_BOX_LIST_NUM_NOTICE 0x312390`: `u16 m_usError, u8 m_ucListNum`, stores
  `mpManager->mRecvGetRewardBoxListNum` and, under the same GUI flag, adds message 0xCA when non-zero (V,
  same behaviour). Season 3 adds the two u16 and the fill-level announcements.
- Wire `u16 unk_u16_count; u16 unk_u16_capacity; u8 ListNum;` (u16 roles I from the 80 % logic).
  Walk 47/47 slack 2, `stream1-…-35/11973` (16 B, `5d9a50060c0552c7`): `0015 0320 08` (21 of 800, 8),
  end 0xe. The PS4 body (u8 only) also fits (47/47, slack): the two u16 rest on the code.

## 39. 11.118.16 S2C_QUEST_11_118_16_NTC (unresolved; reason)

PC handler `0x7f2e50` reads one u8 into a local and returns (V): the client ignores it. Wire `u8 unk_u8;`.
Walk 41/41 slack 6, `stream1-…-35/11975` (16 B, `3ab364265ce8ec3f`): `00`, end 0xa. **Not settled**: 7
PS4 notices read `u16 + u8` (e.g. NOT_RECV_CYCLE_CONTENTS_REWARD_LIST_NUM_NOTICE `0x312a90`); a no-op PC
handler offers no behaviour to compare. (REWARD_BOX_LIST_NUM is 11.117.16, § 38.)

## 40. 11.121.1 GET_LEVEL_BONUS_LIST_REQ / 11.121.2 …_RES (Season 3-exclusive, confirmed)

No PS4 symbol, string or DWARF type with `LEVEL_BONUS`/`LevelBonus` (V). PC writer `0x837790` empty (V);
handler `0x7f1320`, reader `0x8161c0`: RES header, list `0x75a600` of {u32, list `0x76cf70` of `0x76d050`
{u32, u32, u16, u16, u16, u16}} (V). Wire `MtTypedArray<CDataLevelBonus {u32 unk_u32;
MtTypedArray<CDataLevelBonusElement {u32 MinLevel; u32 MaxLevel; u16 GoldRatio; u16 ExpRatio; u16
RimRatio; u16 AreaPointRatio;}> BonusList;}>` (names Arrowgene, I). Walk REQ 182/182 slack 7 (`12196`,
`990577df5241f79c`); RES 182/182 slack 3, always 1 element; `12197` (48 B, `7f48df0992a49c37`): {`1c`, 1
x {1, `0x59`, 100, 2000, 100, 100}}, end 0x2d.

## 41. 11.122.1 GET_ADVENTURE_GUIDE_QUEST_LIST_REQ / 11.122.2 …_RES (Season 3-exclusive, confirmed)

No PS4 symbol, string or type with `ADVENTURE_GUIDE`/`AdventureGuide` (V). PC writer `0x836d10` empty;
handler `0x7f07d0`, reader `0x815a20`: RES header, list `0x758bc0` of {u8, **CDataQuestOrderList
`0x774a70`** (Quest.hexpat type, V), bool, bool, u32} (V). Wire `MtTypedArray<{u8 Category;
CDataQuestOrderList Param; bool Important; bool unk_bool; u32 QuestOrderBackgroundImage;}>` (names
Arrowgene `CDataQuestAdventureGuideList`, I). Walk REQ 45/45 slack 7 (`12579`, `a81de62dd92c0c0e`); RES
45/45 slack 4-15, up to 20 elements; `12582` (2304 B, `779a10ba716f5fa0`), end 0x8f7.

## 42. 11.123.1 GET_ADVENTURE_GUIDE_QUEST_NTC_REQ / 11.123.2 …_RES (Season 3-exclusive, confirmed)

Same absence (V). PC writer `0x836dd0` empty; handler `0x7f0880`, reader `0x815aa0`: RES header, bool (V).
Walk REQ 155/155 slack 7 (`12264`, `ed4c9bb018116c9f`); RES 155/155 slack 14 (`12265`, 32 B,
`4006a3d38a76d8d7`: bool 1, end 0x12).

## 43. Summary

PS4 mark: V = confirmed by code (symbol + body, notice class, or behaviour); X = no PS4 counterpart
(confirmed by code); X(I) = no counterpart found, inferred; U = unresolved (reason in section). Body bytes
for Error == 0 (lists as `+kn`; var = nested lists).

| id | name (file) | PS4 | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 11.0.1 | C2S_QUEST_GET_LIGHT_QUEST_LIST_REQ | V | 4 | 11307 | 1/1 |
| 11.0.2 | S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | V (S3 QuestList, detail +u32, contents +2 u16) | var | 11308 | 1/1 |
| 11.1.1 | C2S_QUEST_GET_SET_QUEST_LIST_REQ | V | 4 | 12178 | 179/179 |
| 11.1.2 | S2C_QUEST_GET_SET_QUEST_LIST_RES | V (S3 QuestList, detail lists) | var | 12185 | 179/179 |
| 11.2.1 | C2S_QUEST_GET_MAIN_QUEST_LIST_REQ | V | 0 | 12166 | 44/44 |
| 11.2.2 | S2C_QUEST_GET_MAIN_QUEST_LIST_RES | V (S3 QuestList) | var | 12167 | 44/44 |
| 11.3.1 | C2S_QUEST_GET_TUTORIAL_QUEST_LIST_REQ | V | 4 | 12238 | 146/146 |
| 11.3.2 | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | V (S3 QuestList) | var | 12257 | 146/146 |
| 11.4.1 | C2S_QUEST_GET_LOT_QUEST_LIST_REQ | V | 4 | 13011 | 20/20 |
| 11.4.2 | S2C_QUEST_GET_LOT_QUEST_LIST_RES | V (S3 QuestList, contents) | var | 11248 | 20/20 |
| 11.5.1 | C2S_QUEST_GET_PACKAGE_QUEST_LIST_REQ | X | 4 | 12260 | 146/146 |
| 11.5.2 | S2C_QUEST_GET_PACKAGE_QUEST_LIST_RES | X | 12+var (always empty) | 12261 | 146/146 |
| 11.7.16 | S2C_QUEST_11_7_16_NTC (MobHuntQuestListNum) | X (candidate C) | 4+5n | 12236 | 43/43 |
| 11.9.1 | C2S_QUEST_GET_WORLD_MANAGE_QUEST_LIST_REQ | V | 0 | 12163 | 42/42 |
| 11.9.2 | S2C_QUEST_GET_WORLD_MANAGE_QUEST_LIST_RES | V (S3 QuestList, code-only) | 12+var | 12164 | 42/42 |
| 11.10.1 | C2S_QUEST_GET_END_CONTENTS_GROUP_REQ | V | 4 | 138772 | 3/3 |
| 11.10.2 | S2C_QUEST_GET_END_CONTENTS_GROUP_RES | V (S3 bool, 2 members) | var | 138774 | 3/3 |
| 11.14.1 | C2S_QUEST_GET_SET_QUEST_INFO_LIST_REQ | V | 4 | 11569 | 2/2 |
| 11.14.2 | S2C_QUEST_GET_SET_QUEST_INFO_LIST_RES | V (S3 u64, lists) | var | 11572 | 2/2 |
| 11.15.1 | C2S_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_REQ | V | 0 | 11553 | 6/6 |
| 11.19.1 | C2S_QUEST_GET_AREA_BONUS_LIST_REQ | V | 0 | 12191 | 182/182 |
| 11.20.1 | C2S_QUEST_QUEST_ORDER_REQ | V | 4 | 11321 | 1/1 |
| 11.20.2 | S2C_QUEST_QUEST_ORDER_RES | V | var | 11322 | 1/1 |
| 11.21.1 | C2S_QUEST_QUEST_PROGRESS_REQ | V | 14 | 12275 | 705/705 |
| 11.21.2 | S2C_QUEST_QUEST_PROGRESS_RES | V | 13+var | 12344 | 705/705 |
| 11.23.1 | C2S_QUEST_LIGHT_QUEST_GP_COMPLETE_REQ | V | 4 | 11354 | 1/1 |
| 11.23.2 | S2C_QUEST_LIGHT_QUEST_GP_COMPLETE_RES | V | 16+8n | 11371 | 1/1 |
| 11.31.1 | C2S_QUEST_GET_QUEST_COMPLETE_LIST_REQ | V | 1 | 12169 | 86/86 |
| 11.31.2 | S2C_QUEST_GET_QUEST_COMPLETE_LIST_RES | V | 13+4n | 121462 | 86/86 |
| 11.32.1 | C2S_QUEST_SET_PRIORITY_QUEST_REQ | V | 4 | 11328 | 3/3 |
| 11.32.2 | S2C_QUEST_SET_PRIORITY_QUEST_RES | V | 12 | 11330 | 3/3 |
| 11.32.16 | S2C_QUEST_SET_PRIORITY_QUEST_NTC | V | 8+var | 11332 | 5/5 |
| 11.33.2 | S2C_QUEST_CANCEL_PRIORITY_QUEST_RES | V | 12 | 11714 | 2/2 |
| 11.34.1 | C2S_QUEST_GET_PRIORITY_QUEST_REQ | V | 0 | 12217 | 45/45 |
| 11.34.2 | S2C_QUEST_GET_PRIORITY_QUEST_RES | V | 12+var | 139075 | 45/45 |
| 11.37.1 | C2S_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_REQ | V | 0 | 11980 | 41/41 |
| 11.38.1 | C2S_QUEST_GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_REQ | V | 4 | 11664 | 2/2 |
| 11.38.2 | S2C_QUEST_GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_RES | V | 16+8n | 11666 | 2/2 |
| 11.39.1 | C2S_QUEST_PLAY_ENTRY_REQ | V | 0 | 139304 | 1/1 |
| 11.39.2 | S2C_QUEST_PLAY_ENTRY_RES | V | 8 | 139308 | 1/1 |
| 11.39.16 | S2C_QUEST_PLAY_ENTRY_NTC | V behaviour `PLAY_ENTRY_NOTICE` | 4 | 139309 | 1/1 |
| 11.41.1 | C2S_QUEST_PLAY_START_REQ | V | 4 | 139313 | 1/1 |
| 11.41.2 | S2C_QUEST_PLAY_START_RES | V | 8 | 139317 | 1/1 |
| 11.42.1 | C2S_QUEST_PLAY_START_TIMER_REQ | V | 0 | 139435 | 1/1 |
| 11.42.2 | S2C_QUEST_PLAY_START_TIMER_RES | V | 8 | 139445 | 1/1 |
| 11.45.1 | C2S_QUEST_PLAY_END_REQ | V | 0 | 154698 | 1/1 |
| 11.45.2 | S2C_QUEST_PLAY_END_RES | V | 8 | 154701 | 1/1 |
| 11.45.16 | S2C_QUEST_PLAY_END_NTC | V (S3 s32 + 3 u32) | 36+7n | 154701 | 1/1 |
| 11.56.1 | C2S_QUEST_GET_AREA_INFO_LIST_REQ | V | 0 | 11563 | 1/1 |
| 11.57.1 | C2S_QUEST_GET_QUEST_PARTY_BONUS_LIST_REQ | V | 0 | 12175 | 84/84 |
| 11.57.2 | S2C_QUEST_GET_QUEST_PARTY_BONUS_LIST_RES | V | 20+21n | 12176 | 84/84 |
| 11.60.16 | C2S_QUEST_11_60_16_NTC | V behaviour `PRT_READY_SET_RETURN_SESSION` | 1 | 106978 | 7/7 |
| 11.62.1 | C2S_QUEST_GET_REWARD_BOX_LIST_REQ | V | 0 | 25963 | 8/8 |
| 11.62.2 | S2C_QUEST_GET_REWARD_BOX_LIST_RES | V | 12+var | 25965 | 8/8 |
| 11.64.1 | C2S_QUEST_GET_REWARD_BOX_ITEM_REQ | V | 8+var | 159022 | 6/6 |
| 11.64.2 | S2C_QUEST_GET_REWARD_BOX_ITEM_RES | V | 8 | 26145 | 6/6 |
| 11.68.16 | S2C_QUEST_QUEST_BOARD_RELOAD_NTC | X(I) | 6 | 11369 | 1/1 |
| 11.69.1 | C2S_QUEST_DELIVER_ITEM_REQ | V | 10+var | 11658 | 1/1 |
| 11.69.2 | S2C_QUEST_DELIVER_ITEM_RES | V | 14 | 11661 | 1/1 |
| 11.69.16 | S2C_QUEST_DELIVER_ITEM_NTC | V | 14+8n | 11663 | 1/1 |
| 11.70.1 | C2S_QUEST_DECIDE_DELIVERY_ITEM_REQ | V | 6 | 11706 | 1/1 |
| 11.70.2 | S2C_QUEST_DECIDE_DELIVERY_ITEM_RES | V | 14 | 11707 | 1/1 |
| 11.70.16 | S2C_QUEST_DECIDE_DELIVERY_ITEM_NTC | V notice class | 8 | 11708 | 1/1 |
| 11.71.1 | C2S_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_REQ | V | 0 | 12199 | 43/43 |
| 11.83.16 | S2C_QUEST_11_83_16_NTC | V notice class `SET_QUEST_UNRELEASED_AREA_NOTICE` | 4+4n | 12006 | 20/20 |
| 11.88.16 | S2C_QUEST_11_88_16_NTC | U (no-op handler) | 0 | 12482 | 20/20 |
| 11.90.16 | S2C_QUEST_PROGRESS_WORK_SAVE_NTC | V | 14+20n | 101161 | 11/11 |
| 11.91.16 | S2C_QUEST_QUEST_COMPLETE_NTC | V | 11 | 11714 | 4/4 |
| 11.95.16 | S2C_QUEST_11_95_16_NTC | V notice class `FORT_DEFENSE_NOTICE` (S3 u64, list) | var | 12009 | 48/48 |
| 11.101.16 | S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC | V (S3 3 bools, u8 list) | var | 139317 | 1/1 |
| 11.103.16 | S2C_QUEST_11_103_16_NTC | V notice class `PLAY_STOP_TIMER_NOTICE` | 0 | 154682 | 1/1 |
| 11.117.16 | S2C_QUEST_11_117_16_NTC | V behaviour `REWARD_BOX_LIST_NUM_NOTICE` (S3 2 u16) | 5 | 11973 | 47/47 |
| 11.118.16 | S2C_QUEST_11_118_16_NTC | U (handler discards the u8) | 1 | 11975 | 41/41 |
| 11.121.1 | C2S_QUEST_GET_LEVEL_BONUS_LIST_REQ | X | 0 | 12196 | 182/182 |
| 11.121.2 | S2C_QUEST_GET_LEVEL_BONUS_LIST_RES | X | var | 12197 | 182/182 |
| 11.122.1 | C2S_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_REQ | X | 0 | 12579 | 45/45 |
| 11.122.2 | S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_RES | X | var | 12582 | 45/45 |
| 11.123.1 | C2S_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_REQ | X | 0 | 12264 | 155/155 |
| 11.123.2 | S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_RES | X | 9 | 12265 | 155/155 |

Triage corrections: of the 11 unresolved ids, 7 are settled by code (11.39.16 PLAY_ENTRY_NOTICE,
11.60.16 PRT_READY_SET_RETURN_SESSION, 11.70.16 DECIDE_DELIVERY_ITEM_NOTICE, 11.83.16
SET_QUEST_UNRELEASED_AREA_NOTICE, 11.95.16 FORT_DEFENSE_NOTICE, 11.103.16 PLAY_STOP_TIMER_NOTICE,
11.117.16 REWARD_BOX_LIST_NUM_NOTICE), 11.7.16 is Season 3-exclusive (V; candidate
GET_CHARACTER_BINARY_STATUS_NTC rejected, C), 11.68.16 Season 3-exclusive (I), 11.88.16 and 11.118.16 stay
unresolved (no-op PC handlers). The 8 exclusive ids stay exclusive (V). The triage's 11.62.1 `pc_va` is
the `WritePacket` call (`0x838883`) in undefined code.

Capture-tested discrimination (PS4 body with PC framing): fails 1/1 (11.0.2), 58/179 (11.1.2), 23/44
(11.2.2), 66/146 (11.3.2), 3/20 (11.4.2), 3/3 (11.10.2), 2/2 (11.14.2), 1/1 (11.45.16), 48/48 (11.95.16),
1/1 (11.101.16). PS4 framing (u16 error first) on PC NTCs fails 5/5 (11.32.16), 20/20 (11.83.16), 11/11
(11.90.16), 1/1 (11.69.16): the PC NTCs carry no header. Code-only (empty lists or slack): every
11.5.2/11.9.2 element, the 11.117.16 u16 pair, the 11.7.16 element shape. No RES with Error != 0 captured.

Recompilation (`D:/ddon-data-s2/recompilation/.../UserSession/{C2S,S2C}.cpp`): only
`CPacket_S2C_QUEST_COMPLETE_NOTICE::ReadPacket` (S2C.cpp:9520) has a body; it agrees with PS4 (11.91.16).
T001's `recompiled_body yes` is a `DDON_STUB` for 11.0.2 (S2C.cpp:4908), 11.10.2 (4516), 11.14.2 (6000),
11.21.2 (9714), 11.90.16 (9743), 11.21.1 (C2S.cpp:247), 11.64.1 (177), 11.69.1 (82): overstated.
`PacketData/Quest.cpp` has no reader bodies (DTI stubs only).

## 44. Shared types for pattern authors

Reuse: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`), `Character.hexpat`
`CDataWalletPoint` (PC `0x77c5a0`), `Quest.hexpat` (`CDataRewardItem`, `CDataQuestEnemyInfo`,
`CDataQuestProgressWork`, `CDataQuestCommand(Check)`, `CDataQuestProcessState`, `CDataQuestAnnounce`,
`CDataQuestTalkInfo`, `CDataQuestLog`, `CDataQuestFlag`, `CDataQuestLayoutFlag`,
`CDataQuestOrderConditionParam`, `CDataQuestSetInfo`, `CDataQuestLayoutFlagSetInfo`, `CDataQuestExp`,
`CDataQuestDeliveryItem`, `CDataQuestOrderList` (11.122.2), `CDataQuestIdScheduleId`,
`CDataDeliveredItem(Record)`). Framing as T003 § 18 (inline RES header; NTCs without header).

Add to `Quest.hexpat` (V from the PC readers named; names PS4 DWARF unless marked I):

| Struct | PC reader | Wire |
| --- | --- | --- |
| `CDataQuestList` | `0x774530` | § 1.1 |
| `CDataQuestContents` | `0x773a20` | u8 Type, s32 Param01..04, u16 unk_u16_0, u16 unk_u16_1 (S3) |
| `CDataLightQuestDetail` | `0x76d1c0` | 7 x u32 (Arrowgene names, I) |
| `CDataLightQuestList` | `0x76d250` element | CDataQuestList Param, CDataLightQuestDetail Detail, CDataQuestContents Contents |
| `CDataSetQuestDetail` | `0x778040` | § 1.2 |
| `CDataSetQuestList` | `0x7783d0` element | CDataQuestList Param, CDataSetQuestDetail Detail |
| `CDataTutorialQuestList` / `CDataWorldManageQuestList` | `0x77b690` / `0x77cd60` | CDataQuestList Param, u8 EnableCancel / IsTutorialGuide |
| `CDataLotQuestList` | `0x76dae0` element | CDataQuestList Param, CDataQuestContents Contents |
| `CDataRewardItemDetail` | `0x7772a0` element | u32 ItemId, u16 Num, u8 Type |
| `CDataTimeGainQuestList` | `0x77b080` | § 10 (restriction members, I names) |
| `CDataSetQuestInfoList` | `0x778230` | § 11 |
| `CDataPriorityQuest` / `CDataPriorityQuestSetting` | `0x7735b0` / `0x773710` | § 1.2 / u32 CharacterId + list |
| `CDataQuestContentsSituationInfo` | `0x773ab0` element | u32 QuestScheduleId, u32 QuestId |
| `CDataQuestPartyBonusInfo` | `0x774de0` | § 1.2 |
| `CDataRewardBoxItem` / `CDataRewardBoxRecord` | `0x777000` / `0x777080` | § 26 |
| `CDataContentsPlayEnd` | `0x75ef90` | § 23 |
| `CDataContentsPlayStartData` | `0x75f030` | § 36 |
| `CDataCycleContentsNoticeData` / `CDataQuestContentsSituationInfoDetail` | `0x761970` / `0x773c60` | § 35 |
| Season 3-only: `CDataPackageQuestList`/`Detail`, `CDataLevelBonus`/`Element`, adventure-guide element | `0x7704d0`, `0x770e50`, `0x75a600`, `0x76d050`, `0x758bc0` | §§ 7, 40, 41 (names I) |

## 45. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`:

1. `PacketId.C2S_QUEST_11_60_16_NTC` is declared `PacketSource.Server` with the comment "clicking on quest
   glowing light"; the client sends it (capture source byte 0x00, PC writer `0x8395a0`) and it is the PRT
   return-session flag (§ 25).
2. `CDataContentsPlayEnd` writes `Gold, Exp, Rim, PlayTimeMillSec, Unk0, Unk1, Unk2`; the capture puts
   the play time in the 7th u32 (§ 23, I by timestamps). Widths agree.
3. `S2CQuestPlayEndNtc` leads with `WriteInt32 Unk0` — agrees with PC (s32 into the Error slot); not a
   misplacement, but its role (I) is the error slot.
4. Not misplacements (agree with PC 03040008): `CDataQuestList` (two `Int64` dates, `ContentsReleaseList`
   u32 list), `CDataSetQuestDetail` (wallet + exp lists), `CDataLightQuestList`, `CDataLightQuestDetail`
   (7 u32), `CDataQuestContents` (+`Unk0/Unk1` u16), `CDataTimeGainQuestList` (5 bools, `Restrictions`,
   `RequiredItemsList`), `CDataSetQuestInfoList` (two u64, trailing condition list),
   `CDataContentsPlayStartData` (3 bools, `Unk3List`), `S2CQuestBoardReloadNtc` (bool, bool, u32),
   `S2CQuestPlayEntryNtc` (u32), `S2CQuestGetLightQuestListRes`, `S2CQuestGetEndContentsGroupRes`, the
   Season 3-only `S2CQuestGetPackageQuestListRes`, `S2CQuestGetLevelBonusListRes`,
   `S2CQuestGetAdventureGuideQuestListRes` (`CDataQuestAdventureGuideList` with `CDataQuestOrderList`),
   `S2CQuestGetAdventureGuideQuestNtcRes`. Arrowgene has no structure for 11.7.16, 11.83.16, 11.95.16,
   11.117.16, 11.118.16 (ids only).

## 46. Open items and checks not run

- Names without code backing (I): the Season 3 members of § 1.1 (which u64 is new, the u32 list), the
  7th LightQuestDetail u32 position, the 5th TimeGain bool position and its two new members, the 11.14.2
  extra u64 and trailing condition list, the 11.45.16 middle u32s and lead s32, the 11.95.16 extra u64 and
  {u32,u32} list, the 11.101.16 bools and u8 list, the 11.117.16 u16 roles, every Season 3-only field.
- 11.68.16 exclusivity rests on absence of a matching PS4 reader/behaviour (I). 11.88.16 and 11.118.16
  identities: not settled (no-op PC handlers).
- Never non-empty in captures (code-only): 11.5.2 package list, 11.9.2 world-manage list.
- PC handler bodies for 11.0.2, 11.2.2, 11.4.2, 11.21.2, 11.31.2, 11.33.2, 11.34.2, 11.45.16 lie in
  undefined code; read by linear decoding only.
- ImHex not run (not on `PATH`); no pattern written (outside this package).
