# 008 T005: batches B3, B7 and B6, patterns, JSON and names (client 03040008)

Date 2026-11-03, base `024203f2e9`. Scope: the 45 ids of batches B3 (group 62 dungeon info / blockade / EX items /
area buffs, group 12 unison recruitment and dungeon start), B7 (50.0.16, 27.10, 41.5, 41.8, 65.3, 2.5.16, 29.23.16,
34.0, 10.14.16) and B6 (group 63, 13.16, 13.17, 13.23.16) of `T001-triage.tsv` (579 raw files). All VAs are PC
03040008 (image base `0x400000`). Marks per `spec.md`: V = read in the PC code, I (basis) = inferred, G (basis) =
guess, `open` = kept `unk_*` with its leads in the comment. Pattern comments read `// T005 <mark>: <basis>`.

## 1. Answer

- **45 patterns** in `research/03040008/packets/`, one per id; **579/579** raw files exported and fit (`fits` and
  `sourceOk` true, no `.json.err`). Every layout is the PC reader/writer sequence read in IDA for this task (types
  from the reader's own calls: `Read_bool`, `Read_u64`, `Write_cstr`, ...), except 29.23.16, whose handler
  `0x7d5730` is `return 1` (body ignored, V): its pattern is the capture shape (u32, list of 18-byte elements), marks G.
- **One T001 correction**: 34.0.1's writer `0x77dff0` writes a u32 count then one `Write_u64` per element: the body
  is `MtTypedArray<CDataCommonU64>` (T001 read `{4 8}` plain; the server's `L[8]` was right).
- **Includes**: new `ChainDungeon.hexpat` (group 63: `CDataChainDungeonLayoutInfo` PC `0x762c50`,
  `CDataSituationObjective` `0x762b40`); additions to `SeasonDungeon.hexpat` (buff effect `0x779540`, its param
  `0x778e70`, buff level `0x778fa0`, dungeon info `0x777b00`, section `0x777e80` with `0x777c40`, blockade element
  `0x777b50`, `CDataSoulOrdealItem` `0x777c80`) and `Packet.hexpat` (`CDataCommonU64`, PS4 DWARF name). No existing
  field changed. Reused: `Item.hexpat` `CDataItemSort` (same reader `0x75e6e0`), `Achievement.hexpat`
  `CDataAchievementProgress` (`0x758810`), `Character.hexpat` `CDataWalletPoint` (`0x77c5a0`), `Context.hexpat`
  `CDataEditInfo` (writer `0x77eb40`), `Quest.hexpat` `CDataItemUIDList` (writer `0x77fd30`), `Instance.hexpat`
  `CDataStageLayoutId`, `CDataOmData` and `GatheringItemListRes_unk_1` (reader `0x7731b0`), `Packet.hexpat`
  `CDataCommonU8`.
- **Names**: value correlation (§ 4) upgrades 42 fields to I (28 in the pattern files, 14 in the includes), among them the season dungeon buffs against
  `contents_buff_info.abl` (BuffId = AbilityId, ParamType 85/85). Server names alone stay G (lead); server `Unk*`
  stay `unk_*` (open) with the lead in the comment.
- **Two packets renamed** (raws and JSON keep the CLI name; the export selects by `// packet-id:`): 62.39.16
  `S2C_SEASON_62_39_16_NTC` -> `S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC` (G (context; value): a CharacterId plus
  the (BuffId, Level) pairs of the 62.38.16 area buffs sent within 3 packets, 148/148); 63.2.16 `S2C_63_2_16_NTC`
  -> `S2C_SITUATION_DATA_UPDATE_OBJECTIVES_NTC` (G (lead: server class S2CSituationDataUpdateObjectivesNtc; context:
  objective texts)).
- **Independent check**: `t005/walk.py` (stdlib; T003's decoder loaded by path, plus fixed arrays) decodes all 579
  raws (579 fit); `check` compares 75 samples (smallest and largest raw per id; 1 for single-capture ids) leaf by
  leaf with the JSON: 75/75 match, 6,642 leaves (§ 6).

## 2. Sources and method

- Layouts: `T001-triage.tsv`, T002 for the `0x77fd30` writers (62.10.1, 12.5.1).
- IDA: one headless read-only batch (`t003/run.sh` -> `t003/read_funcs.py`, `DBFL_KILL`, `qexit`) on a `cp` of the
  wave-2 database `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64` (sha256
  `ee07f0b6…8c1d`) in `ddon-data-t005w/`: every handler, sender and reader VA of the 45 ids (96 functions plus
  `0x762b40`, `0x77fd30`; `0x7d1be0` is no function in the dump, its reader `0x806610` was read).
- Values: `t005/walk.py stats` and `t005/correlate.py`; client data `client/03040008/base/etc/itemlist.ipa.json`,
  `base/scr/stage_list.slt.json` (StageId), `contents_buff/obj/pl/pl000000/param/etc/contents_buff_info.abl.json`.
- Leads: Arrowgene fork `Entity/{PacketStructure,Structure}/*.cs` (local clone), the upstream names via T001 § 2.

## 3. Per id

| id | pattern | layout (body, PC) | names and marks | fit |
| --- | --- | --- | --- | ---: |
| 62.38.16 | `S2C_SEASON_DUNGEON_AREA_BUFFS_NTC` | `0x819510`: list `0x778e70` {u32, `0x779540` {u32, MtString, u32 x5}} (V) | Level, BuffId, BuffName, ParamType I; MaxLv G (value); 3 open | 148/148 |
| 62.39.16 | `S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC` (renamed) | `0x819570`: u32, list `0x778fa0` {u32, u32} (V) | CharacterId, BuffId, Level I | 148/148 |
| 62.0.1 | `C2S_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_REQ` | `0x83b3b0`: u32 (V) | NpcId G (lead) | 4/4 |
| 62.0.2 | `S2C_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_RES` | `0x819c00`: header, u32 (V) | DungeonId I | 4/4 |
| 62.1.1 | `C2S_SEASON_DUNGEON_GET_INFO_REQ` | `0x83b490`: u32 (V) | DungeonId I | 4/4 |
| 62.1.2 | `S2C_SEASON_DUNGEON_GET_INFO_RES` | `0x819c80`: header, `0x777b00` {u32, MtString, u32}, list `0x777e80` {u32 x4, {u32, u32}, bool, MtString}, u8 (V) | DungeonId (server's first `Unk0`), Name, section StageId, SectionName I; 7 open | 4/4 |
| 62.7.1 | `C2S_SEASON_DUNGEON_GET_EXTENDABLE_BLOCKADE_LIST_FROM_NPC_ID_REQ` | `0x83b110`: u32 (V) | NpcId G (lead) | 4/4 |
| 62.7.2 | `S2C_SEASON_DUNGEON_GET_EXTENDABLE_BLOCKADE_LIST_FROM_NPC_ID_RES` | `0x819a50`: header, list `0x777b50` {u32, MtString} (V) | G (lead); empty 4/4 | 4/4 |
| 62.8.1 | `C2S_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_REQ` | `0x842150`: layout id, u32 (V) | LayoutId I; PosId G | 7/7 |
| 62.8.2 | `S2C_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_RES` | `0x8199d0`: header, u32 (V) | EpitaphId I | 7/7 |
| 62.9.1 | `C2S_SEASON_DUNGEON_GET_EX_REQUIRED_ITEM_REQ` | `0x83b2d0`: u32 (V) | EpitaphId I | 7/7 |
| 62.9.2 | `S2C_SEASON_DUNGEON_GET_EX_REQUIRED_ITEM_RES` | `0x819b60`: header, bool, bool, list `0x777c80` {u32, u16} (V) | ItemId, Num I; 2 open | 7/7 |
| 62.10.1 | `C2S_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_REQ` | `0x83aca0`: u32, list `0x77fd30` {MtString, u32}, bool (V) | EpitaphId, ItemList I; 1 open | 6/6 |
| 62.10.2 | `S2C_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_RES` | `0x819670`: header (V) | - | 12/12 |
| 62.27.16 | `S2C_SEASON_62_27_16_NTC` | `0x7f8a70`: u32 (V; announce parameter of message 0x250) | open | 1/1 |
| 12.5.1 | `C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ` | `0x842930`: u32, list `0x77fd30`, u32, cstr (V) | ContentId, SectionName I; EntranceId G | 3/3 |
| 12.5.2 | `S2C_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_RES` | `0x81ce40`: header (V) | - | 3/3 |
| 12.9.16 | `S2C_STAGE_DUNGEON_START_NTC` | `0x81d070`: `0x779a90` {u32, MtString, u32, u32, bool, list `0x779b10` {u32, u16}} (V) | ContentId, StageId I; StartPos G; 4 open | 3/3 |
| 50.0.16 | `S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC` | `0x7ddab0`: `Read_CDataItemSort_` `0x75e6e0` (V) | I (same structure as 50.0.2) | 48/48 |
| 27.10.1 | `C2S_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_REQ` | `0x81dc90`: u8 (V) | Category G (lead) | 19/19 |
| 27.10.2 | `S2C_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES` | `0x7ff650`: header, `0x758810` (V) | V (same reader as 27.0.2) | 19/19 |
| 41.8.1 | `C2S_CHARACTER_EDIT_GET_SHOP_PRICE_REQ` | `0x821440`: none (V) | - | 4/4 |
| 41.8.2 | `S2C_CHARACTER_EDIT_GET_SHOP_PRICE_RES` | `0x802130`: header, list `0x764d70` {u8, list `0x77c5a0`} (V) | UpdateType G; PriceList V (CDataWalletPoint) | 4/4 |
| 41.5.1 | `C2S_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_REQ` | `0x8406b0`: u8, {u8, u32}, `Write_CDataEditInfo_`, MtString (V) | EditPrice I; EditInfo V; UpdateType, FirstName G | 1/1 |
| 41.5.2 | `S2C_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_RES` | `0x8022d0`: header (V) | - | 1/1 |
| 2.5.16 | `S2C_CHARACTER_2_5_16_NTC` | `0x7c7770`: u8 (V; argument of sItemManager `0xb9f450`) | open | 2/2 |
| 29.23.16 | `S2C_EQUIP_29_23_16_NTC` | none: handler `0x7d5730` ignores the body (V); capture shape u32, list {u32 x3, u8, u32, u8} | G (capture shape) | 2/2 |
| 65.3.1 | `C2S_EQUIP_ENHANCED_GET_PACKS_REQ` | `0x827e40`: u8 (V) | EnhanceType G | 2/2 |
| 65.3.2 | `S2C_EQUIP_ENHANCED_GET_PACKS_RES` | `0x807e10`: header, list `0x765d90` (tree in the pattern) (V) | RowTitle I; three lists V (same readers); Index, Category, lists G; 9 open | 2/2 |
| 10.14.16 | `S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC` | `0x80cca0`: u16, list `0x76cc70` {u8, u32} (V) | ItemId I; 2 open | 1/1 |
| 34.0.1 | `C2S_ENTRY_BOARD_ENTRY_BOARD_LIST_REQ` | `0x827580`: list `0x77dff0` {u64} (V; T001 corrected) | BoardIdList V/I | 1/1 |
| 34.0.2 | `S2C_ENTRY_BOARD_ENTRY_BOARD_LIST_RES` | `0x8075a0`: header, list `0x7652c0` {u64, u16 x5, bool, u32} (V) | BoardId I; SortieMin, NoPartyMembers, TimeOut G; 4 open | 1/1 |
| 13.23.16 | `S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC` | `0x80af70`: u32, u64, u32, u32 (V) | StageId, Value, ValueOld I (same structure: 13.23.2) | 46/46 |
| 13.16.1 | `C2S_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_REQ` | `0x82c70d`: u32 (V) | open | 1/1 |
| 13.16.2 | `S2C_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES` | `0x80bdc0`: header, list `0x77b470` {u32, MtString, u8} (V) | CategoryId, CategoryName, EntryCount I | 1/1 |
| 13.17.1 | `C2S_INSTANCE_TREASURE_POINT_GET_LIST_REQ` | `0x82c7f0`: u32 (V) | CategoryId I | 1/1 |
| 13.17.2 | `S2C_INSTANCE_TREASURE_POINT_GET_LIST_RES` | `0x80bed0`: header, u32, list `0x77b580` {u32, MtString, bool} (V) | CategoryId, Index, Name I; 1 open | 1/1 |
| 63.0.16 | `S2C_63_0_16_NTC` | `0x7d1ae0`: u32 (V; value unused) | open | 1/1 |
| 63.1.16 | `S2C_63_1_16_NTC` | `0x7d1b80`: u32 (V; read and dropped) | open | 1/1 |
| 63.2.16 | `S2C_SITUATION_DATA_UPDATE_OBJECTIVES_NTC` (renamed) | `0x806610`: bool, u8, u32 x4, list `0x762b40` {u8, u32, MtString} (V) | Message I; 8 open | 21/21 |
| 63.3.16 | `S2C_63_3_16_NTC` | `0x7d1f50`: none (V) | - | 1/1 |
| 63.5.16 | `C2S_CHAIN_DUNGEON_END_CHAIN_NTC` | `0x826330` `Send_S2C_63_5_16_NTC`: none (V) | - | 1/1 |
| 63.6.16 | `S2C_CHAIN_DUNGEON_REWARD_CHEST_APPEAR_NTC` | `0x7d2150`: list `0x762c50` {u32, u8, u32, u32} (V) | LayoutId I; 1 open | 1/1 |
| 63.7.16 | `S2C_63_7_16_NTC` | `0x7d2000`: list `0x762c50` (V) | as 63.6.16 | 8/8 |
| 63.10.16 | `S2C_63_10_16_NTC` | `0x8066b0`: u32, MtString, u8 (V) | 3 open | 12/12 |

Total 579/579.

## 4. Value correlation (`t005/correlate.py`)

| check | result | used for |
| --- | --- | --- |
| 62.38.16 BuffId is an AbilityId of `contents_buff_info.abl`; the last u32 = that ability's ParamType (203-209) | 85/85; 85/85 | `BuffId`, `ParamType` I |
| 62.38.16 third u32 = the ability's level count | 85/85, but one value (4) only | `MaxLv` G (value) |
| 62.38.16 Level = the "Lv. n" suffix of BuffName | 85/85 | `Level` I |
| 62.39.16 (BuffId, Level) list = the 62.38.16 list sent within 3 packets of the stream | 148/148 | 62.39.16 names I, packet name G |
| 62.39.16 u32 is a CharacterId field in another JSON of the stream | 41/41 (stream, id) pairs | `CharacterId` I |
| 62.9.1 / 62.10.1 EpitaphId = the preceding 62.8.2 | 7/7, 6/6 | `EpitaphId` I |
| 62.10.1 sum of Num = the preceding 62.9.2 required Num (240) | 6/6 | ItemList, 62.9.2 `Num` I |
| item ids in `itemlist.ipa.json` | 62.9.2 7/7, 65.3.2 38/38, 10.14.16 1/1 | `ItemId` I |
| 62.1.1 = 62.0.2 DungeonId; 62.1.2 first u32 = the 62.1.1 DungeonId | 4/4; 4/4 | `DungeonId` I (server names the third u32 DungeonId: contradicted) |
| StageIds in `stage_list.slt.json` | 62.8.1 560 7/7, 62.1.2 sections 550 16/16, 12.9.16 559 3/3, 13.23.16 46/46, 63.x 655 9/9 | StageId/LayoutId I |
| 62.1.2 Name "メガドシスの記憶" = stage_list name of StageId 559 | 4/4 | `Name` I |
| 12.5.1 string is a 62.1.2 SectionName; 12.9.16 ContentId = 12.5.1 ContentId | 3/3; 3/3 | `SectionName`, `ContentId` I |
| 34.0.2 BoardId = the 34.0.1 id | 1/1 | `BoardId`, `BoardIdList` I |
| 41.5.1 EditPrice (5, 20) = the UpdateType 2 price of the preceding 41.8.2 | 1/1 | `EditPrice` I |
| 13.17.1 CategoryId in the 13.16.2 list; 13.17.2 count = the category's u8; Name ends in 《Index + 1》 | 1/1; 1/1; 5/5 | CategoryId, EntryCount, Index I |
| 13.23.16 ValueOld = the Value the previous 13.23.16 set for (StageId, Key) | 25/35 (others follow a 13.20/13.23.2 change) | `ValueOld` I (with the 13.23.2 structure) |

## 5. Open and not run

- Field consumers were not traced (budget): the G names (server leads) and the open fields of 62.1.2 sections, 63.x,
  65.3.2 and 34.0.2 would need a consumer pass. 62.27.16's announce message 0x250 was not resolved to a text.
- Code-only (never captured non-empty): 62.7.2 BlockadeList, 12.5.1 EntryFeeList, 12.9.16 EntryCostList, 65.3.2's
  wallet lists and second item list.
- 29.23.16 has no reader: its layout is the capture shape (two identical bodies of one stream).
- Single-capture ids (15) cannot be cross-checked across sessions.
- `GatheringItemListRes_unk_1` (Instance.hexpat, reader `0x7731b0`) keeps `unk_u32`/`unk_u16`; in 65.3.2 the u32 is
  an itemlist ItemId 38/38. Renaming the include fields is a change to an existing include: not done (proposal).
- ImHex GUI validation: not run (plbatch export only).

## 6. Verification

- `python -X utf8 -I specs/008-remaining-packets/research/t005/walk.py fits`: 45 ids, 579/579 JSON with `fits` and
  `sourceOk` true, 0 `.json.err` ("fits: 0 id(s) with a missing, unfit or failed file").
- `python -X utf8 -I specs/008-remaining-packets/research/t005/walk.py check`: 75/75 samples match (30 ids x 2
  files, 15 single-capture ids x 1), 6,642 leaves compared, slack equal ("check: 0 sample(s) differ").
- Export: `packets/imhex-export.sh --force @ <name> </dev/null` per pattern: 45 runs, 579 exported, 0 skipped, 0
  failed, 0 nonfinite, 0 badjson.

## 7. For Sam's inspection

- New JSON: 579 files under `packets/decrypted_json/` for the 45 ids (per-id counts in § 3; 45 new patterns, 1 new
  include, 2 extended).
- Renamed packets: 62.39.16 pattern `S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC` (raw `S2C_SEASON_62_39_16_NTC`);
  63.2.16 pattern `S2C_SITUATION_DATA_UPDATE_OBJECTIVES_NTC` (raw `S2C_63_2_16_NTC`).
- Server names replaced: 62.1.2 `CDataSeasonDungeonInfo` `Unk0` -> `DungeonId` and the server's `DungeonId` -> `unk_u32`
  (values: the first u32 echoes the requested DungeonId 4/4, the third is 40); `CDataSeasonDungeonUnk2` `Label` ->
  `BuffName`, `Unk2` -> `MaxLv` (G), `Unk6` -> `ParamType` (I); section `Unk1` -> `StageId` (I); section `Unk4`
  ({BuffId, Level} in the server) kept unk (values 3 with 7/15/23 are no buff levels); 12.5.1 `Unk2String` ->
  `SectionName`; 12.9.16 `Unk0` -> `ContentId`; 62.39.16 struct `CDataSeasonDungeonUnk0` -> `CDataSeasonDungeonBuffLevel`;
  41.8.2 `Prices` -> `PriceList`, `PriceInfo` -> `PriceInfoList`; 62.1.2 `DungeonSections` -> `SectionList`; 13.16.2
  `TreasurePointCategories` -> `CategoryList`; 65.3.2 `ShopTypeListings` -> `ShopTypeList`; 63.x
  `CDataS2C_63_7_16`/upstream `CDataStageLayoutInfo` -> `CDataChainDungeonLayoutInfo`, `Unk0List` -> `LayoutInfoList`.

## 8. Files

- `research/03040008/packets/*-pattern.cpp`: the 45 patterns (§ 3); `include/ChainDungeon.hexpat` (new),
  `include/SeasonDungeon.hexpat` and `include/Packet.hexpat` (additions); `README.md`: include rows, 45 table rows
  and the T005 paragraph.
- `specs/008-remaining-packets/research/t005/walk.py` (`stats`, `check`, `fits`, `dump`), `correlate.py`.

## Errata (T006, 2026-11-03)

Applied by 008 T007 (`specs/008-remaining-packets/briefs/T007-mark-fixes.md`) from the adversarial review `T006-adversarial.md` F1-F3; the text above is unchanged. Counts above are values in captures; this table gives the distinct values behind every `I (value)` mark of this task and the mark after T007 (rule: README "How value bases are counted"). `chance`: probability that every distinct value is an id of the item or stage table by luck (id claims only). Source: `t007/marks-before.tsv`, `t007/mark-changes.tsv`.

- 62.39.16: "148/148" includes 121 empty lists; 27 are non-empty, 21 distinct lists, 3 CharacterIds.
- 10.14.16 ItemId is now V (consumer); the "I 1" of the § 3 row reads "V".
- `Instance.hexpat` `GatheringItemListRes_unk_1` (§ 5 proposal): `unk_u32` -> `ItemId`, `unk_u16` -> `Num`, both G (lead; value consistent: 19 distinct, chance 0.21 / 1 distinct).
- The README table rows count the marks after T007; the tables above keep the marks before it.

| id | field | values | distinct | chance | mark after T007 |
| --- | --- | ---: | ---: | ---: | --- |
| 10.14.16 | `CDataItemAchievementReward.ItemId` | 1 | 1 | 1 | V (consumer): handler `0x7de260` passes element +8 to the sItemManager lookup `0xb98c80` and posts chat message 0x85 (T006 F1) |
| 12.5.1 | `C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ.ContentId` | 3 | 1 |  | G (lead) (was I) |
| 12.5.1 | `C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ.SectionName` | 3 | 1 |  | G (lead) (was I) |
| 12.9.16 | `CDataStageDungeonStart.ContentId` | 3 | 1 |  | G (lead) (was I) |
| 12.9.16 | `CDataStageDungeonStart.StageId` | 3 | 1 | 1 | I |
| 13.16.2 | `CDataTreasurePointCategory.CategoryId` | 4 | 4 |  | I |
| 13.16.2 | `CDataTreasurePointCategory.CategoryName` | 4 | 4 |  | I |
| 13.16.2 | `CDataTreasurePointCategory.EntryCount` | 4 | 2 |  | G (lead) (was I) |
| 13.17.1 | `C2S_INSTANCE_TREASURE_POINT_GET_LIST_REQ.CategoryId` | 1 | 1 |  | G (lead) (was I) |
| 13.17.2 | `CDataTreasurePoint.Index` | 5 | 5 |  | I |
| 13.17.2 | `CDataTreasurePoint.Name` | 5 | 5 |  | I |
| 13.17.2 | `S2C_INSTANCE_TREASURE_POINT_GET_LIST_RES.CategoryId` | 1 | 1 |  | G (lead) (was I) |
| 13.23.16 | `S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC.StageId` | 46 | 5 | 0.28 | I |
| 13.23.16 | `S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC.ValueOld` | 46 | 25 | 2.1e-77 | I |
| 34.0.2 | `CDataEntryBoardListParam.BoardId` | 1 | 1 |  | G (lead) (was I) |
| 41.5.1 | `C2S_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_REQ.EditPrice` | 1 | 1 |  | I |
| 62.0.2 | `S2C_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_RES.DungeonId` | 4 | 1 |  | G (lead) (was I) |
| 62.1.1 | `C2S_SEASON_DUNGEON_GET_INFO_REQ.DungeonId` | 4 | 1 |  | G (lead) (was I) |
| 62.1.2 | `CDataSeasonDungeonInfo.DungeonId` | 4 | 1 |  | G (lead) (was I) |
| 62.1.2 | `CDataSeasonDungeonInfo.Name` | 4 | 1 |  | I |
| 62.1.2 | `CDataSeasonDungeonSection.SectionName` | 16 | 4 |  | I |
| 62.1.2 | `CDataSeasonDungeonSection.StageId` | 16 | 1 | 1 | G (lead) (was I) |
| 62.10.1 | `C2S_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_REQ.EpitaphId` | 6 | 6 |  | I |
| 62.10.1 | `C2S_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_REQ.ItemList` | 19 | 19 |  | I |
| 62.38.16 | `CDataSeasonDungeonBuffEffect.BuffId` | 85 | 5 |  | I |
| 62.38.16 | `CDataSeasonDungeonBuffEffect.BuffName` | 85 | 11 |  | I |
| 62.38.16 | `CDataSeasonDungeonBuffEffect.ParamType` | 85 | 5 |  | I |
| 62.38.16 | `CDataSeasonDungeonBuffEffectParam.Level` | 85 | 3 |  | G (lead) (was I) |
| 62.39.16 | `CDataSeasonDungeonBuffLevel.BuffId` | 85 | 5 |  | I |
| 62.39.16 | `CDataSeasonDungeonBuffLevel.Level` | 85 | 3 |  | G (lead) (was I) |
| 62.39.16 | `S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC.CharacterId` | 148 | 3 |  | G (lead) (was I) |
| 62.8.1 | `C2S_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_REQ.LayoutId` | 7 | 6 | 1 | I |
| 62.8.2 | `S2C_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_RES.EpitaphId` | 7 | 6 |  | I |
| 62.9.1 | `C2S_SEASON_DUNGEON_GET_EX_REQUIRED_ITEM_REQ.EpitaphId` | 7 | 6 |  | I |
| 62.9.2 | `CDataSoulOrdealItem.ItemId` | 7 | 1 | 1 | G (lead) (was I) |
| 62.9.2 | `CDataSoulOrdealItem.Num` | 7 | 1 |  | G (lead) (was I) |
| 63.2.16 | `CDataSituationObjective.Message` | 84 | 6 |  | I |
| 63.6.16,63.7.16 | `CDataChainDungeonLayoutInfo.LayoutId` | 9 | 2 | 1 | I |
| 65.3.2 | `CDataEquipEnhanceLotteryOption.RowTitle` | 38 | 19 |  | I |
