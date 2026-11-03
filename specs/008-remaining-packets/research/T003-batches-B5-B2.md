# 008 T003: batches B5 and B2, patterns, JSON and names (client 03040008)

Date 2026-11-03, base `ee01b82dc3`. Scope: the 33 ids of batches B5 and B2 in `T001-triage.tsv` (2,677 raw files).
All VAs are PC 03040008 (image base `0x400000`). Marks per `spec.md`: V = read in the PC code, I (basis) = inferred,
G (basis) = guess, `open` = kept `unk_*` with its leads in the comment. Pattern comments read `// T003 <mark>: <basis>`.

## 1. Answer

- **33 patterns** in `research/03040008/packets/`, one per id; **2,677/2,677** raw files exported and fit (`fits`
  and `sourceOk` true, no `.json.err`). The layouts are the PC reader/writer width sequences of the T001 TSV (all V);
  70.0.1's list writer is V by 008 T002.
- **Includes**: none changed. Reused: `Quest.hexpat` `CDataQuestOrderList` (PC `0x774a70`, 11.122.2) and
  `CDataQuestList` (PC `0x774530`, 11.5.2), `Furniture.hexpat` `CDataFurnitureLayout` (PC `0x766f90`, 31.53.2),
  `Packet.hexpat` `CDataCommonU32` (PC `0x75e8e0`). The new element types are single-use and live in their patterns.
- **Independent check**: a stdlib walk (`t003/walk.py`) decodes all 2,677 raws with the same layouts (2,677 fit), and
  its `check` mode compares a stratified sample (smallest and largest raw per id; 1 file for the three single-capture
  ids) leaf by leaf with the exported JSON: **63/63 samples match**, slack equal (enum leaves compared on the raw
  number only, since the JSON carries enum names).
- **One packet renamed**: 11.7.16 `S2C_QUEST_11_7_16_NTC` -> pattern `S2C_QUEST_MOB_HUNT_QUEST_LIST_NUM_NTC`
  (I (consumer): the handler pushes notice `cQuestSvNotQuestMobHuntQuestListNum`; no `OnPacket_` string, so not V).
  The raw and JSON files keep the CLI name; renaming them is the CLI's job (TC2 style).

## 2. Sources and method

- Layouts: `T001-triage.tsv` columns `pc_va`, `readers`, `width_seq`; the 006 reports for the ids spec 006 had read
  (T005 § 7, 8, 28, 32, 39-42; T008 § 2.8, 2.10; T009 § 20; T010 § 11, 12, 15, 16, 22; T011 § 13); T002 for 70.0.1.
- IDA: one headless read-only batch (`t003/run.sh` -> `t003/read_funcs.py`, derived from T002's script plus a caller
  list; `DBFL_KILL`, `qexit`) on a `cp` of the wave-2 database
  `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64` (sha256
  `ee07f0b6…8c1d`) in `ddon-data-t003w/`; the copy's sha256 was unchanged afterwards and the copy is deleted. Read:
  the handlers `0x7c3840 0x7e62d0 0x7f1320 0x7f0880 0x7f1bb0 0x7d6fd0 0x7f07d0 0x7f2db0 0x7fede0 0x7d74c0 0x7cdd80
  0x7ed380 0x7d84e0`, senders `0x81e150 0x836dd0 0x837fc0 0x829df0 0x83f4b0 0x840080 0x8302f0 0x834ab0`, readers
  `0x8138e0 0x772d70 0x80ff90 0x76f940 0x76fa80`, and `0x416bb0`. They confirm the 006/T001 statements cited in the
  pattern headers; the S2C handlers mostly keep the packet object in a connection slot, so field consumers lie
  behind getters that this task did not trace (budget; see § 5).
- Values: `t003/walk.py stats` (histogram of every leaf over all captures) and `t003/correlate.py` (pairings below).
- Leads: Arrowgene `Arrowgene.Ddon.Shared/Entity/{PacketStructure,Structure}/*.cs` (local clone).

## 3. Per id

