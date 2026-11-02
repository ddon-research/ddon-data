# 006 T009: groups 37 MAIL, 45 STAMP, 2 CHARACTER

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T009-mail-stamp-character.md`; the 48 rows of groups 37, 45
and 2 in `research/T001-triage.tsv` (17 + 8 + 23 ids, 1,342 captures). Base `a9227d8d48` (HEAD was
`d07e7552f8` when the report was written; no input of this report changed in between). Marks: **V**
verified in code (or by capture for walk results), **I** inferred, **C** contradicted. All addresses
are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t009/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t009/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays, `ida_ua.decode_insn`
  for linear decoding, `ida_typeinf` for DWARF structs); nothing renamed, retyped, commented, patched or
  reanalysed.
- PC primitives as T003/T005/T008 § 0 (`nPacket::Read_u8 0x8bc410`, `Read_u16 0x8bc440`, `Read_s32
  0x8bc480`, `Read_u32 0x8bc4d0`, `Read_MtString 0x8bc5b0`, `Read_s64 0x8bc660`, `Read_u64 0x8bc6a0`,
  `Read_bool 0x8bc6e0`; `Write_u8 0x8bc860`, `Write_u32 0x8bc920`, `Write_u64 0x8bcb40`, `Write_bool
  0x8bcb80`; `WritePacket 0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` -> group 2 `{0x212b0f8, 36}`, group 37 `{0x212d798, 15}`,
  group 45 `{0x212fd30, 5}`; stride 0x18, key `(sub<<16)|id` at +0x10; entry +0 filled by the initializer
  (`movq` stores, e.g. `0x1a2f511` for 37.9.2 = `loc_7E404F+1` = `0x7e4050`; group 45 entries named
  `n8380736` = `0x7fe140` etc.). Every S2C `pc_va` of the triage equals its table handler (V, 24/24).
- **Not functions in the PC database** (decoded linearly, no database change): handlers `0x7e4050`
  (37.9.2; IDA's item starts at `0x7e404f`, the real entry `push esi` is at `0x7e4050`), `0x7fe140`
  (45.0.2), `0x7fe070` (45.1.2), `0x7fe1f0` (45.3.2); the 45.4.1 writer `0x83f5a0-0x83f659` (the triage
  `0x83f613` is its `WritePacket` call; bytes at `0x83f5a0` start `83 ec 1c 56`, `sub_83F4B0` ends at
  `0x83f59c`). The readers these handlers call (`0x81d170`, `0x81d0d0`, `0x81d200`, `0x80f190`) are
  functions.
- PC writers (C2S): `WritePacket(p, group, id, sub, -1)` with group/id/sub read from the call (V each,
  19/19; for 45.4.1 from the pushes `6a ff 6a 01 … 6a 04 … 6a 2d`).
- PS4 match by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, behaviour), never by
  PS4 id. RES header (V, every PC RES reader here): `Read_s32` Error (+16); non-zero -> return; else
  `Read_s32` Result, body. PS4 reads `u16 m_usError, s32 m_nResult`. PC NTC readers read **no** header
  (V: 2.5.16, 2.6.16, 2.7.16, 2.27-2.32.16, 37.13.16); PS4 NTCs start with `Read_u16 m_usError`. PS4 C2S
  writers start with `Write_u16 0` (PS4 framing), PC C2S bodies do not.
- **Walk**: `specs/006-packet-pattern-coverage/research/T009-walk.py` (stdlib; run from `D:/ddon-data`
  with `python -X utf8 -I specs/006-packet-pattern-coverage/research/T009-walk.py`; holds every PC layout
  below, the PS4 counter-test variants and `tally` fields). Input `packets/decrypted_raw/*/`, every file
  whose suffix is `.<g>_<id>_<sub>` of the 48 ids (each suffix carries exactly one packet name: the
  script prints the names per id). Header check: group, u16 id, sub, source (0x00 C2S, 0x34 S2C). Body
  from 0x09; fit = end within the last 15 bytes, no overrun. **Totals: 1,342 files, header 1,342/1,342,
  fit 1,342/1,342, no RES with Error != 0.** Samples: file (relative to `packets/decrypted_raw/`), size,
  sha256 first 16 hex digits, body end offset.

Field-name sources: PS4 DWARF member (`m_`/type prefix dropped) **V**; other names **I** with the basis
stated; a Season 3 field without code backing is `unk_*` (server names only as leads in comments).

## 1. Shared structures

### 1.1 Mail (group 37) — identical to PS4

| Struct | PC reader | PS4 | Wire (PC 03040008 = PS4) |
| --- | --- | --- | --- |
| `CDataCommunityCharacterBaseInfo` | `0x75ecf0` | `CCommunityCharacterBaseInfo` | `Character.hexpat` (u32, 3 MtString) (V) |
| `CDataMailInfo` | element `0x76e5a0`, list `0x76e480` | `Read_CDataMailInfo_ 0x19f53b0` / list `__0 0x19f65f0`: {u64 m_ullId, u8 m_ucState, u8 m_ucItemState, m_BaseInfo, MtString m_wstrSenderName, MtString m_wstrMailText, s64 m_llSenderDate} | u64 Id, u8 State, u8 ItemState, CDataCommunityCharacterBaseInfo BaseInfo, MtString SenderName, MtString MailText, s64 SenderDate (V) |
| `CDataMailAttachmentInfo` (inline) | inside each list below | {u64 m_ullAttachmentId, b8 m_bIsReceived} | u64 AttachmentId, bool IsReceived (V) |
| `CDataMailItemInfo` | list `0x76e630` | `0x19f5510` {AttachmentInfo, u32 m_unItemId, u16 m_usNum} | AttachmentInfo, u32 ItemId, u16 Num (V) |
| `CDataMailGPInfo` | list `0x76e350` | `0x19f57b0` {AttachmentInfo, u32 m_unNum, u32 m_unType} | AttachmentInfo, u32 Num, u32 Type (V) |
| `CDataMailOptionCourseInfo` | list `0x76e890` | `0x19f5a40` {AttachmentInfo, u32 m_unOptionCourseId, u32 m_unOptionCourseLineupId, u32 m_unTime} | same (V) |
| `CDataMailLegendPawnInfo` | list `0x76e760` | `0x19f5d00` {AttachmentInfo, u32 m_unPawnId, MtString m_wstrName} | same (V) |
| `CDataMailAttachmentList` | `0x76e2f0` (4 lists) | {m_ItemList, m_GPList, m_OptionCourseList, m_LegendPawnList} | 4 x MtTypedArray in that order (V) |
| `CDataMailTextInfo` | `0x76e9e0` | {MtString m_wstrText, CMailAttachmentList} | MtString Text, CDataMailAttachmentList (V) |

Mail attachments do **not** reuse the item types of `Item.hexpat` (`CDataItemList` etc.): they are
their own PS4 classes (V).

### 1.2 Stamp (group 45) — Season 3 shapes

| Struct | PC reader | PS4 02020005 | Wire (PC 03040008) |
| --- | --- | --- | --- |
| `CDataStampBonus` | list `0x77a380` {u32,u32,u32} | {u32 m_unBonusType, u32 m_unBonusValue} | **3 x u32** (S3 +1, V); which u32 is new: I (server lead: `Unk0, BonusType, BonusValue`, new first) |
| stamp asset (PS4 `CDataStampBonusDaily` = `CDataStampBonusTotal` shape) | list `0x77a6b0` {list `0x77a380`, u16, u8} | {MtTypedArray<CDataStampBonus> m_StampBonus, u16 m_usStampNum, u8 m_ucRecieveState} | list StampBonus, u16 StampNum, u8 RecieveState (V order, names V by matching shape) |
| daily campaign (S3 wrapper) | list `0x77a490` {u32, u32, list `0x77a6b0`} | — | u32 unk_u32_0, u32 unk_u32_1, list asset (S3, V shape) |
| total (S3 wrapper) | `0x77a7d0` {u16, list `0x77a6b0`} | (PS4 had `u16 m_usTotalStampNum` + `m_StampBonusTotal` at packet level) | u16 TotalStampNum (I: position + PS4 member), list asset |
| check pair (S3) | list `0x77a5c0` {u32, u32} | — | u32 unk_u32_0, u32 unk_u32_1 |

Capture link (I): in every walked capture the {u32, u32} of the 45.0.2 daily wrapper, of the 45.1.2
check list and of the 45.3.1 request carry the same values `(1, 77)`; they identify a daily campaign.

### 1.3 CDataCharacterInfo (2.0.2) — PC `0x75c2a0`, PS4 `Read_CDataCharacterInfo_ 0x1a2f950`

| # | PC 03040008 | PS4 02020005 | Name / source |
| --- | --- | --- | --- |
| 1-3 | u32 x3 | u32 m_unCharacterId, m_unUserId, m_unVersion | CharacterId, UserId, Version (V) |
| 4-5 | MtString x2 | m_wstrFirstName, m_wstrLastName | FirstName, LastName (V) |
| 6 | `0x764550` | CEditInfo | `CDataEditInfo` (Context.hexpat, V) |
| 7 | `0x77a810` {u32,u32,u8,u32 x9} | CStatusInfo {u32 m_unHp, m_unStamina, u8 m_ucRevivePoint, u32 m_unMaxHp, m_unMaxStamina, m_unWhiteHp, m_unGainHp, m_unGainStamina, m_unGainAttack, m_unGainDefense, m_unGainMagicAttack, m_unGainMagicDefense} | `CDataStatusInfo` (new type, V) |
| 8 | u8 | m_ucJob | Job (V) |
| 9 | list `0x75c660` | m_CharacterJobDataList | `CDataCharacterJobData` (Pawn.hexpat, V) |
| 10 | list `0x76c670` | m_PlayPointList | `CDataJobPlayPoint` (Job.hexpat, V) |
| 11-12 | list `0x75c190` x2 | m_CharacterEquipDataList, m_CharacterEquipViewDataList | `CDataCharacterEquipData` (Pawn.hexpat; S3 `CDataEquipItemInfo`, V) |
| 13 | list `0x766120` | m_CharacterEquipJobItemList | `CDataEquipJobItem` (Pawn.hexpat, V) |
| 14 | u8 | m_ucJewelrySlotNum | JewelrySlotNum (V) |
| 15 | **list `0x766210` {u8, u16}** | — | `MtTypedArray<EquipStatParam> unk_List` (S3, V shape: the same reader as `CDataPawnInfo.unk_List` in Pawn.hexpat; server lead `EmblemStatList`) |
| 16 | list `0x75c570` | m_CharacterItemSlotInfoList | `CDataCharacterItemSlotInfo` (Server.hexpat, V by reader identity) |
| 17 | list `0x77c5a0` | m_WalletPointList | `CDataWalletPoint` (Character.hexpat, V) |
| 18-19 | u8 x2 | m_ucMyPawnSlotNum, m_ucRentalPawnSlotNum | V |
| 20 | list `0x7702d0` | m_OrbStatusList | `CDataOrbPageStatus` (Pawn.hexpat, V) |
| 21 | list `0x75cee0` {u32, MtString, list `0x75cdc0` {u32, MtString, u32, bool}} | m_MsgSetList: CDataCharacterMsgSet {u32 m_unSetNo, MtString m_wstrMsgSetName, MtTypedArray<CDataCharacterMessage {u32 m_unMessageNo, MtString m_wstrMessage, u32 m_unEmotion, b8 m_bEmotoChat}>} | `CDataCharacterMsgSet`, `CDataCharacterMessage` (new, V) |
| 22 | list `0x778990` (element `0x778a80` {u32 x5, u8}) | CDataShortCut {u32 m_unPageNo, m_unButtonNo, m_unShortcutID, m_unU32Data, m_unF32Data, u8 m_ucExexType} | `CDataShortCut` (new, V) |
| 23 | list `0x75ea80` {u32, u32, u8, u8, u32} | CDataCommunicationShortCut {u32 m_unPageNo, m_unButtonNo, u8 m_ucType, m_ucCategory, u32 m_unId} | `CDataCommunicationShortCut` (new, V) |
| 24 | `0x76ed10` | CMatchingProfile | `CDataMatchingProfile` (Login.hexpat, V) |
| 25 | `0x7596f0` | CArisenProfile | `CDataArisenProfile` (Pawn.hexpat, V) |
| 26-29 | bool x4 | b8 m_bHideEquipHead, m_bHideEquipLantern, m_bHideEquipHeadPawn, m_bHideEquipLanternPawn | V |
| 30-31 | u8 x2 | m_ucArisenProfileShareRange, m_ucOnlineStatus | V |

Season 3 difference: item 15 only (plus the Season 3 `CDataEquipItemInfo` inside items 11-12, already
in Login.hexpat). Counter-test (2.0.2 walk): dropping item 15 fails 22/42 captures (the 22 with a
non-empty list; up to 17 elements).

## 2. 2.0.1 C2S_CHARACTER_DECIDE_CHARACTER_ID_REQ / 2.0.2 S2C_…_RES

- PC writer `0x821360` (2,0,1): u32 (V). PS4 `Send_C2S_DECIDE_CHARACTER_ID_REQ 0x19b0510`: u32
  `m_unCharacterID` (V). PS4 mark V.
- PC handler `0x7c7f20` (string `OnPacket_CHARACTER_DECIDE_CHARACTER_ID_RES`), reader `0x802060`: RES
  header, u32, `CDataCharacterInfo 0x75c2a0`, bool, u8[1024] by `0x757de0` (the save-blob reader of
  9.0.2), **u8** (V). PS4 `CPacket_S2C_DECIDE_CHARACTER_ID_RES::ReadPacket 0x19d4760`: `u32
  m_unCharacterID, CCharacterInfo m_CharacterInfo, b8 m_bIsReturnPrepare, u8[1024] m_ucBin` (V). PS4 mark
  V.
- Season 3: CharacterInfo item 15 (§ 1.3) and the trailing u8 (no PS4 member; name open, server lead
  `Unk1`; value 1 in 42/42 captures).
- Wire REQ `u32 CharacterID;` RES `s32 Error; if (Error == 0) { s32 Result; u32 CharacterID;
  CDataCharacterInfo CharacterInfo; bool IsReturnPrepare; CharacterBinSaveData Bin; u8 unk_u8; }` —
  `CharacterBinSaveData` from `CharacterData.hexpat` (1024 bytes, the 9.x blob).
- Walk: REQ 42/42 slack 3; `stream1-marked.pcapng_tcp-stream-34/11887_…2_0_1` (16 B,
  `27f5d50354e2c456`), end 0xd. RES 42/42 slack 0-12;
  `stream51-marked.pcapng_tcp-stream-10/10055_…2_0_2` (4544 B, `091e86ae0a1391b7`), end 0x11c0. PS4 body
  counter-test (no item 15, no trailing u8) fails 22/42.

## 3. 2.5.16 S2C_CHARACTER_2_5_16_NTC (unresolved -> settled: no PS4 counterpart, I)

- PC handler `0x7c7770`: `Read_u8` (no header), then `sub_B9F450(sItemManager, u8, 0, 0)` (V).
  `sub_B9F450` stores the 64-bit pair at `this + 4*(772 + 2*n)` for `n < 17`; `sub_B9F090` writes the same
  array indexed by wallet type 1..16, and the 2.0.2 handler first clears all 17 entries with
  `sub_B9F450` (`0x7c8021-0x7c8035`), then fills them from `CharacterInfo.WalletPointList` through
  `sub_B9F090(value, type)` (`0x7c8044-0x7c806f`) (V). So 2.5.16 zeroes the client's wallet value of
  the type it carries (V by code). PS4 holds the same per-type store as `sItemManager::mPoint u64[9]`,
  written only by `setGoldToServer`/`setGoldToServerDirect`, whose callers are RES handlers (DECIDE_
  CHARACTER_ID, STAY_INN, BUY_AREA_QUEST_HINT, RELEASE_*ORB_ELEMENT, RENT_REGISTERED_PAWN, BUY_SHOP_GOODS,
  SELL_ITEM): no PS4 notice resets a wallet type (V for those callers); PS4 mark **X(I)** (Season
  3-only).
- Triage's shape-sharing PS4 candidates (7 bodies of `u16 + u8`) are rejected by behaviour; the server
  lead `S2C_REWARD_BOX_LIST_NUM_NTC?` is **C**: PS4 `OnPacket_S2C_REWARD_BOX_LIST_NUM_NOTICE 0x312390`
  stores `mRecvGetRewardBoxListNum` and drives GUI/chat, not the wallet store.
- Wire `u8 WalletPointType;` (I name: the value indexes the wallet store; type `E_WALLET_POINT_TYPE` of
  Character.hexpat fits, values to 16).
- Walk 2/2 slack 6; `stream59-epi-1-2-party-hobo1-marked.pcapng_tcp-stream-11/10215_…2_5_16` (16 B,
  `93e38114e3848cf0`): u8 `0x0a` (both captures 10), end 0xa. PS4-framing counter (u16 first) also fits
  (2/2): the 1-byte body cannot be discriminated by the fit window; the layout rests on the PC code.

## 4. 2.6.16 S2C_CHARACTER_CONTENTS_RELEASE_ELEMENT_NTC (unresolved -> V)

- PC handler `0x7c7400`: list `0x75d050` of {u32} (no header); for each element `v < 0x5e` it sets bit
  `v` of the bitset at `sQuestManagerExt + 0x34` (V). PS4 `OnPacket_S2C_CHARACTER_CONTENTS_RELEASE_
  ELEMENT_NOTICE 0x2ea0c0`: u16 error, `Read_CDataCharacterReleaseElement_` list {u32
  m_unReleaseElementNo}; for each `v <= 0x3a` sets `sQuestManagerExtPointer->mReleaseContents.mBit` (V).
  Same behaviour, wider bit range in Season 3 (0x5e vs 0x3a): PS4 mark **V** (behaviour).
- Wire `MtTypedArray<CDataCharacterReleaseElement> ReleaseElementList;` with element `u32
  ReleaseElementNo` (V).
- Walk 41/41 slack 7-15, up to 59 elements; `stream21-failedlogin-marked.pcapng_tcp-stream-48/12264_…2_6_16`
  (256 B, `2166d59903d9a6c9`), end 0xf9. PS4-framing counter fails 41/41.

## 5. 2.7.16 S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC

- PC handler `0x7c7da0`, reader `0x801f60` (no header): list `0x75cbd0` of `CDataCharacterListElement`
  (Character.hexpat, S3 trailing u8), list `0x77c0d0` of {u32, MtString} (V). PS4
  `OnPacket_S2C_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC 0x2f7ed0`: `MtTypedArray<CDataCharacterListElement>
  m_UpdateCharacterList, MtTypedArray<CDataUpdateMatchingProfileInfo> m_UpdateMatchinfProfileList`
  {u32 m_unCharacterID, MtString m_wstrComment} (V). PS4 mark V.
- Wire `MtTypedArray<CDataCharacterListElement> UpdateCharacterList;
  MtTypedArray<CDataUpdateMatchingProfileInfo> UpdateMatchinfProfileList;` (PS4 DWARF spelling).
- Walk 111/111 slack 8-15, max 1 element / 0 profiles;
  `stream1-marked.pcapng_tcp-stream-35/12016_…2_7_16` (64 B, `6489ecd8cf9427ba`), end 0x33. PS4 body
  (element without the S3 u8) fails 107/111 (the 4 others have an empty first list).

## 6. 2.12.1 COMMUNITY_CHARACTER_STATUS_GET_REQ / 2.12.2 …_RES

- PC writer `0x821190` (2,12,1): u32 (V); PS4 `0x19cad40`: u32 `m_unType` (V). PC handler `0x7c7af0`,
  reader `0x801ed0`: RES header only (V); PS4 `0x332270`: header only (V). PS4 mark V.
- Wire REQ `u32 Type;` RES `s32 Error; if (Error == 0) s32 Result;`.
- Walk REQ 45/45 slack 3 (Type 1 in 45/45; `stream1-marked.pcapng_tcp-stream-35/12067_…2_12_1`, 16 B,
  `2981bc3524d37358`, end 0xd). RES 45/45 slack 15 (`…/12069_…2_12_2`, 32 B, `d09bb40c004e7422`, end 0x11).

## 7. 2.16.1 CHARACTER_POINT_REVIVE_REQ / 2.16.2 …_RES

- PC writer `0x820ef0` (2,16,1): u32 (V); PS4 `0x19cbc30`: u32 `m_unHpMax` (V). PC handler `0x7c76a0`,
  reader `0x801cc0`: RES header, u8 (V); PS4 `0x32e470`: u8 `m_ucRevivePoint` (V). PS4 mark V.
- Wire REQ `u32 HpMax;` RES `… s32 Result; u8 RevivePoint; }`.
- Walk REQ 5/5 slack 3 (`stream85-marked.pcapng_tcp-stream-11/102918_…2_16_1`, 16 B,
  `0631646cec3ef1c1`, end 0xd). RES 5/5 slack 14 (`…/102920_…2_16_2`, 32 B, `af6e0becfeceb212`, end 0x12).

## 8. 2.18.1 CHARACTER_PENALTY_REVIVE_REQ / 2.18.2 …_RES

- PC writer `0x820e00` (2,18,1): **u32, u32** (V). PS4 `0x19cbeb0`: u32 `m_unHpMax` (V; its caller
  `cNetGameServer::reqCharacterPenaltyRevive` passes `mWeakHpMax_pri`). PC caller `0x879940` pushes `ebp`
  then `ebx` (`0x879a05`/`0x879a06`): first u32 = `(int)` of `sub_872760(status)`, second = `(int)` of
  `sub_65AB10(status)` (V); Hex-Rays shows the call as `(conn, a2, 0)`, which is wrong (the second value
  is 4265 in both captures). PS4 mark V (S3 +u32).
- PC handler `0x7c75e0`, reader `0x801c30`: header only (V); PS4 `0x32e750`: header only (V).
- Wire REQ `u32 HpMax; u32 unk_u32;` (HpMax I: PS4 position; the walk shows 3198/4265, first < second).
  RES header only.
- Walk REQ 2/2 slack 15 (`stream85-marked.pcapng_tcp-stream-11/116836_…2_18_1`, 32 B,
  `46f019b656645830`, end 0x11). PS4 body (one u32) fails 2/2. RES 2/2 slack 15 (`…/116839_…2_18_2`,
  32 B, `5d8a483827e7ca88`, end 0x11).

## 9. 2.24.1 GET_REVIVE_CHARGEABLE_TIME_REQ / 2.24.2 …_RES

- PC writer `0x821930`: empty (V); PS4 `0x19cc670`: empty (V). PC handler `0x7c9910`, reader `0x8028d0`:
  header, u32 (V); PS4 `0x32ece0`: u32 `m_unRemainTime` (V). PS4 mark V.
- Wire REQ empty; RES `… s32 Result; u32 RemainTime; }`.
- Walk REQ 3/3 slack 7 (`stream1-marked.pcapng_tcp-stream-35/12824_…2_24_1`, 16 B, `dbfdcb85af506116`,
  end 0x9); RES 3/3 slack 11 (`…/12827_…2_24_2`, 32 B, `f057aa0444a1d82e`, end 0x15).

## 10. 2.25.1 CHARGE_REVIVE_POINT_REQ / 2.25.2 …_RES

- PC writer `0x8210d0`: empty (V); PS4 `0x19cc7a0`: empty (V). PC handler `0x7c7a40`, reader `0x801e50`:
  header, u8 (V); PS4 `0x32ee40`: u8 `m_ucRevivePoint` (V). PS4 mark V.
- Walk REQ 2/2 slack 7 (`stream85-marked.pcapng_tcp-stream-11/125890_…2_25_1`, 16 B,
  `7d464ed6b6a936ed`, end 0x9); RES 2/2 slack 14 (`…/125893_…2_25_2`, 32 B, `20ba35806cfda8cd`, end 0x12).

## 11. 2.27.16-2.32.16 lantern and death-penalty notices (unresolved -> settled)

PC handlers read no header. Behaviour key: PS4 START/FINISH_LANTERN apply/cure object condition
`0x3003`, START/FINISH_DEATH_PENALTY `0x3006`; the four `*_OTHER_NOTICE` read u32 `m_unCharacterID` and
do nothing else (V, `0x32a660`, `0x32a6f0`, `0x32aaa0`, `0x32ab30`).

| id | PC handler | PC body (V) | PC behaviour (V) | PS4 match | Wire |
| --- | --- | --- | --- | --- | --- |
| 2.27.16 | `0x7c9f60` | u32 | if u32 != 0: `sub_47B400(player, 0, 0x3003, {1}, 1)` (set condition 0x3003) | `OnPacket_S2C_START_LANTERN_NOTICE 0x32a3e0` {u32 m_unRemainTime}, sets 0x3003: **V** (behaviour) | `u32 RemainTime;` |
| 2.28.16 | `0x7c8ea0` | none | clears 0x3003 (`sub_47B400(…, 0x3003, {0}, 0)`) | `OnPacket_S2C_FINISH_LANTERN_NOTICE 0x32a540` (no body), cures 0x3003: **V** | empty |
| 2.29.16 | `0x7ca090` | u32 | none | one of the four `*_OTHER_NOTICE` (V); START_LANTERN_OTHER (`0x32a660`) **I** (order) | `u32 CharacterID;` (V: all four share the member) |
| 2.30.16 | `0x7c8f40` | u32 | none | as above; FINISH_LANTERN_OTHER (`0x32a6f0`) **I** | `u32 CharacterID;` |
| 2.31.16 | `0x7c9d50` | u32 | sets 0x3006, timer `= 30 * u32` | `OnPacket_S2C_START_DEATH_PENALTY_NOTICE 0x32a780` {u32 m_unRemainTime}, 0x3006: **V** | `u32 RemainTime;` |
| 2.32.16 | `0x7c8d90` | none | clears 0x3006, timer 0 | `OnPacket_S2C_FINISH_DEATH_PENALTY_NOTICE 0x32a950` (no body), cures 0x3006: **V** | empty |

2.29.16/2.30.16 identity: the PC handlers are no-ops after `Read_u32` and so are all four PS4 OTHER
notices; behaviour cannot separate them. The PC ids 2.27-2.34 run START_LANTERN, FINISH_LANTERN, ?, ?,
START_DP, FINISH_DP, ?, ? with the four V ids at 27/28/31/32 and the same no-op u32 handlers at 29, 30
(`0x7ca090`, `0x7c8f40`) and 33, 34 (`0x7c9f00`, `0x7c8e40`); this matches PS4 source order (lantern
OTHER pair after the lantern pair, death-penalty OTHER pair last) (I). The wire layout is the same for
every candidate (V).

Walk (all fit, PS4-framing counter passes on every one: 1- or 4-byte bodies cannot be told apart by
the window; layouts rest on code):
2.27.16 25/25 slack 3 (`stream10-musicplayer-marked.pcapng_tcp-stream-9/10322_…2_27_16`, 16 B,
`71e857aa2a62307d`, end 0xd); 2.28.16 9/9 slack 7 (`stream85-marked.pcapng_tcp-stream-11/107765_…2_28_16`,
16 B, `9f88ce4757d63a33`, end 0x9); 2.29.16 3/3 slack 3
(`stream6-annilot-hobo-marked.pcapng_tcp-stream-2/16713_…2_29_16`, 16 B, `897310dad795bed5`, end 0xd);
2.30.16 1/1 slack 3 (`stream85-marked.pcapng_tcp-stream-11/60294_…2_30_16`, 16 B, `54df8a430540d438`, end
0xd); 2.31.16 2/2 slack 3 (`…/116838_…2_31_16`, 16 B, `99a3f80dd2544cbb`, RemainTime 900, end 0xd);
2.32.16 1/1 slack 7 (`…/123073_…2_32_16`, 16 B, `63f8a828b3036ebc`, end 0x9).

## 12. 2.38.1 SET_ONLINE_STATUS_REQ / 2.38.2 …_RES

- PC writer `0x821e70`: u8, bool (V); PS4 `0x19c5c40`: u8 `m_ucStatusID`, b8 `m_bIsSaveSetting` (V). PC
  handler `0x7c9cb0`, reader `0x802af0`: header, u8 (V); PS4 `0x2f8130`: u8 `m_ucStatusID` (V). PS4 mark V.
- Walk REQ 2/2 slack 5 (`stream85-marked.pcapng_tcp-stream-11/123977_…2_38_1`, 16 B, `3cb5c56f8ae3e4ae`,
  end 0xb); RES 2/2 slack 14 (`…/123979_…2_38_2`, 32 B, `0b33bd7491b60ca4`, end 0x12).

## 13. 37.0-37.2 MAIL_GET_LIST_HEAD / DATA / FOOT

| id | PC | PS4 | Wire |
| --- | --- | --- | --- |
| 37.0.1 | writer `0x82f220`: empty | `Send_C2S_MAIL_GET_LIST_HEAD_REQ 0x19c89f0`: empty | empty (V) |
| 37.0.2 | handler `0x7e3130`, reader `0x80ecd0`: header, u32 | `0x32be80`: u32 `m_unNum` | `… u32 Num; }` (V) |
| 37.1.1 | writer `0x82f070`: u32, u32 | `0x19c8b20`: u32 `m_unOffset`, u32 `m_unNum` | `u32 Offset; u32 Num;` (V) |
| 37.1.2 | handler `0x7e2f90`, reader `0x80ebc0`: header, list `0x76e480` | `0x32bfb0`: `Read_CDataMailInfo__0` `m_MailInfo` | `… MtTypedArray<CDataMailInfo> MailInfo; }` (V) |
| 37.2.1 | writer `0x82f160`: empty | `0x19c8c80`: empty | empty (V) |
| 37.2.2 | handler `0x7e30a0`, reader `0x80ec40`: header only | `0x32c1c0`: header only | header only (V) |

PS4 marks V (all six). Walk: 37.0.1 42/42 slack 7 (`stream1-marked.pcapng_tcp-stream-35/12084_…37_0_1`,
16 B, `b9d53292fcd59e13`, end 0x9); 37.0.2 42/42 slack 11 (`…/12085_…37_0_2`, 32 B, `12c40ee3adbdefb3`,
end 0x15); 37.1.1 42/42 slack 15 (`…/12087_…37_1_1`, 32 B, `50a9b273a29e4a31`, end 0x11); 37.1.2 42/42
slack 4-11, max 1 element (`stream21-failedlogin-marked.pcapng_tcp-stream-48/12397_…37_1_2`, 80 B,
`d4941b540609d569`, end 0x4c); 37.2.1 42/42 slack 7 (`…35/12090_…37_2_1`, 16 B, `8a19d03d569f1bfa`, end
0x9); 37.2.2 42/42 slack 15 (`…35/12091_…37_2_2`, 32 B, `e03decc45c0322cf`, end 0x11). No PS4
counter-test: bodies identical.

## 14. 37.6-37.8 SYSTEM_MAIL_GET_LIST_HEAD / DATA / FOOT

| id | PC | PS4 | Wire |
| --- | --- | --- | --- |
| 37.6.1 | writer `0x82f830`: empty | `0x19c9030`: empty | empty (V) |
| 37.6.2 | handler `0x7e3fb0`, reader `0x80f110`: header, u32 | `0x32c970`: u32 `m_unNum` | `… u32 Num; }` (V) |
| 37.7.1 | writer `0x82f680`: u32, u32 | `0x19c9160`: `m_unOffset`, `m_unNum` | `u32 Offset; u32 Num;` (V) |
| 37.7.2 | handler `0x7e3e40`, reader `0x80f000`: header, list `0x76e480` | `0x32caa0`: `Read_CDataMailInfo__0` `m_MailInfo` | `… MtTypedArray<CDataMailInfo> MailInfo; }` (V; system mail uses the player-mail element) |
| 37.8.1 | writer `0x82f770`: empty | `0x19c92c0`: empty | empty (V) |
| 37.8.2 | handler `0x7e3f20`, reader `0x80f080`: header only | `0x32ccb0`: header only | header only (V) |

PS4 marks V. Walk: 37.6.1 42/42 slack 7 (`stream1-marked.pcapng_tcp-stream-35/12093_…37_6_1`, 16 B,
`ce65c94046550fd5`, end 0x9); 37.6.2 42/42 slack 11 (`…/12094_…37_6_2`, 32 B, `dfe6ae7c4e8161fd`, end
0x15); 37.7.1 42/42 slack 15 (`…/12096_…37_7_1`, 32 B, `8a27553d4b8d86ec`, end 0x11); 37.7.2 42/42 slack
0-15, up to 18 elements (`stream21-failedlogin-marked.pcapng_tcp-stream-48/12407_…37_7_2`, 1856 B,
`394f5608c5d27b4a`, end 0x73c); 37.8.1 42/42 slack 7 (`…35/12099_…37_8_1`, 16 B, `a037e7dae2a58bac`, end
0x9); 37.8.2 42/42 slack 15 (`…35/12100_…37_8_2`, 32 B, `30b3319d2a7a425f`, end 0x11).

## 15. 37.9.1 SYSTEM_MAIL_GET_TEXT_REQ / 37.9.2 …_RES

- PC writer `0x82f8f0` (37,9,1): u64 (V); PS4 `0x19c93f0`: u64 `m_ullId` (V).
- PC handler `0x7e4050` (not a function; linear), reader `0x80f190`: header, u64, `0x76e9e0` = MtString +
  `CDataMailAttachmentList 0x76e2f0` (V). PS4 `0x32cdc0`: u64 `m_ullId`, `m_MailTextInfo` {MtString
  m_wstrText, 4 attachment lists} (V). PS4 mark V.
- Wire REQ `u64 Id;` RES `… s32 Result; u64 Id; CDataMailTextInfo MailTextInfo; }`.
- Walk REQ 7/7 slack 15 (`stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/2873_…37_9_1`, 32 B,
  `c675db3569b09fdd`, end 0x11). RES 7/7 slack 6-15, up to 3 items, GP/course/pawn lists always empty
  (`…/2905_…37_9_2`, 480 B, `befbf6e70fd02b86`, end 0x1d4).

## 16. 37.11.1 SYSTEM_MAIL_GET_ALL_ITEM_REQ / 37.11.2 …_RES

- PC writer `0x82f590` (37,11,1): **u64, u8** (V); its caller `0x872050` forwards (u64, u8) from UI
  state. PS4 `0x19c9530`: u64 `m_ullId` only (V). PS4 mark V (S3 +u8).
- PC handler `0x7e3c10`, reader `0x80eee0`: header, u64, `CDataMailAttachmentList 0x76e2f0` (V). PS4
  `CPacket_S2C_SYSTEM_MAIL_GET_ALL_ITEM_RES::ReadPacket 0x19ddb50`: u64 `m_ullId`, 4 lists of
  `m_AttachmentList` (V). PS4 mark V.
- Wire REQ `u64 Id; u8 unk_u8;` (server lead `StorageType`; 13 in 5/5 captures). RES `… s32 Result; u64
  Id; CDataMailAttachmentList AttachmentList; }`.
- Walk REQ 5/5 slack 14 (`stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/2889_…37_11_1`, 32
  B, `4a1c440e4d677f76`: Id `0x1aa8128f`, u8 `0x0d`, end 0x12); the PS4 body (u64 only) also fits 5/5
  (1 byte inside the window): the u8 rests on the PC writer. RES 5/5 slack 8-10, up to 3 items
  (`…/2997_…37_11_2`, 96 B, `bf1af697ef535f07`, end 0x56).

## 17. 37.13.16 S2C_MAIL_SYSTEM_MAIL_SEND_NTC

- PC handler `0x7e4180` (no header): `CDataMailInfo` element reader `0x76e5a0`, then `sub_7E4120` adds it
  to the list at manager `+41452` (V). That list is the system-mail one: the 37.7.2 handler path
  `sub_7E3DB0` uses `+41432`/`+41452`, while 37.5.16 (`0x7e3330`, same reader) adds to `+41412`, the
  player-mail list of 37.1.2 (`+41392`/`+41412`) (V). PS4 `OnPacket_S2C_SYSTEM_MAIL_SEND_NTC 0x32d8e0`:
  u16 error, `Read_CDataMailInfo_`, `addMailInfo(&mAddSysMailList)` (V); `OnPacket_S2C_MAIL_SEND_NTC
  0x32c7b0` reads the same body into `mAddMailList`. PS4 mark **V** (behaviour: system list).
- Wire `CDataMailInfo MailInfo;`.
- Walk 5/5 slack 7 (`stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/2532_…37_13_16`, 48 B,
  `4e22cc59180e436f`, end 0x29). PS4-framing counter fits too (5/5): the 2-byte shift sits in the
  window; framing rests on the PC handler.

## 18. 45.0.1 STAMP_BONUS_GET_LIST_REQ / 45.0.2 …_RES

- PC writer `0x83f3f0`: empty (V); PS4 `Send_C2S_STAMP_BONUS_GET_LIST_REQ 0x19cd010`: empty (V).
- PC handler `0x7fe140` (not a function; calls `0x81d170` after allocating with `sub_78D900`), reader
  `0x81d170`: header, list `0x77a490` (daily wrapper), `0x77a7d0` (u16 + asset list) (V). PS4
  `CPacket_S2C_STAMP_BONUS_GET_LIST_RES::ReadPacket 0x19df1a0`: `u16 m_usTotalStampNum,
  MtTypedArray<CDataStampBonusDaily> m_StampBonusDaily, MtTypedArray<CDataStampBonusTotal>
  m_StampBonusTotal` (V). PS4 mark V (Season 3 restructured).
- Season 3 (V by code): the daily list is wrapped in a list of {u32, u32, list}; TotalStampNum moved
  behind it (I: the u16 before the total list); `CDataStampBonus` has 3 u32.
- Wire RES `… s32 Result; MtTypedArray<CDataStampBonusDailyGroup> DailyStamp; u16 TotalStampNum;
  MtTypedArray<CDataStampBonusAsset> TotalStamp; }` (§ 1.2; wrapper names are proposals).
- Walk REQ 81/81 slack 7 (`stream10-musicplayer-marked.pcapng_tcp-stream-9/10648_…45_0_1`, 16 B,
  `4f0ebe92bb3281ec`, end 0x9). RES 81/81 slack 3: 1 daily group `(1, 77)` with 8 assets, 10 total assets
  (`…/10649_…45_0_2`, 384 B, `266bae810ec5f40d`, end 0x17d). PS4 body counter-test fails 81/81.

## 19. 45.1.1 STAMP_BONUS_CHECK_REQ / 45.1.2 …_RES

- PC writer `0x83f330`: empty (V); PS4 `0x19cd140`: empty (V).
- PC handler `0x7fe070` (not a function), reader `0x81d0d0`: header, list `0x77a5c0` {u32, u32}, u8, u8
  (V). PS4 `CPacket_S2C_STAMP_BONUS_CHECK_RES::ReadPacket 0x19df230` (and recompilation S2C.cpp:11561):
  `u16 m_usTotalStampNum, u8 m_ucisRecieveBonusDaily, u8 m_ucisRecieveBonusTotal` (V). PS4 mark V.
- Season 3 (V by code): the u16 is replaced by a list of {u32, u32} (§ 1.2 check pair). The two u8 keep
  the PS4 names by position (I).
- Wire RES `… s32 Result; MtTypedArray<CDataStampCheck> StampCheck; u8 IsRecieveBonusDaily; u8
  IsRecieveBonusTotal; }`.
- Walk REQ 84/84 slack 7 (`stream1-marked.pcapng_tcp-stream-35/12111_…45_1_1`, 16 B, `0afcfa64499f939e`,
  end 0x9). RES 84/84 slack 1-9, at most 1 element
  (`stream10-musicplayer-marked.pcapng_tcp-stream-9/10426_…45_1_2`, 32 B, `28b1f236d6d53e55`: element
  `(1, 77)`, u8 0, u8 1, end 0x1f). The PS4 body fits too (0/84 fails): the captures cannot discriminate;
  the list rests on the PC reader. T001's `recompiled_body yes` for 45.1.2 is a real body, but it is
  the PS4 layout (contradicted for 03040008).

## 20. 45.3.1/45.3.2 RECIEVE_DAILY and 45.4.1/45.4.2 RECIEVE_TOTAL (Season 3-exclusive, confirmed)

- PC strings: `OnPacket_STAMP_BONUS_GET_LIST_RES`, `…_UPDATE_RES` (45.2), `…_CHECK_RES`,
  `…_RECIEVE_DAILY_RES` (45.3.2 `0x7fe1f0`), `…_RECIEVE_TOTAL_RES` (45.4.2 `0x7fe280`) (V). PS4 stamp
  symbols: `GET_LIST`, `CHECK`, `RECIEVE` (`Send_C2S_STAMP_BONUS_RECIEVE_REQ 0x19cd270`: u8
  `m_ucBonusType`; `OnPacket_S2C_STAMP_BONUS_RECIEVE_RES 0x330910`: header), `ADD_TOTAL_NUM` (`0x19cd3c0`
  empty; `0x330a20` header) (V). No PS4 class named RECIEVE_DAILY/RECIEVE_TOTAL (V by symbol search),
  and PS4's only receive request carries `u8 BonusType`, a body neither PC request has (V) -> exclusive
  **confirmed by code**. Descent (I): PC splits PS4's RECIEVE by bonus type; both PC writers are called
  from one UI branch (`0xebc489`: `0x8785c0` -> 45.3.1 writer, else `0x878650` -> 45.4.1 writer).
- 45.3.1 PC writer `0x83f4b0` (45,3,1): u32, u32 (V; arguments from the UI object `+0x25a8`, `+0x25ac`).
  45.3.2 handler `0x7fe1f0` (not a function), reader `0x81d200`: header only (V).
- 45.4.1 PC writer `0x83f5a0` (not a function): `WritePacket(p, 0x2d, 4, 1, -1)`, no body (V). 45.4.2
  handler `0x7fe280`, reader `0x81d290`: header only (V).
- Wire 45.3.1 `u32 unk_u32_0; u32 unk_u32_1;` (the daily-group pair of § 1.2, I by capture values; server
  `Unk0, Unk1`). 45.3.2, 45.4.2 header only; 45.4.1 empty.
- Walk: 45.3.1 40/40 slack 15, values `(1, 77)` in 40/40
  (`stream10-musicplayer-marked.pcapng_tcp-stream-9/10655_…45_3_1`, 32 B, `62479f31cf92f1de`, end 0x11);
  PS4 RECIEVE body (u8) fails 40/40. 45.3.2 40/40 slack 15 (`…/10660_…45_3_2`, 32 B, `c1cc45440dd3d6be`,
  end 0x11). 45.4.1 1/1 slack 7 (`stream46-bofarming-mq-marked.pcapng_tcp-stream-11/10581_…45_4_1`, 16 B,
  `ca8c60d739a5c957`, end 0x9; a PS4 u8 body also fits). 45.4.2 1/1 slack 15 (`…/10586_…45_4_2`, 32 B,
  `f13561655f8059a3`, end 0x11).

## 21. Summary

PS4 mark: V = confirmed by code (symbol + body, or behaviour); V(S3) = same class, Season 3 body
differs; X = no PS4 counterpart (confirmed by code); X(I) = none found, inferred. Body bytes for
Error == 0 (lists `var`).

| id | name (file) | PS4 | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 2.0.1 | C2S_CHARACTER_DECIDE_CHARACTER_ID_REQ | V | 4 | 11887 | 42/42 |
| 2.0.2 | S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | V(S3: CharacterInfo list, trailing u8) | var | 10055 | 42/42 |
| 2.5.16 | S2C_CHARACTER_2_5_16_NTC | X(I) (wallet-type reset) | 1 | 10215 | 2/2 |
| 2.6.16 | S2C_CHARACTER_CONTENTS_RELEASE_ELEMENT_NTC | V (behaviour) | var | 12264 | 41/41 |
| 2.7.16 | S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC | V(S3 list element) | var | 12016 | 111/111 |
| 2.12.1 | C2S_CHARACTER_COMMUNITY_CHARACTER_STATUS_GET_REQ | V | 4 | 12067 | 45/45 |
| 2.12.2 | S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_GET_RES | V | 0 | 12069 | 45/45 |
| 2.16.1 | C2S_CHARACTER_CHARACTER_POINT_REVIVE_REQ | V | 4 | 102918 | 5/5 |
| 2.16.2 | S2C_CHARACTER_CHARACTER_POINT_REVIVE_RES | V | 1 | 102920 | 5/5 |
| 2.18.1 | C2S_CHARACTER_CHARACTER_PENALTY_REVIVE_REQ | V(S3 +u32) | 8 | 116836 | 2/2 |
| 2.18.2 | S2C_CHARACTER_CHARACTER_PENALTY_REVIVE_RES | V | 0 | 116839 | 2/2 |
| 2.24.1 | C2S_CHARACTER_GET_REVIVE_CHARGEABLE_TIME_REQ | V | 0 | 12824 | 3/3 |
| 2.24.2 | S2C_CHARACTER_GET_REVIVE_CHARGEABLE_TIME_RES | V | 4 | 12827 | 3/3 |
| 2.25.1 | C2S_CHARACTER_CHARGE_REVIVE_POINT_REQ | V | 0 | 125890 | 2/2 |
| 2.25.2 | S2C_CHARACTER_CHARGE_REVIVE_POINT_RES | V | 1 | 125893 | 2/2 |
| 2.27.16 | S2C_CHARACTER_START_LANTERN_NTC | V (behaviour) | 4 | 10322 | 25/25 |
| 2.28.16 | S2C_CHARACTER_FINISH_LANTERN_NTC | V (behaviour) | 0 | 107765 | 9/9 |
| 2.29.16 | S2C_CHARACTER_START_LANTERN_OTHER_NTC | OTHER-family V, which one I | 4 | 16713 | 3/3 |
| 2.30.16 | S2C_CHARACTER_FINISH_LANTERN_OTHER_NTC | OTHER-family V, which one I | 4 | 60294 | 1/1 |
| 2.31.16 | S2C_CHARACTER_START_DEATH_PENALTY_NTC | V (behaviour) | 4 | 116838 | 2/2 |
| 2.32.16 | S2C_CHARACTER_FINISH_DEATH_PENALTY_NTC | V (behaviour) | 0 | 123073 | 1/1 |
| 2.38.1 | C2S_CHARACTER_SET_ONLINE_STATUS_REQ | V | 2 | 123977 | 2/2 |
| 2.38.2 | S2C_CHARACTER_SET_ONLINE_STATUS_RES | V | 1 | 123979 | 2/2 |
| 37.0.1 | C2S_MAIL_MAIL_GET_LIST_HEAD_REQ | V | 0 | 12084 | 42/42 |
| 37.0.2 | S2C_MAIL_MAIL_GET_LIST_HEAD_RES | V | 4 | 12085 | 42/42 |
| 37.1.1 | C2S_MAIL_MAIL_GET_LIST_DATA_REQ | V | 8 | 12087 | 42/42 |
| 37.1.2 | S2C_MAIL_MAIL_GET_LIST_DATA_RES | V | var | 12397 | 42/42 |
| 37.2.1 | C2S_MAIL_MAIL_GET_LIST_FOOT_REQ | V | 0 | 12090 | 42/42 |
| 37.2.2 | S2C_MAIL_MAIL_GET_LIST_FOOT_RES | V | 0 | 12091 | 42/42 |
| 37.6.1 | C2S_MAIL_SYSTEM_MAIL_GET_LIST_HEAD_REQ | V | 0 | 12093 | 42/42 |
| 37.6.2 | S2C_MAIL_SYSTEM_MAIL_GET_LIST_HEAD_RES | V | 4 | 12094 | 42/42 |
| 37.7.1 | C2S_MAIL_SYSTEM_MAIL_GET_LIST_DATA_REQ | V | 8 | 12096 | 42/42 |
| 37.7.2 | S2C_MAIL_SYSTEM_MAIL_GET_LIST_DATA_RES | V | var | 12407 | 42/42 |
| 37.8.1 | C2S_MAIL_SYSTEM_MAIL_GET_LIST_FOOT_REQ | V | 0 | 12099 | 42/42 |
| 37.8.2 | S2C_MAIL_SYSTEM_MAIL_GET_LIST_FOOT_RES | V | 0 | 12100 | 42/42 |
| 37.9.1 | C2S_MAIL_SYSTEM_MAIL_GET_TEXT_REQ | V | 8 | 2873 | 7/7 |
| 37.9.2 | S2C_MAIL_SYSTEM_MAIL_GET_TEXT_RES | V | var | 2905 | 7/7 |
| 37.11.1 | C2S_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_REQ | V(S3 +u8) | 9 | 2889 | 5/5 |
| 37.11.2 | S2C_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_RES | V | var | 2997 | 5/5 |
| 37.13.16 | S2C_MAIL_SYSTEM_MAIL_SEND_NTC | V (behaviour) | var | 2532 | 5/5 |
| 45.0.1 | C2S_STAMP_BONUS_GET_LIST_REQ | V | 0 | 10648 | 81/81 |
| 45.0.2 | S2C_STAMP_BONUS_GET_LIST_RES | V(S3 restructured) | var | 10649 | 81/81 |
| 45.1.1 | C2S_STAMP_BONUS_CHECK_REQ | V | 0 | 12111 | 84/84 |
| 45.1.2 | S2C_STAMP_BONUS_CHECK_RES | V(S3 list replaces u16) | var | 10426 | 84/84 |
| 45.3.1 | C2S_STAMP_BONUS_RECIEVE_DAILY_REQ | X (confirmed) | 8 | 10655 | 40/40 |
| 45.3.2 | S2C_STAMP_BONUS_RECIEVE_DAILY_RES | X (confirmed) | 0 | 10660 | 40/40 |
| 45.4.1 | C2S_STAMP_BONUS_RECIEVE_TOTAL_REQ | X (confirmed) | 0 | 10581 | 1/1 |
| 45.4.2 | S2C_STAMP_BONUS_RECIEVE_TOTAL_RES | X (confirmed) | 0 | 10586 | 1/1 |

Totals: 48 ids, 1,342 captures, header 1,342/1,342, fit 1,342/1,342. Unresolved of the triage settled:
2.5.16 (X(I)), 2.6.16 (V), 2.27/2.28/2.31/2.32.16 (V), 2.29/2.30.16 (layout V, identity I).

Recompilation (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/{C2S,S2C}.cpp`):
the only body among these ids is `CPacket_S2C_STAMP_BONUS_CHECK_RES::ReadPacket` (S2C.cpp:11561): it
agrees with PS4 and is contradicted by PC 03040008 (§ 19). `CPacket_S2C_STAMP_BONUS_GET_LIST_RES::
ReadPacket` (S2C.cpp:11603) is a `DDON_STUB`: T001's `recompiled_body yes` for 45.0.2 is overstated.
`PacketData/Mail.cpp` and `PacketData/StampBonus.cpp` hold DTI stubs only (no reader bodies).

## 22. Shared types for pattern authors

Reuse: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`), `Character.hexpat`
(`CDataCommunityCharacterBaseInfo`, `CDataCharacterListElement`, `CDataWalletPoint`,
`E_WALLET_POINT_TYPE`), `Context.hexpat` (`CDataEditInfo`, `EquipStatParam`), `Pawn.hexpat`
(`CDataCharacterJobData`, `CDataCharacterEquipData`, `CDataEquipJobItem`, `CDataOrbPageStatus`,
`CDataArisenProfile`), `Job.hexpat` (`CDataJobPlayPoint`), `Login.hexpat` (`CDataMatchingProfile`,
`CDataEquipItemInfo`), `Server.hexpat` (`CDataCharacterItemSlotInfo`), `CharacterData.hexpat`
(`CharacterBinSaveData`, 2.0.2). Framing as T003 § 18 (inline RES header; NTCs without header).

Add (V from the PC readers named; names PS4 DWARF unless marked):

| Include | Struct | PC reader | Wire |
| --- | --- | --- | --- |
| new `Mail.hexpat` | `CDataMailInfo` | `0x76e5a0` | § 1.1 |
| `Mail.hexpat` | `CDataMailAttachmentInfo`, `CDataMailItemInfo`, `CDataMailGPInfo`, `CDataMailOptionCourseInfo`, `CDataMailLegendPawnInfo`, `CDataMailAttachmentList`, `CDataMailTextInfo` | `0x76e630`, `0x76e350`, `0x76e890`, `0x76e760`, `0x76e2f0`, `0x76e9e0` | § 1.1 |
| new `Stamp.hexpat` | `CDataStampBonus` | `0x77a380` element | u32 unk_u32, u32 BonusType, u32 BonusValue (order of the two PS4 members after the new one: I) |
| `Stamp.hexpat` | `CDataStampBonusAsset` (PS4 Daily/Total element shape) | `0x77a6b0` element | MtTypedArray<CDataStampBonus> StampBonus, u16 StampNum, u8 RecieveState |
| `Stamp.hexpat` | daily group (S3) | `0x77a490` element | u32 unk_u32_0, u32 unk_u32_1, MtTypedArray<CDataStampBonusAsset> AssetList |
| `Stamp.hexpat` | check pair (S3) | `0x77a5c0` element | u32 unk_u32_0, u32 unk_u32_1 |
| `Character.hexpat` | `CDataStatusInfo` | `0x77a810` | § 1.3 item 7 |
| `Character.hexpat` | `CDataCharacterMessage`, `CDataCharacterMsgSet` | `0x75cdc0`, `0x75cee0` | § 1.3 item 21 |
| `Character.hexpat` | `CDataShortCut`, `CDataCommunicationShortCut` | `0x778a80`, `0x75ea80` | § 1.3 items 22-23 |
| `Character.hexpat` | `CDataCharacterInfo` | `0x75c2a0` | § 1.3 (needs Context/Pawn/Job/Login/Server includes: may sit in its own include to avoid cycles) |
| `Character.hexpat` | `CDataUpdateMatchingProfileInfo` | `0x77c0d0` element | u32 CharacterID, MtString Comment |
| `Character.hexpat` | `CDataCharacterReleaseElement` | `0x75d050` element | u32 ReleaseElementNo |

## 23. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`:

1. `PacketId.S2C_CHARACTER_2_5_16_NTC` comment "S2C_REWARD_BOX_LIST_NUM_NTC?": contradicted (§ 3): the
   PC handler resets a wallet-type value; PS4 REWARD_BOX_LIST_NUM drives GUI/chat.
2. Not misplacements (agree with PC 03040008 in order and widths): `CDataCharacterInfo`
   (`EmblemStatList` at item 15), `CDataStatusInfo`, `S2CCharacterDecideCharacterIdRes` (trailing
   `Unk1`), `C2SCharacterCharacterPenaltyReviveReq` (`Unk0, Unk1`; Arrowgene names neither HpMax),
   `S2CCharacterContentsReleaseElementNtc`, `S2CCharacterCommunityCharacterStatusUpdateNtc`,
   `S2CCharacterStartLanternOtherNtc`/`FinishLanternOtherNtc` (`CharacterId`),
   `S2CCharacterStartDeathPenaltyNtc` (`RemainTime`), `S2CCharacterSetOnlineStatusRes`, `CDataMailInfo`,
   the mail attachment classes, `S2CMailSystemMailGetTextRes`, `S2CMailSystemGetAllItemRes`,
   `C2SMailSystemMailGetAllItemReq` (u64 + `StorageType` u8), `S2CStampBonusGetListRes` (list
   `CDataStampBonusDaily` {Unk0, Unk1, AssetList}, `CDataStampBonusTotal` {u16 TotalStampNum,
   AssetList}), `CDataStampBonusAsset`, `CDataStampBonus` (`Unk0, BonusType, BonusValue`),
   `S2CStampBonusCheckRes` (`CDataStampCheck` list, two bytes), `C2SStampBonusRecieveDailyReq`. Note:
   Arrowgene's class names `CDataStampBonusDaily`/`Total` are its own wrappers, not the PS4 classes of
   those names (the PS4 ones are the asset shape).

## 24. Open items and checks not run

- Names without code backing (I/unk): 2.0.2 trailing u8; CharacterInfo item 15 (`unk_List`); 2.18.1
  second u32 (and which of the two is PS4's HpMax); 37.11.1 u8; the new `CDataStampBonus` u32 and its
  position; the stamp daily-group and check-pair u32s; 45.0.2 `TotalStampNum` placement; 45.1.2 u8 names
  by position.
- 2.29.16/2.30.16 identity rests on ordering (I); their layout is V.
- 2.5.16 exclusivity rests on the absence of a PS4 notice that resets a wallet type (I).
- Fit-window limits (layout from code only): 2.5.16, 2.27-2.32.16, 37.11.1 u8, 37.13.16 framing,
  45.1.2 list, 45.4.1.
- PC handlers 37.9.2, 45.0.2, 45.1.2, 45.3.2 and writer 45.4.1 lie in undefined code; read by linear
  decoding only.
- ImHex not run (not on `PATH`); no pattern written (outside this package).
