# 006 T008: groups 14 WARP, 10 ITEM, 50 ITEM_SORT

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T008-warp-item.md`; the 37 rows of groups 14, 10 and 50 in
`research/T001-triage.tsv` (18 + 14 + 5 ids). Base `c3344053d7`. Marks: **V** verified in code (or by
capture for walk results), **I** inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t008/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t008/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays, `ida_ua.decode_insn`
  for linear decoding, `ida_typeinf` for DWARF structs, byte search for field offsets); nothing renamed,
  retyped, commented, patched or reanalysed.
- PC primitives as T003/T005/T007 § 0 (`nPacket::Read_u8 0x8bc410`, `Read_u16 0x8bc440`, `Read_s32
  0x8bc480`, `Read_u32 0x8bc4d0`, `Read_MtString 0x8bc5b0`, `Read_bool 0x8bc6e0`; `Write_u32 0x8bc920`,
  `Write_cstr 0x8bca30` (= big-endian u16 length + bytes, the MtString wire form, V); `WritePacket
  0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` -> group 10 `{0x212d0d8, 27}`, group 14 `{0x212fe38, 14}`,
  group 50 `{0x212d360, 3}`; stride 0x18, key `(sub<<16)|id` at +0x10. Entry +0 is filled by the
  initializer (`movq psub_X, xmm0` at e.g. `0x1a2e0dd`); IDA names each entry after its handler
  (`psub_7DE430`, group 50: `n8248192` = `0x7ddb80`, `n8247984` = `0x7ddab0`, `n8248368` = `0x7ddc30`).
  Every S2C `pc_va` of the triage equals its table handler (V, all 20).
- **Not functions in the PC database** (decoded linearly, no database change): handlers `0x7ddb80`
  (50.0.2) and `0x7ddab0` (50.0.16); reader `0x80ca00` (50.0.2); list reader `0x75e6e0` (CDataItemSort,
  starts 3 bytes after IDA's `0x75e6dd`); list reader `0x766af0` (14.4.2; Hex-Rays shows it as
  `loc_766AED + 3`); the 14.8.1 writer `0x83f910-0x83f9e4` (the triage `0x83f983` is its `WritePacket` call;
  IDA ends `sub_83F800` at `0x83f901`).
- PC writers (C2S): `WritePacket(p, group, id, sub, -1)` with group/id/sub read from the call (V each,
  17/17; 14.10.16 and 14.11.16 use sub `0x10`).
- PS4 match by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, behaviour, call site),
  never by PS4 id. Shape uniqueness was checked against an index of all 969 PS4 `OnPacket_S2C_*` /
  `CPacket_S2C_*::ReadPacket` read sequences.
- RES header (V, every PC RES reader here): `Read_s32` Error (+16); non-zero -> return; else `Read_s32`
  Result, body. PS4 reads `u16 m_usError, s32 m_nResult`. PC NTC readers read **no** header (V: 10.0.16
  `0x80cd10`, 10.10.16 `0x80c1a0`, 10.12.16 `0x80cb90`, 10.13.16 `0x80cb10`, 10.14.16 `0x80cca0`, 50.0.16
  inline in `0x7ddab0`); PS4 NTCs start with `Read_u16 m_usError`.
- **Walk**: `specs/006-packet-pattern-coverage/research/T008-walk.py` (stdlib; run from `D:/ddon-data` with
  `python -X utf8 -I specs/006-packet-pattern-coverage/research/T008-walk.py`; holds every PC layout below
  and the PS4 counter-test variants; `tally` prints field values for differences the fit window cannot
  see). Input `packets/decrypted_raw/*/`, every file whose suffix is `.<g>_<id>_<sub>` of the 37 ids
  (each suffix carries exactly one packet name: no collision). Header check: group, u16 id, sub, source
  (0x00 C2S, 0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no overrun (every file length
  is a multiple of 16). **Totals: 2,038 files, header 2,038/2,038, fit 2,038/2,038, no RES with
  Error != 0.** Samples: file number, size, sha256 first 16 hex digits, body end offset.

Field-name sources: PS4 DWARF member (`m_` prefix dropped) **V**; Season 3 names are Arrowgene leads, **I**.

**PS4 class sharing (asked by the brief).** Groups 10 and 50 share **no** PS4 class: group 10 uses
`CDataItemList`, `CDataItemUpdateResult`, `CDataUpdateWalletPoint`, `CDataSwitchStorage`,
`CDataMoveItemUIDFromTo`, `CDataCommonU8`, `CDataGameItemStorage`; group 50 uses `CDataItemSort` and
`CDataCommonU32`. Group 14 shares `CDataCommonU32` with group 50 (14.1.2 and 14.14.2 use the same PC list
reader `0x75e8e0` as `Packet.hexpat`'s CDataCommonU32 list). Within group 10, 10.3.2, 10.6.2 and 10.12.16
share the PC `CDataItemList` reader `0x76aca0` (list `0x76abe0`, V); 50.0.2 and 50.0.16 share the
`CDataItemSort` list reader `0x75e6e0` (V).

## 1. Shared Season 3 structures

### 1.1 CDataItemList (PC element `0x76aca0`, list `0x76abe0`; PS4 `Read_CDataItemList__0 0x19fe070`)

Users: 10.3.2, 10.6.2, 10.12.16 (inside CDataItemUpdateResult). PC wire order (V), PS4 DWARF:

| # | PC | PS4 02020005 (order) | Name for patterns |
| --- | --- | --- | --- |
| 1 | MtString | 1 u8 m_ucStorageType | `ItemUId` (PS4 `m_wstrUID` is item 3; V by type) |
| 2 | u32 | 2 u16 m_usSlotNo | `ItemId` (PS4 `m_unItemID`, I by position among u32) |
| 3 | u32 | 3 MtString m_wstrUID | `ItemNum` (PS4 `m_unItemNum`, I) |
| 4 | u8 | 4 u32 m_unItemID | `unk_u8` (S3; Arrowgene `SafetySetting`, I) |
| 5 | u8 | 5 u32 m_unItemNum | `StorageType` (I; capture values 1-6, 13, 14 match storage types) |
| 6 | u16 | 6 u32 m_unEquipCharacterID | `SlotNo` (I; only u16 member) |
| 7, 8 | u8, u8 | 7 u32 m_unEquipPawnID | `Color`, `PlusValue` (I) |
| 9 | bool | 8 u32 m_unEquipPoint | `Bind` (PS4 `b8 m_bBind`, I by type) |
| 10-12 | u32 x3 | 9 u8 m_ucColor | `EquipPoint`, `EquipCharacterID`, `EquipPawnID` (I; Arrowgene order) |
| 13 | list `0x765a90` {u8, u32, u16} | 10 list CDataEquipElementParam {u8, u32} | Context.hexpat `EquipElementParam` (S3 element +u16) |
| 14 | list `0x765ba0` {u8, u8, u16, u16} | 11 u8 m_ucPlusValue | Context.hexpat `AddStatusParam` (S3) |
| 15 | list `0x766210` {u8, u16} | 12 b8 m_bBind | Context.hexpat `EquipStatParam` shape (S3; reader of Login.hexpat's third list) |

Season 3 reorders the whole element and adds items 4, 14, 15 and the u16 of item 13 (V widths; names I
except where marked). Counter-test (PS4 element): fails **130/136** (10.3.2), **3/3** (10.6.2), **245/390**
(10.12.16); every PS4-fitting capture has an empty item list. Capture: up to 393 elements per list, up to
4 / 2 / 17 entries in lists 13 / 14 / 15.

### 1.2 Other readers

| Struct | PC | Wire | PS4 02020005 |
| --- | --- | --- | --- |
| CDataItemUpdateResult | list `0x76aec0` element | CDataItemList, s32 | `CItemList m_ItemInfo, s32 m_nUpdateItemNum` (V) |
| CDataUpdateWalletPoint | list `0x77c1c0` element | u8, u32, s32, u32 | `CWalletPoint m_PointParam {u8 m_ucType, u32 m_unValue}, s32 m_nAddPoint, u32 m_unExtraBonusPoint` (same, V) |
| CDataSwitchStorage | list `0x75c570` element | u8, **u16** | `u8 m_ucTargetStorageType, u8 m_ucChangeStorageType` (**S3 second field widened**, V width; name I) |
| CDataMoveItemUIDFromTo | writer `0x780090` element | MtString, u32, u8, u8, u16 | `m_wstrUID, u32 m_unNum, u8 m_ucSrcStorageType, u8 m_ucDstStorageType, u16 m_usSlotNo` (same, V) |
| CDataItemSort | list `0x75e6e0` (linear) element | u8, u8[0x400] (fixed) | `u8 m_ucStorageType, u8[1024] m_ucBin` (same, V; PS4 `Read_CDataItemSort_`) |
| CDataWarpPoint | list `0x77c870` element | u32, u32 | `u32 m_ulID, u32 m_ulRimPrice` (V) |
| CDataFavoriteWarpPoint | list `0x766af0` (linear) element | u32 x3 | `u32 m_ulSlotNo, m_ulWarpPointID, m_unPrice` (V) |
| CDataAreaWarpPoint | list `0x7595e0` element | u32 x3 | `u32 m_unAreaID, m_unWarpPointID, m_unPrice` (V) |
| CDataJumpLocation | `0x76c9e0` | u32, u32 | `CJumpLocation {u32 m_ulStageId, u32 m_unStartPos}` (V) |
| CDataCommonU32 list | `0x75e8e0` | list {u32} | `CDataCommonU32 {u32 m_unvalue}` (V) |

## 2. Group 14 WARP

### 2.1 14.1.1 GET_RELEASE_WARP_POINT_LIST_REQ / 14.1.2 …_RES

- PC writer `0x83fad0` (14,1,1): no body (V). PS4 `Send_C2S_GET_RELEASE_WARP_POINT_LIST_REQ 0x19bed00`: none (V).
- PC handler `0x7fec00`, reader `0x81d7e0`: RES header, list `0x75e8e0` CDataCommonU32 (V). PS4
  `OnPacket_S2C_GET_RELEASE_WARP_POINT_LIST_RES 0x2f6f40`: `m_WarpPointReleaseList` (V).
- Wire: REQ empty. RES `s32 Error; if (Error == 0) { s32 Result; MtTypedArray<CDataCommonU32> WarpPointReleaseList; }`.
- Walk REQ 41/41 slack 7 (`stream1-…-35/12055_…14_1_1`, 16 B, `cbcb5feac62134a1`, end 0x9). RES 41/41 slack
  11-15, up to 79 ids; `stream21-failedlogin-marked.pcapng_tcp-stream-48/12362_…14_1_2` (352 B,
  `00eb51217d2aafe8`), end 0x151: 79 ids 1, 2 … 99.

### 2.2 14.2.1 GET_WARP_POINT_LIST_REQ / 14.2.2 …_RES

- PC writer `0x83fd10` (14,2,1): u32 (V). PS4 `Send_C2S_GET_WARP_POINT_LIST_REQ 0x19bebc0`: `u32 in_CurrentPointID` (V).
- PC handler `0x7feef0`, reader `0x81d960`: RES header, list `0x77c870` CDataWarpPoint (V). PS4 `0x2f6dc0`:
  `m_WarpPointList` (V).
- Wire: REQ `u32 CurrentPointID`. RES header + `MtTypedArray<CDataWarpPoint> WarpPointList`.
- Walk REQ 178/178 slack 3 (`stream1-…-35/12190_…14_2_1`, 16 B, `d187348eb27741cf`, end 0xd: point 1).
  RES 178/178 slack 3-11; `stream21-…-48/13229_…14_2_2` (656 B, `f84259547b211ef8`), end 0x28d: 79 points
  {1, 0}, {2, 3000} … {99, 3000}.

### 2.3 14.3.1 WARP_REQ / 14.3.2 …_RES

- PC writer `0x840220` (14,3,1): u32 x3 (V). PS4 `CPacket_C2S_WARP_REQ::WritePacket 0x1a356e0`: `in_CurrentPointID,
  in_DestPointID, in_Price` (V).
- PC handler `0x7ff580`, reader `0x81dc00`: RES header, u32, u32 (V). PS4 `0x2f7190`: `u32 m_unWarpPointID, u32 m_unrim` (V).
- Walk REQ 44/44 slack 11 (`stream21-…-48/12916_…14_3_1`, 32 B, `de78048054ef8c93`, end 0x15: 1 -> 53, price 0).
  RES 44/44 slack 7 (`stream21-…-48/12919_…14_3_2`, 32 B, `c625bfd21803f797`, end 0x19: point 53, rim 2089227).

### 2.4 14.4.1 GET_FAVORITE_WARP_POINT_LIST_REQ / 14.4.2 …_RES

- PC writer `0x83f9f0` (14,4,1): u32 (V). PS4 `0x19bee30`: `u32 in_AreaID` (V).
- PC handler `0x7feb30`, reader `0x81d750`: RES header, list `0x766af0` (linear: three `Read_u32` per element,
  alloc 0x10) CDataFavoriteWarpPoint, u32 (V). PS4 `0x2f72d0`: `m_FavoriteWarpPointList, u32 m_unSlotIDMax` (V).
- Walk REQ 104/104 slack 3 (`stream1-…-35/11980_…14_4_1`, 16 B, `2b0835c338d35a2a`, end 0xd). RES 104/104 slack
  3-15; `stream51-marked.pcapng_tcp-stream-11/10189_…14_4_2` (976 B, `dafbf86b0cbf96ca`), end 0x3cd: 79
  entries {1, 1, 0} … {0, 99, 400}, SlotIDMax 10.

### 2.5 14.8.1 GET_AREA_WARP_POINT_LIST_REQ / 14.8.2 …_RES

- PC writer `0x83f910` (not a function; linear: `push -1; push 1; push 8; push 0xe; call WritePacket` at
  `0x83f983`, then `Write_u32`): u32 (V). PS4 `0x19bf200`: `u32 in_CurrentAreaID` (V).
- PC handler `0x7fea80`, reader `0x81d6d0`: RES header, list `0x7595e0` CDataAreaWarpPoint (V). PS4 `0x2f7c10`:
  `m_AreaWarpPointList` (V).
- Walk REQ 1/1 slack 3 (`stream76-marked.pcapng_tcp-stream-11/11552_…14_8_1`, 16 B, `c0b2ade3dd7f870d`, end 0xd:
  area 1). RES 1/1 slack 15 (`stream76-…-11/11554_…14_8_2`, 288 B, `c9ec27b7a87f38aa`, end 0x111: 21 entries
  {1, 2, 0} … {21, 96, 100}).

### 2.6 14.9.1 AREA_WARP_REQ / 14.9.2 …_RES

- PC writer `0x83f800` (14,9,1): u32 x3 (V). PS4 `CPacket_C2S_AREA_WARP_REQ::WritePacket 0x1a35640`:
  `in_CurrentAreaID, in_WarpPointID, in_Price` (V).
- PC handler `0x7fe940`, reader `0x81d5b0`: RES header, u32, u32 (V). PS4 `0x2f7d90`: `u32 m_unWarpPointID, u32 m_unRim` (V).
- Walk REQ 18/18 slack 11 (`stream21-…-48/13354_…14_9_1`, 32 B, `fe1663a9406e7ce8`, end 0x15: area 1, point 66,
  price 0). RES 18/18 slack 7 (`stream21-…-48/13356_…14_9_2`, 32 B, `4f4bb3273482f819`, end 0x19: 66, 2089227).

### 2.7 14.10.16 C2S_WARP_WARP_START_NTC (unresolved -> matched PS4 `C2S_WARP_END_NTC`, V by call site)

- PC writer `0x840160` (14,10,0x10): **no body** (V). Its only caller chain: `0x8865f0` (login guard) <-
  `0x415470` at `0x4155ff`. `0x415470` is the PC `aStage::move_menu_warp` (state 100, chat message
  `0x70` with `"%s %s"` of the player name, `aStage::GuardData::setJmpStatus(0)`), and the call sits after
  `mov [manager+0x9df0], 1` and before `mov [edi+4], 1`.
- PS4: `cNetGameServer::warpEndNotice` -> `Send_C2S_WARP_END_NTC 0x19bf340` (no body), called once, from
  `aStage::move_menu_warp 0x107bd`: `v13->mReqAreaChangeJumpType = 1; cNetGameServer::warpEndNotice(v13);
  this->mRno = 1;` (same message `0x70`, same state 100). Same place, same preceding store, same empty
  body: **PS4 C2S_WARP_END_NTC = PC 14.10.16** (V). PS4 has no `WARP_START` symbol or type.
- So the triage/Arrowgene name `WARP_START_NTC` is **contradicted** (C) by the PS4 name of the same call;
  the 14.11.16 candidate `Send_C2S_WARP_END_NTC` belongs here, not to 14.11.16.
- Wire: empty body. Walk 62/62 slack 7 (`stream21-…-48/12942_…14_10_16`, 16 B, `aa4b0984e5574948`, end 0x9).

### 2.8 14.11.16 C2S_WARP_WARP_END_NTC (unresolved -> Season 3, no PS4 counterpart)

- PC writer `0x840080` (14,11,0x10): **u32** (V). Caller `0x885a90` (login guard) <- `0xb61ab0`, an sGame setter:
  `if (a2 != sGame[0x3994]) { send(a2); sGame[0x3994] = a2; }` (V). Callers of the setter: `0x407060`
  (passes 1) and `0x412910` (passes `[edi+0x30]`).
- PS4: the only warp C2S notice is `WARP_END_NTC` (empty, § 2.7); no PS4 C2S packet type carries a lone u32
  sent from an sGame change-detect setter. Rejected: `Send_C2S_WARP_END_NTC` (empty body, and its call site
  is 14.10.16's). **Season 3 addition (I by absence).** Name `WARP_END_NTC` is a community lead only (I).
- Wire: `u32 unk_u32` (I; captured values 1 x48, 20 x3, 87 x3, 97, 21, 72; 1 and 87 also appear as 14.14.2
  start-point ids, so a point id is plausible, I).
- Walk 57/57 slack 3 (`stream1-…-35/12145_…14_11_16`, 16 B, `76588d201b7dcd76`, end 0xd: 1). Counter-test
  "empty body" fits 57/57 (4 bytes inside the window): the u32 is code-only.

### 2.9 14.12.1 GET_RETURN_LOCATION_REQ / 14.12.2 …_RES

- PC writer `0x83fb90` (14,12,1): no body (V). PS4 `0x19cafc0`: none (V).
- PC handler `0x7fecf0`, reader `0x81d860`: RES header, `0x76c9e0` CDataJumpLocation {u32, u32} (V). PS4
  `0x308e50`: `CJumpLocation m_jumpLocation {m_ulStageId, m_unStartPos}` (V).
- Walk REQ 9/9 slack 7 (`stream85-marked.pcapng_tcp-stream-11/102852_…14_12_1`, 16 B, `d7c9652c926f226d`, end 0x9).
  RES 9/9 slack 7 (`stream85-…-11/102856_…14_12_2`, 32 B, `f6eed32271703b97`, end 0x19: stage 595, pos 7).

### 2.10 14.14.1 GET_START_POINT_LIST_REQ / 14.14.2 …_RES (exclusive, confirmed)

- PC writer `0x83fc50` (14,14,1): no body (V); caller `0x871c60`. PC handler `0x7fede0`, reader `0x81d8e0`:
  RES header, list `0x75e8e0` CDataCommonU32 (V); handler string
  `"cSeedGameSvConnection::OnPacket_WARP_GET_START_POINT_LIST_RES"`, network status slot **710**; the list is
  copied into a GUI object (`n3_0 + 5294`).
- PS4: no symbol and no DWARF `CPacket_*` type containing `START_POINT`; the PS4 `cNetGameServer::mStatus`
  array has **563** slots, below the PC slot 710 (V). **Season 3-exclusive confirmed** (V by absence of
  symbol/type; slot range supporting).
- Wire: REQ empty. RES header + `MtTypedArray<CDataCommonU32> StartPointIdList` (name I; Arrowgene `WarpPointIdList`).
- Walk REQ 42/42 slack 7 (`stream1-marked.pcapng_tcp-stream-34/11938_…14_14_1`, 16 B, `6a780460c1b28ebc`, end 0x9).
  RES 42/42 slack 3-7, up to 2 ids (`stream21-…-47/12203_…14_14_2`, 32 B, `6f66768bdf6a3583`, end 0x1d: 1, 87).

## 3. Group 10 ITEM

### 3.1 10.0.1 USE_BAG_ITEM_REQ / 10.0.2 …_RES

- PC writer `0x82d700` (10,0,1): `Write_cstr` (MtString), u32 (V). PS4 `Send_C2S_USE_BAG_ITEM_REQ 0x19b6310`:
  `Write_MT_CSTR in_strUID, u32 in_Num` (V).
- PC handler `0x7de430`, reader `0x80cd90`: RES header only (V). PS4 `0x2e9170`: u16, s32 (V).
- Walk REQ 18/18 slack 9 (`stream6-annilot-hobo-marked.pcapng_tcp-stream-2/30499_…10_0_1`, 32 B,
  `29fad77c1a518baa`, end 0x17: "CF1045C8", 1). RES 21/21 slack 15 (`stream6-…-2/30504_…10_0_2`, 32 B,
  `84fd08c070f473ea`, end 0x11).

### 3.2 10.0.16 S2C_ITEM_USE_BAG_ITEM_NTC (unresolved -> matched `USE_BAG_ITEM_NOTICE`, V by behaviour)

- PC handler `0x7de3b0`, reader `0x80cd10`: u32 x3, no header (V). The handler only stores the three values into
  the network manager (`this+79`) at +0x8dd4/+0x8dd8/+0x8ddc; the only other code touching +0x8dd4 is a reset
  in `0x8469f0` (V, byte search).
- PS4: six notices read u16 + u32 x3 (`PARTY_INVITE_ENTRY_NTC`, `USE_BAG_ITEM_NOTICE`, `ENEMY_KILL_RES`,
  `SET_OM_INSTANT_KEY_VALUE_NOTICE`, `LEADER_WARP_NTC`, `CLAN_POINT_ADD_NTC`); only
  `OnPacket_S2C_USE_BAG_ITEM_NOTICE 0x2e9280` just stores them into the manager
  (`mUsedItemCharacterId`, `mUsedItemId`, `mUsedItemNum`, consecutive u32 at cNetGameServer +29456), the
  same three-consecutive-field store as PC (V by behaviour). Members `u32 m_unCharacterID, m_unItemID, m_unItemNum`.
- Wire: `u32 CharacterID; u32 ItemID; u32 ItemNum`. Walk 18/18 slack 11 (`stream6-…-2/30501_…10_0_16`, 32 B,
  `d8142fa73e09e3a8`, end 0x15: 2144504, 55, 1). PS4 framing fits 18/18 (2 bytes inside the window, not
  discriminating; the code reads no u16).

### 3.3 10.3.1 GET_STORAGE_ITEM_LIST_REQ / 10.3.2 …_RES

- PC writer `0x82d0d0` (10,3,1): list `0x77e050` {u8} (V). PS4 `CPacket_C2S_GET_STORAGE_ITEM_LIST_REQ::WritePacket
  0x1a37da0`: `MtTypedArray<CDataCommonU8> m_StorageList` (V).
- PC handler `0x7dd540`, reader `0x80c6b0`: RES header, list `0x76abe0` CDataItemList (§ 1.1, V). PS4 `0x2e95a0`:
  `MtTypedArray<CDataItemList> m_ItemList` (V; element differs).
- Walk REQ 136/136 slack 2-10, up to 9 types (`stream1-…-35/12033_…10_3_1`, 32 B, `16081a07621451b3`, end 0x16:
  1, 2, 3, 4, 5, 14, 16, 15, 17). RES 136/136 slack 0-15, PS4 element fails 130/136;
  `stream51-…-11/10232_…10_3_2` (19584 B, `eb22d630fdbc9af9`), end 0x4c72: 393 items, first
  {"0A56A6C2", 41, 19, 0, 6, 71, 0, 0, false, 0, 0, 0, [], [], []}; element lists seen non-empty
  (e.g. {"ECEBB9A7", 21651, 1, 0, 6, 64, …, EquipElementParam [{1, 23033, 0}]}).

### 3.4 10.6.1 GET_POST_ITEM_LIST_REQ / 10.6.2 …_RES

- PC writer `0x82cf20` (10,6,1): no body (V). PS4 `0x19cc8d0`: none (V).
- PC handler `0x7dd270`, reader `0x80c5b0`: identical to 10.3.2's (RES header + list `0x76abe0`, V). PS4 `0x2e9850`:
  `m_ItemList` (V).
- Walk REQ 3/3 slack 7 (`stream6-…-2/23356_…10_6_1`, 16 B, `9dc896baffb1c45b`, end 0x9). RES 3/3 slack 11-14, PS4
  element fails 3/3; `stream6-…-2/29661_…10_6_2` (9344 B, `3cf5e98df4a7d18e`), end 0x2473: 190 items.

### 3.5 10.7.1 MOVE_ITEM_REQ / 10.7.2 …_RES

- PC writer `0x82d270` (10,7,1): u8, list `0x780090` CDataMoveItemUIDFromTo (§ 1.2, V). PS4
  `CPacket_C2S_MOVE_ITEM_REQ::WritePacket 0x1a37b30`: `u8 in_SourceGameStorageType, m_ItemUIDList` (same, V).
- PC handler `0x7dd780`, reader `0x80c850`: RES header only (V). PS4 `0x2e9b40` (V).
- Walk REQ 6/6 slack 0 (`stream6-…-2/23531_…10_7_1`, 32 B, `33534aacc7c522c9`, end 0x20: source 13,
  {"35B3BA2E", 1, 13, 3, 0}). RES 6/6 slack 15 (`stream6-…-2/23538_…10_7_2`, 32 B, `d8c87d738cb86716`, end 0x11).

### 3.6 10.9.1 GET_ITEM_STORAGE_INFO_REQ (10.9.2 already covered)

- PC writer `0x82ce40` (10,9,1): list `0x77f970` {u8} (V). PS4 `CPacket_C2S_GET_ITEM_STORAGE_INFO_REQ::WritePacket
  0x1a324e0`: `MtTypedArray<CDataGameItemStorage>` (Item.hexpat `CDataGameItemStorage`, V).
- Walk 4/4 slack 2 (`stream6-…-2/27175_…10_9_1`, 16 B, `c9d4057723a20039`, end 0xe: [13]).

### 3.7 10.10.16 S2C_ITEM_EXTEND_ITEM_SLOT_NTC (unresolved -> matched `EXTEND_ITEM_SLOT_NTC`, V)

- PC handler `0x7dcad0`, reader `0x80c1a0`: u8, u16, u16, no header (V). PS4 `OnPacket_S2C_EXTEND_ITEM_SLOT_NTC
  0x305830` is the **only** PS4 notice reading u16 + u8, u16, u16 (V), and both handlers do the same: look up
  the storage by the u8 (`sItemManager::setLinkItem` / PC `0xb9f390`), store the second u16 into the
  per-category slot array of sGame, announce a GUI message (PS4 `0x1BC`, PC `0x1BA`) when the total changes,
  then switch on the category (V by behaviour). Members `u8 m_ucCategory, u16 m_usAddNum, u16 m_usTotalNum`.
- Walk 43/43 slack 2 (`stream21-…-47/12131_…10_10_16`, 16 B, `b41ece27548f82e1`, end 0xe: category 6, add 40,
  total 400). PS4 framing fits 43/43 (not discriminating; code reads no u16).

### 3.8 10.12.16 S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC

- PC handler `0x7ddd80`, reader `0x80cb90`: u16, list `0x76aec0` CDataItemUpdateResult, list `0x77c1c0`
  CDataUpdateWalletPoint, no header (V). PS4 `OnPacket_S2C_UPDATE_CHARACTER_ITEM_NOTICE 0x315b80` (unique
  shape): `u16 m_usUpdateType, m_UpdateItemList, CWallet m_UpdateWallet` (V; element CDataItemList differs, § 1.1).
- Walk 390/390 slack 0-14, up to 16 items and 2 wallet entries (wallet non-empty in 207); PS4 element fails
  245/390 (every fit has an empty item list), PS4 framing fails 388/390;
  `stream85-…-11/139321_…10_12_16` (880 B, `980e541ac0fbd14e`), end 0x363: type 44, 16 items
  ({"B507A7DF", 9363, 0, 0, 1, 2, …}, -10) …, wallets [].

### 3.9 10.13.16 S2C_SWITCH_STORAGE_NTC

- PC handler `0x7ddcc0`, reader `0x80cb10`: s32, bool, list `0x75c570` {u8, **u16**}, no header (V); on s32 == 0 it
  passes bool and list to `0xb9f560` (sItemManager). PS4 `OnPacket_S2C_SWITCH_STORAGE_NTC 0x3374a0` (unique
  shape u16, s32, bool, list): `s32 m_nResult, b8 m_bIsStart, m_ChangeList {u8, u8}`, and on result 0 calls
  `sItemManager::setSwitchStorage(IsStart, …)` (V by behaviour). Season 3 widens the element's second field
  to u16 (V width).
- Walk 2/2 slack 11 (`stream85-…-11/139320_…10_13_16`, 32 B, `8f0ffdca18c29fb8`, end 0x15: 0, true, [{1, 10}]).
  PS4 element fits 2/2 (1 byte inside the window: **code-only**); PS4 framing fails 2/2.

### 3.10 10.14.16 S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC (unresolved -> Season 3, no PS4 counterpart)

- PC handler `0x7de260`, reader `0x80cca0`: u16, list `0x76cc70` {u8, u32}, no header (V). For each element the
  handler looks the u32 up in the item manager (`0xb98c80`, i.e. an item id) and posts chat message `0x85`
  with the item name (V).
- PS4: no notice reads u16 + u16 + list (index: only `UPDATE_CHARACTER_ITEM_NOTICE` and
  `ENTRY_BOARD_ITEM_TIMEOUT_TIMER_NOTICE` start u16, u16; neither has a {u8, u32} list). Rejected:
  `ACHIEVEMENT_RECEIVABLE_REWARD_NTC 0x309a10` (list only, CDataAchieveRewardCommon), `ACHIEVEMENT_REWARD_RECEIVE_RES
  0x309b80` (RES, two lists). **Season 3 addition (I by absence)**; name community lead (I). The PC has
  `"cSeedGameSvConnection::OnPacket_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_RES"` (another group).
- Wire: `u16 unk_u16; MtTypedArray<{u8 unk_u8; u32 ItemId}> unk_ItemList` (ItemId I by use).
- Walk 1/1 slack 12 (`stream65-epi1-4-marked.pcapng_tcp-stream-9/1957_…10_14_16`, 32 B, `e53f14a5d0e8a8f6`, end 0x14:
  2, [{7, 16227}]).

## 4. Group 50 ITEM_SORT

### 4.1 50.0.1 GET_ITEM_SORTDATA_BIN_REQ / 50.0.2 …_RES

- PC writer `0x82d550` (50,0,1): list `0x77df90` {u32} (V). PS4 `CPacket_C2S_GET_ITEM_SORTDATA_BIN_REQ::WritePacket
  0x1a32690`: `MtTypedArray<CDataCommonU32> m_SortList` (V).
- PC handler `0x7ddb80` (linear), reader `0x80ca00` (linear): RES header, list `0x75e6e0` CDataItemSort (V). PS4
  `OnPacket_S2C_GET_ITEM_SORTDATA_BIN_RES 0x333210`: `MtTypedArray<CDataItemSort> m_SortData` (V).
- Walk REQ 46/46 slack 7-15, up to 7 (`stream1-…-35/12020_…50_0_1`, 48 B, `9997680b64dc4729`, end 0x29: 1, 2, 3, 5,
  4, 6, 7). RES 46/46 slack 11, **list always empty** (`stream1-…-35/12027_…50_0_2`, 32 B, `c6f4a5c467b2e383`,
  end 0x15); the data arrives in 50.0.16 just before it (same element reader).

### 4.2 50.0.16 S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC (unresolved -> Season 3, no PS4 counterpart)

- PC handler `0x7ddab0` (linear): reads list `0x75e6e0` CDataItemSort directly (no header), then `0x7dd960`, which
  for each element maps the storage type, loads the 1024-byte bin through an `MtMemoryStream` into the item
  manager's sort table and re-sorts (V).
- PS4: `nPacket::Read_CDataItemSort_` has exactly one caller, `OnPacket_S2C_GET_ITEM_SORTDATA_BIN_RES` (V); no PS4
  notice carries CDataItemSort. **Season 3 addition** (V by absence of any other reader caller); name I.
- Wire: `MtTypedArray<CDataItemSort> SortData`. Walk 48/48 slack 2-14, up to 5 elements; PS4 framing fails 47/48;
  `stream1-…-35/12025_…50_0_16` (5152 B, `a228539d39cabbc4`), end 0x1412: storage types 1, 2 … 7, 1024 bytes each.

### 4.3 50.1.1 SET_ITEM_SORTDATA_BIN_REQ / 50.1.2 …_RES

- PC writer `0x841860` (50,1,1): u8, `0x780fe0` (1024 x `Write_u8`), **bool** (V). PS4
  `CPacket_C2S_SET_ITEM_SORTDATA_BIN_REQ::WritePacket 0x1a325f0`: `CDataItemSort m_SortData` only. **Season 3 adds
  the trailing bool** (V code; name I).
- PC handler `0x7ddc30`, reader `0x80ca80`: RES header only (V). PS4 `0x333410` (V).
- Walk REQ 59/59 slack 5; PS4 body fits 59/59 (1 byte inside the window: code-only), the bool reads 1 in 59/59
  (`stream1-…-35/25926_…50_1_1`, 1040 B, `6cca7eeece042f6c`, end 0x40b: type 6, bin, true). RES 59/59 slack 15
  (`stream1-…-35/25929_…50_1_2`, 32 B, `5c2db694d05a017a`, end 0x11).

## 5. Summary

PS4 mark: V = confirmed by code (symbol + body, behaviour, or call site); "none" = no PS4 counterpart.
Body bytes for Error == 0 (lists `+kn`; var = strings or nested lists).

| id | name (file) | PS4 | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 14.1.1 | C2S_WARP_GET_RELEASE_WARP_POINT_LIST_REQ | V | 0 | 12055 | 41/41 |
| 14.1.2 | S2C_WARP_GET_RELEASE_WARP_POINT_LIST_RES | V | 12+4n | 12362 | 41/41 |
| 14.2.1 | C2S_WARP_GET_WARP_POINT_LIST_REQ | V | 4 | 12190 | 178/178 |
| 14.2.2 | S2C_WARP_GET_WARP_POINT_LIST_RES | V | 12+8n | 13229 | 178/178 |
| 14.3.1 | C2S_WARP_WARP_REQ | V | 12 | 12916 | 44/44 |
| 14.3.2 | S2C_WARP_WARP_RES | V | 16 | 12919 | 44/44 |
| 14.4.1 | C2S_WARP_GET_FAVORITE_WARP_POINT_LIST_REQ | V | 4 | 11980 | 104/104 |
| 14.4.2 | S2C_WARP_GET_FAVORITE_WARP_POINT_LIST_RES | V | 16+12n | 10189 | 104/104 |
| 14.8.1 | C2S_WARP_GET_AREA_WARP_POINT_LIST_REQ | V | 4 | 11552 | 1/1 |
| 14.8.2 | S2C_WARP_GET_AREA_WARP_POINT_LIST_RES | V | 12+12n | 11554 | 1/1 |
| 14.9.1 | C2S_WARP_AREA_WARP_REQ | V | 12 | 13354 | 18/18 |
| 14.9.2 | S2C_WARP_AREA_WARP_RES | V | 16 | 13356 | 18/18 |
| 14.10.16 | C2S_WARP_WARP_START_NTC | V = PS4 `C2S_WARP_END_NTC` (call site; name C) | 0 | 12942 | 62/62 |
| 14.11.16 | C2S_WARP_WARP_END_NTC | none (S3, I) | 4 | 12145 | 57/57 |
| 14.12.1 | C2S_WARP_GET_RETURN_LOCATION_REQ | V | 0 | 102852 | 9/9 |
| 14.12.2 | S2C_WARP_GET_RETURN_LOCATION_RES | V | 16 | 102856 | 9/9 |
| 14.14.1 | C2S_WARP_GET_START_POINT_LIST_REQ | none (exclusive, V) | 0 | 11938 | 42/42 |
| 14.14.2 | S2C_WARP_GET_START_POINT_LIST_RES | none (exclusive, V) | 12+4n | 12203 | 42/42 |
| 10.0.1 | C2S_ITEM_USE_BAG_ITEM_REQ | V | var (6+s) | 30499 | 18/18 |
| 10.0.2 | S2C_ITEM_USE_BAG_ITEM_RES | V | 8 | 30504 | 21/21 |
| 10.0.16 | S2C_ITEM_USE_BAG_ITEM_NTC | V behaviour `USE_BAG_ITEM_NOTICE` | 12 | 30501 | 18/18 |
| 10.3.1 | C2S_ITEM_GET_STORAGE_ITEM_LIST_REQ | V | 4+n | 12033 | 136/136 |
| 10.3.2 | S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | V (S3 CDataItemList) | var | 10232 | 136/136 |
| 10.6.1 | C2S_ITEM_GET_POST_ITEM_LIST_REQ | V | 0 | 23356 | 3/3 |
| 10.6.2 | S2C_ITEM_GET_POST_ITEM_LIST_RES | V (S3 CDataItemList) | var | 29661 | 3/3 |
| 10.7.1 | C2S_ITEM_MOVE_ITEM_REQ | V | var | 23531 | 6/6 |
| 10.7.2 | S2C_ITEM_MOVE_ITEM_RES | V | 8 | 23538 | 6/6 |
| 10.9.1 | C2S_ITEM_GET_ITEM_STORAGE_INFO_REQ | V | 4+n | 27175 | 4/4 |
| 10.10.16 | S2C_ITEM_EXTEND_ITEM_SLOT_NTC | V behaviour + unique shape | 5 | 12131 | 43/43 |
| 10.12.16 | S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | V (S3 CDataItemList) | var | 139321 | 390/390 |
| 10.13.16 | S2C_SWITCH_STORAGE_NTC | V (S3 element u16) | 9+3n | 139320 | 2/2 |
| 10.14.16 | S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC | none (S3, I) | 6+5n | 1957 | 1/1 |
| 50.0.1 | C2S_ITEM_SORT_GET_ITEM_SORTDATA_BIN_REQ | V | 4+4n | 12020 | 46/46 |
| 50.0.2 | S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_RES | V | 12+1025n | 12027 | 46/46 |
| 50.0.16 | S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC | none (S3, V by reader callers) | 4+1025n | 12025 | 48/48 |
| 50.1.1 | C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ | V (S3 trailing bool) | 1026 | 25926 | 59/59 |
| 50.1.2 | S2C_ITEM_SORT_SET_ITEM_SORTDATA_BIN_RES | V | 8 | 25929 | 59/59 |

Triage corrections: 10.0.16 unresolved -> `USE_BAG_ITEM_NOTICE` (V behaviour); 10.10.16 unresolved ->
`EXTEND_ITEM_SLOT_NTC` (V behaviour + unique shape); 14.10.16 unresolved -> PS4 `C2S_WARP_END_NTC` (V call
site; the 14.11.16 candidate moves here); 14.11.16, 10.14.16, 50.0.16 unresolved -> no PS4 counterpart
(Season 3); 14.14.1/2 exclusive confirmed. The 14.8.1 `pc_va` `0x83f983` is the `WritePacket` call inside the
writer at `0x83f910`.

Capture-tested discrimination (PS4 body, PC framing): CDataItemList fails 130/136 (10.3.2), 3/3 (10.6.2),
245/390 (10.12.16); PS4 framing fails 388/390 (10.12.16), 2/2 (10.13.16), 47/48 (50.0.16); it fits 18/18
(10.0.16) and 43/43 (10.10.16) (2 bytes inside the window, not discriminating). Code-only: 10.13.16 element u16
(PS4 fits 2/2), 50.1.1 trailing bool (PS4 fits 59/59; value 1 in all), 14.11.16 u32 (empty body fits 57/57).
No RES with Error != 0 captured.

Recompilation (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp`): no body
for any of the 37 ids. T001's `recompiled_body yes` is a `DDON_STUB` for 10.9.1 (C2S.cpp:162), 14.3.1
(C2S.cpp:387), 14.9.1 (C2S.cpp:27), 50.0.1 (C2S.cpp:157): overstated. `PacketData/{Item,Warp}.cpp` hold DTI
boilerplate and stubs only.

## 6. Shared types for pattern authors

Reuse: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32` = PC `0x75e8e0`/`0x77df90`,
`CDataCommonU8` = `0x77e050`); `Item.hexpat` (`CDataGameItemStorage`, 10.9.1 via `0x77f970`); `Context.hexpat`
(`EquipElementParam` `0x765a90`, `AddStatusParam` `0x765ba0`, `EquipStatParam` shape {u8, u16} for the
`0x766210` list as `Login.hexpat` does); `Character.hexpat` `CDataWalletPoint` shape (but see below). Framing
as T003 § 18 (inline RES header; NTCs without header). Not needed here: the 17-byte
`CDataGatheringItemElement` (`Instance.hexpat`) appears in none of these 37 ids (10.2.2's reader `0x80c7c0`
reads the RES header only; 10.2.1 has no capture and no triage row).

Add (V from the PC readers named; names PS4 DWARF unless marked I):

| Include | Struct | PC reader | Wire |
| --- | --- | --- | --- |
| `Item.hexpat` (include Context) | `CDataItemList` | `0x76aca0` | § 1.1: MtString ItemUId, u32 ItemId, u32 ItemNum, u8 unk (I), u8 StorageType, u16 SlotNo, u8 Color, u8 PlusValue, bool Bind, u32 EquipPoint, u32 EquipCharacterID, u32 EquipPawnID, MtTypedArray<EquipElementParam>, MtTypedArray<AddStatusParam>, MtTypedArray<EquipStatParam> (names after item 3 I) |
| `Item.hexpat` | `CDataItemUpdateResult` | `0x76aec0` element | CDataItemList ItemInfo, s32 UpdateItemNum |
| `Item.hexpat` | `CDataUpdateWalletPoint` | `0x77c1c0` element | u8 Type, u32 Value, s32 AddPoint, u32 ExtraBonusPoint (first two = Character.hexpat `CDataWalletPoint`, read inline) |
| `Item.hexpat` | `CDataSwitchStorage` | `0x75c570` element | u8 TargetStorageType, u16 ChangeStorageType (S3 width; second name I) |
| `Item.hexpat` | `CDataMoveItemUIDFromTo` | writer `0x780090` element | MtString UID, u32 Num, u8 SrcStorageType, u8 DstStorageType, u16 SlotNo |
| `Item.hexpat` | `CDataItemSort` | `0x75e6e0` element | u8 StorageType, u8 Bin[1024] |
| `Item.hexpat` | `CDataItemRewardEntry` (name I) | `0x76cc70` element | u8 unk_u8, u32 ItemId (I) |
| new `Warp.hexpat` | `CDataWarpPoint` | `0x77c870` element | u32 ID, u32 RimPrice |
| `Warp.hexpat` | `CDataFavoriteWarpPoint` | `0x766af0` element | u32 SlotNo, u32 WarpPointID, u32 Price |
| `Warp.hexpat` | `CDataAreaWarpPoint` | `0x7595e0` element | u32 AreaID, u32 WarpPointID, u32 Price |
| `Warp.hexpat` | `CDataJumpLocation` | `0x76c9e0` | u32 StageId, u32 StartPos |

## 7. Arrowgene leads

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`.
Agree with PC 03040008 in order and width: `CDataItemList` (SafetySetting, StorageType, SlotNo … at the PC
positions), `CDataEquipElementParam` {u8, u32, u16}, `CDataUpdateWalletPoint`, `CDataItemSort`, `CDataWarpPoint`,
`CDataFavoriteWarpPoint`, `CDataJumpLocation`, `S2CItemUpdateCharacterItemNtc`, `S2CItemExtendItemSlotNtc`,
`S2CItemSwitchStorageNtc` (s32 `Unk0` = PS4 `m_nResult`, bool, list), `C2SItemMoveItemReq`, `C2SItemUseBagItemReq`,
the warp REQ/RES bodies, `S2CWarpGetStartPointListRes`, `S2CItemSortGetItemSortdataBinNtc`/`Res`, the C2S storage
and sort lists, `C2SWarpWarpStartNtc` (empty).

Misplacements:

- `S2CItemAchievementRewardReceiveNtc` (10.14.16) writes `u16 Unk0, u32 Unk1, u8 Unk2, u32 ItemId`: the PC
  reads `u16, MtTypedArray<{u8, u32}>`, so `Unk1` is the **list count** (its "0-3, else disconnect" comment fits
  a count) and the packet can carry only one element. Same bytes when Unk1 = 1.
- `C2SWarpWarpEndNtc` (14.11.16) reads nothing: the PC writes a **u32** (`0x840080`).
- `C2SItemSortSetItemSortDataBinReq` (50.1.1) reads only `CDataItemSort`: the PC writes a **trailing bool**.
- `CDataSwitchStorage` names the u16 `Num`; PS4 calls the pair Target/ChangeStorageType (the width is S3; name
  lead only).
- Names: Arrowgene `WARP_START_NTC` / `WARP_END_NTC` for 14.10.16 / 14.11.16 conflict with PS4, whose
  `WARP_END_NTC` is the 14.10.16 call site (§ 2.7).
- No structure in Arrowgene for 10.0.16 (`S2C_ITEM_USE_BAG_ITEM_NTC` is only a PacketId).

## 8. Open items and checks not run

- Names without code backing (I): CDataItemList items after 3 (the PS4 order does not carry over), the 14.11.16
  u32, the 10.14.16 u16 and element u8, the 50.1.1 bool, the 10.13.16 second field.
- 14.11.16 and 10.14.16 Season 3 status rests on the absence of a PS4 counterpart (no shape match, no symbol);
  50.0.16 and 14.14 rest on a complete reader/type search (V).
- Never non-empty in captures (code-only): 50.0.2 list (element exercised by 50.0.16), CDataItemList's
  AddStatusParam list was seen (max 2) but 10.6.2's three element lists were always empty.
- PC code read linearly only: `0x7ddb80`, `0x7ddab0`, `0x80ca00`, `0x75e6e0`, `0x766af0`, `0x83f910`.
- GUI message indices (10.10.16 PC `0x1BA` vs PS4 `0x1BC`): message tables not compared.
- ImHex not run (not on `PATH`); no pattern written (outside this package).