| id | pattern | layout (body, PC) | names and marks | fit |
| --- | --- | --- | --- | ---: |
| 70.0.1 | `C2S_ACTION_SET_PLAYER_ACTION_HISTORY_REQ` | writer `0x77d1e0`: list {u8, u32} (V, T002) | `ActionHistoryList` of {`ActionType`, `Num`}: G (context: 13-value small enum, small counts); lead Unk0/Unk1 | 312/312 |
| 70.0.2 | `S2C_ACTION_SET_PLAYER_ACTION_HISTORY_RES` | reader `0x7ff9d0`: header (V) | - | 312/312 |
| 60.0.2 | `S2C_NPC_GET_NPC_EXTENDED_FACILITY_RES` | `0x80ff90`: header, u32, list `0x76fa80` {u32 x6, u8, MtString, u8} (V) | `NpcId` I (value 7/7, below); element: `FunctionClass`, `FunctionSelect`, `ShopId`, `CustomLabel` G (lead); 5 open | 219/219 |
| 24.6.16 | `S2C_JOB_MASTER_MARK_TARGETS_NTC` | `0x76c500` list of `0x76c5f0` {u8, u32, u8, u8, u32, u32} (V), no header | `CDataJobMasterTargetData` {ReleaseType, ReleaseId, ReleaseLv, ConditionType, TargetId, TargetRank}: I (006 T011 § 13 width parallel to PS4 CDataActiveJobOrder + CDataJobOrderProgress heads; lead agrees); packet name G (lead) | 150/150 |
| 28.24.16 | `S2C_GP_28_24_16_NTC` | inline u32 (V) -> `0xb86860` | `unk_u32` open (3 x83, 4 x1) | 84/84 |
| 28.34.1 | `C2S_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_REQ` | none (V) | - | 42/42 |
| 28.34.2 | `S2C_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES` | `0x809020`: header, bool (V) | `UpdateAppCourseBonusFlag`: V (role: stored in an sGame byte when Result == 0), G (name, packet name) | 42/42 |
| 28.23.1 | `C2S_GP_GP_SHOP_CAN_BUY_REQ` | u32 x3 (V) | `LineupId` I (echo 9/9; PS4 PAWN analogue); 2 open | 9/9 |
| 28.23.2 | `S2C_GP_GP_SHOP_CAN_BUY_RES` | `0x809810`: header, bool, u32 x4 (V) | `CanBuy`, `LineupId` I (PS4 PAWN analogue order; echo 9/9); `unk_u32_2` open (echo of REQ u32 3, 9/9); 2 open (0) | 9/9 |
| 45.3.1 | `C2S_STAMP_BONUS_RECIEVE_DAILY_REQ` | u32, u32 (V) | both V (flow: UI +0x25a8/+0x25ac from the 45.1.2 element, 006 T009), names open | 40/40 |
| 45.3.2, 45.4.2 | `S2C_STAMP_BONUS_RECIEVE_DAILY_RES`, `…_TOTAL_RES` | header (V) | - | 40/40, 1/1 |
| 45.4.1 | `C2S_STAMP_BONUS_RECIEVE_TOTAL_REQ` | none (V) | - | 1/1 |
| 31.53.1 | `C2S_CLAN_GET_FURNITURE_REQ` | none (V) | - | 27/27 |
| 31.53.2 | `S2C_CLAN_GET_FURNITURE_RES` | header, list `0x766f90` (V) | `FurnitureLayouts` of `CDataFurnitureLayout`: I (same structure; value 8/8 item ids are ITEM_CATEGORY_CLAN_FURNITURE) | 27/27 |
| 61.2.1 | `C2S_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_REQ` | none (V) | - | 20/20 |
| 61.2.2 | `S2C_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_RES` | `0x8138e0`: header, u32, list `0x772d70` {u32 x3} (V) | `PawnId` I (value 60/60); `unk_u32_1` I (value 60/60 = CDataPawnList.unk_u32_2), name open; 2 open | 20/20 |
| 64.0.1 | `C2S_MANDRAGORA_GET_MY_MANDRAGORA_REQ` | none (V) | - | 20/20 |
| 11.121.1 | `C2S_QUEST_GET_LEVEL_BONUS_LIST_REQ` | none (V) | - | 182/182 |
| 11.121.2 | `S2C_QUEST_GET_LEVEL_BONUS_LIST_RES` | `0x8161c0`: header, list `0x75a600` {u32, list `0x76d050` {u32, u32, u16 x4}} (V) | MinLevel, MaxLevel, Gold/Exp/Rim/AreaPointRatio G (lead; values 1, 89, 100, 2000, 100, 100 fit the reading); `unk_u32` open (28) | 182/182 |
| 11.122.1 | `C2S_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_REQ` | none (V) | - | 45/45 |
| 11.122.2 | `S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_RES` | `0x815a20`: header, list `0x758bc0` {u8, `0x774a70`, bool, bool, u32} (V) | `Param` = CDataQuestOrderList I (same structure); Category, Important, QuestOrderBackgroundImage G (lead); `unk_bool` open (1 in 585/585) | 45/45 |
| 11.123.1 | `C2S_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_REQ` | none (V) | - | 155/155 |
| 11.123.2 | `S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_RES` | `0x815aa0`: header, bool (V) | `HasNotice` G (context) | 155/155 |
| 11.5.1 | `C2S_QUEST_GET_PACKAGE_QUEST_LIST_REQ` | u32 (V) | `unk_u32` open (not a package id, not the NPC id) | 146/146 |
| 11.5.2 | `S2C_QUEST_GET_PACKAGE_QUEST_LIST_RES` | `0x816830` (V; tree in the pattern) | `unk_u32` I (echo 146/146), name open; list never non-empty, element names G (lead) or open; `QuestList` = CDataQuestList I (same structure) | 146/146 |
| 11.7.16 | `S2C_QUEST_MOB_HUNT_QUEST_LIST_NUM_NTC` (raw `S2C_QUEST_11_7_16_NTC`) | `0x8176e0` list `0x76eee0` {u32, u8} (V) | list name I (notice class); `Num` G (context); `unk_u32` open | 43/43 |
| 11.68.16 | `S2C_QUEST_QUEST_BOARD_RELOAD_NTC` | `0x8175d0` bool, bool, u32 (V) | both bools V (role: chat messages 0x132/0x133), names open; `Count` V (role) I (name; lead agrees) | 1/1 |
| 11.88.16 | `S2C_QUEST_11_88_16_NTC` | handler reads nothing (V) | - (meaning open) | 20/20 |
| 11.118.16 | `S2C_QUEST_11_118_16_NTC` | u8 read and discarded (V) | `unk_u8` (meaning open) | 41/41 |
| 14.11.16 | `C2S_WARP_14_11_16_NTC` | u32 (V) | `StartPointId` G (value 51/57, below) | 57/57 |
| 14.14.1 | `C2S_WARP_GET_START_POINT_LIST_REQ` | none (V) | - | 42/42 |
| 14.14.2 | `S2C_WARP_GET_START_POINT_LIST_RES` | `0x81d8e0`: header, list u32 (V) | `StartPointIdList` G (context; lead WarpPointIdList) | 42/42 |

