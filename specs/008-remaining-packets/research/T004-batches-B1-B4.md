# 008 T004: batches B1 and B4, patterns, JSON and names (client 03040008)

Date 2026-11-03, base `0695c20044`. Scope: the 37 ids of batches B1 (group 62 SEASON_DUNGEON, soul ordeal) and B4
(groups 71 BATTLE_CONTENT, 72 DAILY_MISSION, 59 INFINITY_DELIVERY) in `T001-triage.tsv` (1,631 raw files). All VAs are
PC 03040008 (image base `0x400000`). Marks per `spec.md`: V = read in the PC code, I (basis) = inferred, G (basis) =
guess, `open` = kept `unk_*` with its leads in the comment. Pattern comments read `// T004 <mark>: <basis>`.

## 1. Answer

- **37 patterns** in `research/03040008/packets/`, one per id; **1,631/1,631** raw files exported and fit (`fits` and
  `sourceOk` true, no `.json.err`). Every layout is the PC reader/writer width sequence (V); types (u8/bool, u64/s64)
  are the reader's own calls (`Read_bool`, `Read_s64`, ...), read in this task.
- **One T001 correction**: 72.2.1's list writer `0x77df90` writes the count and one `u32` per element (element +4);
  T001's `77df90{4 4} 1` counted the count as a field. The body is `list CDataCommonU32, u8` (V; § 3).
- **Three new includes** (no existing include changed): `SeasonDungeon.hexpat` (`CDataSeasonDungeonOmState` PC
  `0x766790`, `CDataSoulOrdealObjective` `0x779090`, `CDataSoulOrdealRewardItem` `0x769240`/`0x77f9d0`),
  `DailyMission.hexpat` (the mission element `0x762530`, its reward `0x762640` and the two element lists, the course
  list `0x7626e0`/`0x7627f0`), `InfinityDelivery.hexpat` (event `0x769fe0`, ranking element `0x76a850`, category
  status `0x769de0`). Reused: `Instance.hexpat` `CDataStageLayoutId` and `CDataGatheringItemElement` (PC
  `0x769100`), `Mail.hexpat` `CDataMailAttachmentList` (PC `0x76e2f0`, inside the daily mission reward) and
  `CDataMailOptionCourseInfo` (vtable `0x1b2662c`, inside the `0x7627f0` element), `Packet.hexpat` `CDataCommonU32`.
- **Names**: B1 and 71.22 follow the server structures, whose order and widths the PC readers confirm; value
  correlation upgrades those it can check to I (§ 4); the rest stay G (lead) or `open`. Groups 72 and 59 have no server structure: every name comes from
  value correlation (I) or the UI texts and context (G); § 4 lists the bases.
- **One packet renamed**: 72.1.16 `S2C_DAILY_72_1_16_NTC` -> pattern `S2C_DAILY_MISSION_ACHIEVE_NTC` (G (context; value):
  the 1-4 mission ids it lists go from State 1 to State 2 in the surrounding 72.0.2 lists, 113/113; no `OnPacket_`
  string). Raws and JSON keep the CLI name (the export selects by `// packet-id:`).