Total 2,677/2,677. Per-id JSON counts equal the raw counts (`walk.py fits`).

## 4. Value correlation (`t003/correlate.py`)

| check | result | used for |
| --- | --- | --- |
| 60.0.2 NpcId = NpcID of the preceding 60.0.1 in the stream | 7/7 nonzero (706 x4, 4 x3); 212/219 are 0 | `NpcId` I |
| 11.5.2 u32 = preceding 11.5.1 u32 | 146/146 | echo, I |
| 11.5.1 u32 = NpcID of the preceding 60.0.1 | 0/105; package ids in `game_common/ui/00_param/package_quest/package_quest_info.pqi.json` are 1-3 | name stays open |
| 28.23.2 u32 #1 = 28.23.1 u32 #1 | 9/9 | `LineupId` I |
| 28.23.2 u32 #2 = 28.23.1 u32 #3 (u32 #2: 0/9) | 9/9 | echo noted |
| 14.11.16 u32 in a 14.14.2 StartPointIdList of the same capture | 51/57 (1 x48, 87 x3); 20, 21, 72, 97 not | G only: 1 dominates |
| 61.2.2 PawnId in the 8.2.2 pawn list of the same stream | 60/60 | `PawnId` I |
| 61.2.2 element u32 #2 = that pawn's `CDataPawnList.unk_u32_2` | 60/60 (values 3, 0) | I (value), name open |
| 31.53.2 ItemID in `client/03040008/base/etc/itemlist.ipa.json` | 8/8 distinct ids are ITEM_CATEGORY_CLAN_FURNITURE (e.g. 21129 Christmas Tree) | I (value) |

## 5. Open and not run

- Consumers behind the connection-slot getters (60.0.2, 61.2.2, 11.121.2, 11.122.2, 11.123.2, 70.0.1's callers) were
  not traced: names marked G stay guesses; a T014b-style consumer pass would settle them.
- Code-only (never captured non-empty): 11.5.2's package list; 60.0.2's element is captured in 4 files with one value
  set; 11.68.16 has one capture.
- 11.88.16 and 11.118.16: the PC ignores both bodies; their meaning cannot come from the client.
- ImHex GUI validation: not run (plbatch export only).

## 6. For Sam's inspection

- New JSON: 2,677 files under `packets/decrypted_json/` for the 33 ids (per-id counts in § 3; 33 new patterns).
- Renamed packet: 11.7.16 pattern `S2C_QUEST_MOB_HUNT_QUEST_LIST_NUM_NTC` (raws/JSON keep `S2C_QUEST_11_7_16_NTC`).
- Server names replaced: 14.14.2 `WarpPointIdList` -> `StartPointIdList` (packet and PC handler name GET_START_POINT_LIST);
  61.2.2 `PawnTrainingPreparationInfoToAdvices` -> `PreparationInfoList` (shorter, same meaning); 11.123.2 `Unk0` ->
  `HasNotice` (G); 28.34.2 (no server structure) `UpdateAppCourseBonusFlag` (G); 70.0.1 `Unk0`/`Unk1` ->
  `ActionType`/`Num` (G); 11.7.16 (no server structure) `MobHuntQuestListNum`/`Num`; 14.11.16 (server: none) `StartPointId` (G).
- Server names kept as G (lead): 60.0.2 FunctionClass/FunctionSelect/ShopId/CustomLabel; 11.121.2 level bonus element;
  11.122.2 Category/Important/QuestOrderBackgroundImage; 24.6.16 (I, lead agrees).

## 7. Files

- `research/03040008/packets/*-pattern.cpp`: the 33 patterns (§ 3); `research/03040008/packets/README.md`: 33 table
  rows and the T003/G-mark paragraph.
- `specs/008-remaining-packets/research/t003/walk.py` (`stats`, `check`, `fits`), `correlate.py`, `read_funcs.py`,
  `run.sh`. Commands, from `D:/ddon-data`: `python -X utf8 -I specs/008-remaining-packets/research/t003/walk.py fits`
  (0 bad ids), `… walk.py check` (63/63 match), `… correlate.py`; export per pattern
  `packets/imhex-export.sh --force @ <name> </dev/null` (33 runs, 0 failed, 0 badjson).