- **Independent check**: `t004/walk.py` (stdlib; T003's decoder loaded by path with the B1/B4 layouts) decodes all
  1,631 raws (1,631 fit), and `check` compares a stratified sample (smallest and largest raw per id; 1 file for the
  single-capture ids) leaf by leaf with the exported JSON: 68/68 match (§ 6).

## 2. Sources and method

- Layouts: `T001-triage.tsv` (`pc_va`, `readers`, `width_seq`), T002 for the 62.24.1/62.34.1 list writers.
- IDA: two headless read-only batches (`t003/run.sh` -> `t003/read_funcs.py`, `DBFL_KILL`, `qexit`) on a `cp` of the
  wave-2 database `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64` (sha256
  `ee07f0b6…8c1d`) in `ddon-data-t004w/`. Read: handlers `0x7d1950 0x7d18b0 0x7d1760 0x7d1a50 0x7d9d00 0x7d9c20
  0x7d9ac0 0x7d99e0 0x7f8970 0x7f8c60 0x7f8350 0x7f8630 0x7f88d0 0x7f7a50 0x7f7bb0 0x7f8740`, senders `0x8260c0
  0x826180 0x825fe0 0x82ac10 0x82ab30 0x82a960 0x82a880 0x842320 0x83be90 0x8421c0 0x842510 0x8420e0 0x8423b0
  0x842430 0x77df90 0x781020`, readers `0x8064e0 0x806440 0x806580 0x762460 0x762530 0x762640 0x762960 0x762a50
  0x7626e0 0x7627f0 0x76e2f0 0x76e630 0x76e350 0x76e890 0x76e760 0x80a470 0x80a3f0 0x80a2b0 0x80a230 0x769ed0 0x769fe0
  0x769de0 0x76a760 0x76a850 0x76a060 0x76a170 0x769bc0 0x769b10 0x76a8d0 0x76a390 0x76a620 0x7699f0 0x8006f0
  0x759910 0x759ac0 0x759990 0x75bdc0 0x75beb0 0x75bf90 0x819d20 0x7791d0 0x779330 0x779870 0x7796e0 0x7797d0
  0x81a530 0x779090 0x81a2c0 0x81a3c0 0x766790 0x81a4d0 0x819e70 0x779420 0x81a240 0x769240`, and the daily mission
  consumers `0x580b90 0x580f90 0x581230` (they copy the packet lists into the mission manager; no field names).
- Values: `t004/walk.py stats` (histogram of every leaf) and `t004/correlate.py` (§ 4); client data
  `client/03040008/base/etc/itemlist.ipa.json` (item ids), `ui/uGUIDailyMission/ui/00_message/**.gmd.json` (UI texts,
  purpose texts), `infinity_delivery/ui/00_message/ui/infinity_delivery.gmd.json`.
- Leads: Arrowgene `Arrowgene.Ddon.Shared/Entity/{PacketStructure,Structure}/*.cs`, `Model/WalletType.cs`,
  `Model/Storages.cs` (local clone).

## 3. Per id

| id | pattern | layout (body, PC) | names and marks | fit |
| --- | --- | --- | --- | ---: |
| 62.26.16 | `S2C_SEASON_DUNGEON_SET_OM_STATE_NTC` | handler `0x7f8970`: `0x766790` {u32, u8, u32, u32, u8} (V) | `OmState` = `CDataSeasonDungeonOmState`: LayoutId I (same structure; value), PosId, State G (lead) | 428/428 |
| 62.12.16 | `C2S_SEASON_DUNGEON_62_12_16_NTC` | writer `0x842510`: layout id, u32 (V) | LayoutId I, PosId G (lead); purpose open | 259/259 |
| 62.18.1 | `C2S_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_REQ` | writer `0x8421c0`: layout id, u32 (V) | as 62.12.16 | 61/61 |
| 62.18.2 | `S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_RES` | `0x819d20`: header, u8, list `0x7791d0` {u32, MtString, list {u32, u16}, list {u32, list `0x7797d0` {u32 x3, u8, u8, bool x3}}}, bool, u8, bool, u8 (V) | TrialId, TrialName, cost ItemId, reward ItemId I (value); Type, list names G (lead); reward Num G (context); 11 open | 61/61 |
| 62.16.16 | `S2C_SEASON_DUNGEON_UPDATE_SOUL_ORDEAL_OBJECTIVES_NTC` | `0x81a530`: list `0x779090` {u8, u8, u32, u32, MtString} (V) | Type, Priority, ObjectiveLabel I (value); Param1/2 G (lead) | 53/53 |
| 62.14.16 | `S2C_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_NTC` | `0x81a2c0`: MtString, u32, list `0x779090` (V) | TrialName, TrialId I (value) | 28/28 |
| 62.15.16 | `S2C_SEASON_DUNGEON_END_SOUL_ORDEAL_NTC` | `0x81a3c0`: u8, `0x766790`, u32 (V) | EndState G (lead; 1 success with OmState.State 5 21/21, 2 with an all-zero OmState 7/7); `TrialId` I (value 28/28; server Unk3) | 28/28 |
| 62.20.1 | `C2S_SEASON_DUNGEON_SOUL_ORDEAL_READY_REQ` | `0x83be90`: u32, layout id, u32 (V) | TrialId I (value 28/28) | 28/28 |
| 62.20.2 | `S2C_SEASON_DUNGEON_SOUL_ORDEAL_READY_RES` | `0x81a440`: header (V) | - | 28/28 |
| 62.22.16 | `S2C_SEASON_62_22_16_NTC` | handler `0x7f8740` reads nothing (V) | - (meaning open) | 28/28 |
| 62.23.16 | `S2C_SEASON_DUNGEON_GROUP_READY_NTC` | `0x81a4d0`: bool (V) | Ready G (lead) | 28/28 |
| 62.24.1 | `C2S_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_REQ` | `0x8420e0`: u32, list `0x77fd30` {MtString, u32}, `0x781020` {u32, u8, u32}, u32 (V, T002) | TrialId I (value 28/28); TrialCost G (lead; empty 28/28) | 28/28 |
| 62.24.2 | `S2C_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_RES` | `0x819820`: header (V) | - | 28/28 |
| 62.33.1 | `C2S_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_REQ` | writer `0x8422b0`: layout id, u32 (V) | as 62.12.16 | 21/21 |
| 62.33.2 | `S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES` | `0x819e70`: header, list `0x769100`, list `0x779420` {u32, u32, MtString, u32} (V) | ItemRewards I (same structure; value); BuffId, BuffName, Level I (value); BuffEffect G (lead) | 21/21 |
| 62.34.1 | `C2S_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_REQ` | `0x8423b0`: layout id, u32, list `0x77f9d0` {u32, u32} (V, T002) | RewardIndex, Amount I (value 52/52) | 21/21 |
| 62.34.2 | `S2C_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_RES` | `0x81a240`: header, list `0x769240` {u32, u32} (V) | as 62.34.1 (Amount 0) | 21/21 |
| 62.35.1 | `C2S_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_BUFF_REQ` | `0x842320`: layout id, u32, u32, u32 (V) | BuffId I (value 21/21); `unk_u32` open (0) | 21/21 |
| 62.35.2 | `S2C_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_BUFF_RES` | `0x81a1b0`: header (V) | - | 21/21 |
| 62.40.16 | `C2S_SEASON_62_40_16_NTC` | writer `0x842430`: layout id, u32 (V) | as 62.12.16; purpose open | 3/3 |
| 71.22.1 | `C2S_BATTLE_CONTENT_INFO_LIST_REQ` | `0x81f040`: none (V) | - | 42/42 |
| 71.22.2 | `S2C_BATTLE_CONTENT_INFO_LIST_RES` | `0x8006f0` (V; tree in the pattern) | stage/progression/reward Ids, GameMode, ContentName, StageName, the two item lists I (value); Tier, Mode, situation fields G (lead); 5 open | 42/42 |
| 72.0.1 | `C2S_DAILY_MISSION_LIST_GET_REQ` | `0x8260c0`: none (V) | - | 117/117 |
| 72.0.2 | `S2C_DAILY_MISSION_LIST_GET_RES` | `0x8064e0`: header, list `0x762460` x2, list `0x7626e0` (V) | `CDataDailyMission`: MissionId, Purpose, TargetNum, Text, IconUrl, ImageUrl, Progress, State, StartDate, EndDate I (value); SortNo G; reward MissionId, ItemId I, wallet Type I; lists `MissionList`, `SpecialRewardList` G (context) | 117/117 |
| 72.1.16 | `S2C_DAILY_MISSION_ACHIEVE_NTC` (raw `S2C_DAILY_72_1_16_NTC`) | `0x7d1760`: list `0x75e8e0` (V) | `MissionIdList` I (value 113/113) | 64/64 |
| 72.2.1 | `C2S_DAILY_MISSION_REWARD_RECEIVE_REQ` | `0x826180`: list `0x77df90` {u32}, u8 (V; T001 corrected) | `MissionIdList` I (value 8/8); `StorageType` I (value 8/8) | 8/8 |
| 72.2.2 | `S2C_DAILY_MISSION_REWARD_RECEIVE_RES` | `0x806580`: header (V) | - | 8/8 |
| 72.3.1 | `C2S_DAILY_MISSION_EVENT_LIST_GET_REQ` | `0x825fe0`: u8 (V) | `unk_u8` open (7; echoed) | 4/4 |
| 72.3.2 | `S2C_DAILY_MISSION_EVENT_LIST_GET_RES` | `0x806440`: header, u8, list `0x762460`, list `0x7626e0` (V) | `EventMissionList` G (context); `unk_u8` open (echo 4/4) | 4/4 |
| 59.0.1 | `C2S_INFINITY_DELIVERY_GET_CURRENT_EVENT_REQ` | `0x82ac10`: none (V) | - | 2/2 |
| 59.0.2 | `S2C_INFINITY_DELIVERY_GET_CURRENT_EVENT_RES` | `0x80a470`: header, list `0x769fe0` {u32, MtString, s64 x4} (V) | EventId, EventName I; StartDate, EndDate G; 2 open | 2/2 |
| 59.4.1 | `C2S_INFINITY_DELIVERY_GET_CATEGORY_STATUS_REQ` | `0x82ab30`: u32 (V) | `CategoryId` I (value 1/1) | 1/1 |
| 59.4.2 | `S2C_INFINITY_DELIVERY_GET_CATEGORY_STATUS_RES` | `0x80a3f0`: header, `0x769de0` (V) | CategoryName, ranking Rank, CharacterName, Point, ClanId, ClanName I; CharacterId, PointUnit, TallyDate G; 8 open | 1/1 |
| 59.8.1 | `C2S_INFINITY_DELIVERY_GET_CATEGORY_LIST_REQ` | `0x82a960`: none (V) | - | 1/1 |
| 59.8.2 | `S2C_INFINITY_DELIVERY_GET_CATEGORY_LIST_RES` | `0x80a2b0`: header, list `0x76a170` {u32, MtString x5, list {u32, MtString}} (V) | EventId, EventName, Description, IconUrl, ImageUrl, CategoryId, CategoryName I; 1 open | 1/1 |
| 59.9.1 | `C2S_INFINITY_DELIVERY_GET_CATEGORY_INFO_REQ` | `0x82a880`: u32 (V) | `CategoryId` I (value 1/1) | 1/1 |
| 59.9.2 | `S2C_INFINITY_DELIVERY_GET_CATEGORY_INFO_RES` | `0x80a230`: header, `0x769b10` (V; tree in the pattern) | Event, Status I (same structure); item ids, Rank I (value); MaxNum, Point, RewardId, RequiredPoint, list names G (context); 8 open | 1/1 |

Total 1,631/1,631.

## 4. Value correlation (`t004/correlate.py`)

| check | result | used for |
| --- | --- | --- |
| 62.15.16 u32 = TrialId of the preceding 62.14.16/62.24.1 | 28/28 | `TrialId` I (server Unk3) |
| 62.24.1 / 62.20.1 TrialId in the preceding 62.18.2 ElementParamList | 28/28, 28/28 | `TrialId` I |
| 62.34.1 (RewardIndex, Amount) = (Id, Num) of a preceding 62.33.2 ItemRewards element | 52/52 | both I |
| 62.35.1 BuffId in the preceding 62.33.2 BuffRewards | 21/21 | `BuffId` I |
| 62.33.2 BuffRewards Level vs name suffix | 1 with "+Lv.1" 68/68; 4 with "Lv.Max" 35/37 | `Level` I (the server serializer writes BuffId there) |
| objective Type vs label text (62.14.16, 62.16.16) | 243/243 agree with the server enum names (1, 4, 5, 7, 8, 10) | `Type` I |
| 62.12.16/18.1/33.1/40.16 LayoutId also set by a 62.26.16 of the stream | 344/344 | `LayoutId` I |
| item ids in `base/etc/itemlist.ipa.json` | 62.18.2 cost 26/26, rewards 1,033/1,033; 62.33.2 52/52; 71.22.2 126/126 and 1,176/1,176; 72.x 1,880/1,880; 59.9.2 27/27 and 107/107 | `ItemId` I |
| 71.22.2 progression Id = stage Id at the same index; connection values and available-reward Ids among the stage Ids | 294/294 each | Ids I |
| 72.0.2 Reward.MissionId = MissionId | 3,393/3,393 | I |
| 72.0.2 (State, Progress vs TargetNum) | State 2/3 only with Progress >= TargetNum (294), 1 only below (2,868); 0 in 231 | `State`, `Progress`, `TargetNum` I |
| 72.0.2 EndDate - StartDate vs text suffix | 24 h for "daily update" 1,053/1,053; 168 h "weekly" 2,223/2,223; 840 h "5-weekly" 117/117 | dates I |
| 72.0.2 Purpose vs `purpose.gmd` texts | 9/9 values agree (e.g. 3 "clear high difficulty dungeon", 7-9 "clear Reward Mission <VAL> times") | `Purpose` I |
| 72.1.16 ids: State 1 before, 2 after (or no later list) | 113/113 | `MissionIdList` I, packet name G |
| 72.2.1 ids: State 2 before, 3 after | 8/8 | `MissionIdList` I |
| 72.2.1 u8 in {13, 19, 20} | 8/8 (19 x6, 20, 13): server StorageType ItemPost, ReceiveInItemBagCraft, ReceiveInStorageCraft = the gmd "receive in post / item bag / storage" | `StorageType` I |
| 72.3.2 u8 = the preceding 72.3.1 u8 | 4/4 (7) | echo, name open |
| 59.4.1 / 59.9.1 u32 = CategoryId of the preceding 59.8.2 | 1/1, 1/1 | `CategoryId` I |
| 59.8.2 EventId = the 59.0.2 EventId | 1/1 | `EventId` I |
| 59.9.2 RankingRewardList Rank among the ranking ranks | 4/4 (10, 100, 1000, 3000) | `Rank` I |
| ranking ClanId == 0 iff ClanName empty; Point non-increasing | 26/26; 24/24 | `ClanId`, `Point` I |

## 5. Open and not run

- Field consumers: the daily mission consumers copy the lists into a manager; the UI that reads the fields, and the
  consumers of groups 59, 62 and 71, were not traced (budget). Names marked G stay guesses; a T014b-style consumer pass
  would settle them.
- Code-only (never captured non-empty): 72.x third list (`0x7626e0`, a {u32, list {CDataMailOptionCourseInfo, MtString}}
  element); 62.24.1 TrialCost; most mail attachment lists inside the daily mission reward.
- Group 59 rests on one capture session (stream85 tcp-stream-11) plus one empty 59.0.2; its G names cannot be
  cross-checked across sessions.
- 62.22.16: the PC ignores the body; 62.12.16 and 62.40.16: purpose open (names stay the CLI names).
- ImHex GUI validation: not run (plbatch export only).

## 6. Verification

- `python -X utf8 -I specs/008-remaining-packets/research/t004/walk.py fits`: 37 ids, 1,631/1,631 JSON with `fits` and `sourceOk` true, 0 `.json.err` ("fits: 0 id(s) with a missing, unfit or failed file").
- `python -X utf8 -I specs/008-remaining-packets/research/t004/walk.py check`: 68/68 samples match (31 ids x 2 files, 6 single-capture ids x 1), 4,034 leaves compared, slack equal ("check: 0 sample(s) differ").
- Export: `packets/imhex-export.sh --force @ <name> </dev/null` per pattern: 37 runs, 1,631 exported, 0 failed, 0 nonfinite, 0 badjson.

## 7. For Sam's inspection

- New JSON: 1,631 files under `packets/decrypted_json/` for the 37 ids (per-id counts in § 3; 37 new patterns, 3 new
  includes).
- Renamed packet: 72.1.16 pattern `S2C_DAILY_MISSION_ACHIEVE_NTC` (raws/JSON keep `S2C_DAILY_72_1_16_NTC`).
- Server names replaced: 62.15.16 `Unk3` -> `TrialId` (I, value 28/28); 62.15.16 flat `LayoutId`/`PosId`/`EpitaphState`
  -> `OmState` (the PC reads them through the shared reader `0x766790`; 62.26.16 likewise); 62.18.2
  `CDataSoulOrdealUnk0`/`Unk1` -> `CDataSoulOrdealRewardSet`/`CDataSoulOrdealRewardEntry`, `Unk1List` -> `RewardList`,
  element `Unk1` -> `Num` (G, context); 62.33.2 `Level` kept although the server serializer writes `BuffId` there (values
  1/4 agree with the level texts). Server `Unk*` fields stay `unk_*` with the lead in the comment.
- Groups 72 and 59 have no server structure: all their names are new (§ 3, § 4).

## 8. Files

- `research/03040008/packets/*-pattern.cpp`: the 37 patterns (§ 3); `include/SeasonDungeon.hexpat`,
  `include/DailyMission.hexpat`, `include/InfinityDelivery.hexpat`; `README.md`: three include rows, 37 table rows and
  the T004 paragraph.
- `specs/008-remaining-packets/research/t004/walk.py` (`stats`, `check`, `fits`, `dump`), `correlate.py`.
