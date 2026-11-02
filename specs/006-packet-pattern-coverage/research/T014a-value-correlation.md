# 006 T014a: value correlation of the unknown packet fields (client 03040008)

Basis 2 of spec 006 "Naming unknown fields by inference": does an `unk_*` field hold, in the same session, the values of a named field? Nothing is renamed here; every candidate below is `I (value: n/m match <field> in <packet>)` material at best and needs the coincidence check the spec asks for (constants, 0/1 and small enums need more evidence).

Produced by `research/03040008/packets/tools/unk_correlate.py` (stdlib only); one row per unknown (packet, key path) in `T014a-value-correlation.tsv`.

## Inputs and run

- build: client 03040008 (PC), patterns in `research/03040008/packets/`
- patterns (packets): 480
- struct definitions parsed: 853
- stream directories scanned: 125
- sessions: 41
- session unit: one capture file (all its TCP streams: login and game server)
- JSON files read: 155663
- JSON files of unpatterned names skipped: 0
- JSON files unreadable (invalid JSON, skipped): 65 (e.g. `stream85-marked.pcapng_tcp-stream-11/100314_C2S_CONTEXT_SET_CONTEXT_NTC_2019-11-18T12_21_56.0045759-08_00.35_9_16.json`)
- packets with JSON: 472
- unknown (packet, key path) rows: 443
- declared value-bearing unk fields: 238
- runtime: 27 s (CPython 3.14.8, stdlib json)

## Method

1. Patterns: every `*-pattern.cpp` names one packet; the struct declarations of the patterns and `include/*.hexpat` resolve each JSON key path to the struct and file that declare it (`defined_in`, `?` when the light parser cannot follow the path).
2. JSON: each stream directory of `packets/decrypted_json/` is scanned once; only files whose name carries a patterned packet are read. Each file is flattened to scalar leaves by key path (list levels as `[]`; `count`, `length` and the header and fit keys are dropped). A leaf is unknown when its deciding key (the nearest key that is not `entries`, `value`, `m_unValue` or `m_ucValue`) starts with `unk`; all other leaves are named reference fields.
3. Session = one capture file (all its TCP streams: login and game server): all values of a field within one session form its value set for that session.
4. Considered values of an unknown: the informative distinct values per session (integers with |v| >= 256, excluding 0xFFFF, 0x7FFFFFFF, 0xFFFFFFFF, all-ones u64 and -1; non-integral floats with |v| >= 256; strings of >= 3 characters). An unknown with no informative value is matched on all its values except 0 and 1 (`basis` all-nonbinary) and can reach the weak tier only.
5. Per reference field R (packet + key path) the score is `share` = (session, value) pairs of the unknown found in R's value set of the same session / all considered pairs; `agree` = sessions whose own share is >= 0.5; `other_share` = pairs that R holds in another session (a high other_share against share means a global catalogue value such as an item or stage id; a low one, a session-specific value such as a character id or UID). A pseudo-reference tests timestamps: values within capture time -10 y/+2 y as epoch seconds or milliseconds.
6. Coincidence control: `chance` = the share expected if the unknown's integer values hit the reference at its density (distinct values / (max - min + 1)) inside its range. A reference whose chance exceeds share x 0.33 is too dense to tell (`dense-reference`; the row stays weak).
7. The best reference per leaf name is kept and the top 3 leaf names are reported, ranked by share - chance, agree, lower other_share, id-like name.

Caveat on `other_share`: the captures mostly record one player account (inferred: the storage owner id 2144504 recurs in all 41 sessions), so its character and pawn ids recur in nearly every capture; for these ids other_share is high although they are session data. Specificity across sessions therefore cannot separate account ids from catalogue ids in this corpus; `chance` and the reference name carry that judgement.

Tiers:

- **strong**: >= 3 informative distinct values, share >= 0.8, agree >= 2 sessions.
- **medium**: >= 3 informative distinct values and share >= 0.5, but not strong (usually a single session).
- **weak**: best share >= 0.2 otherwise (few informative values, or matched on small values only).
- **unexplained**: no reference reaches share 0.2.
- **no-data**: a declared value-bearing unk field that no JSON file holds.

Flags: `constant`, `0-1`, `small-enum` (<= 16 distinct values, all |v| < 256), `lt3-distinct`, `few-informative` (< 3 informative distinct values), `global-values` (other_share >= share), `dense-reference` (chance > share/3).

## Summary

| Tier | Rows |
| --- | --- |
| strong | 8 |
| medium | 10 |
| weak | 186 |
| unexplained | 239 |
| no-data | 35 |

## Strong candidates

Each with the best reference, the runners-up and two example value pairs (unknown file -> reference file, both in `packets/decrypted_json/`).

### S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES `packet.unk_list_1.entries[].unk_s64`

- declared: `include/Area.hexpat` CDataAreaUnkU32BoolS64.unk_s64; values 389, distinct 39 (informative 39), sessions 41, range 1562529600..1575489600; flags -
- best: **epoch_s** in (timestamp epoch_s, capture time -10 y/+2 y) (41/41, agree 41/41, other 0.00, chance 0.00)
- also: NextReloadTime in S2C_QUEST_GET_QUEST_PARTY_BONUS_LIST_RES:packet.NextReloadTime (28/41, agree 28/41, other 0.05, chance 0.00)
- also: BeginDateTime in S2C_LOADING_INFO_LOADING_GET_INFO_RES:packet.LoadingInfoScheduleList.entries[].BeginDateTime (6/41, agree 6/41, other 0.15, chance 0.00)
- example: 1562529600: `stream1-marked.pcapng_tcp-stream-35/12143_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-06T11_05_53.3305280-07_00.23_8_2.json` -> `-`
- example: 1563307200: `stream10-musicplayer-marked.pcapng_tcp-stream-9/10455_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-15T09_48_51.4727420-07_00.23_8_2.json` -> `-`

### S2C_ITEM_GET_STORAGE_ITEM_LIST_RES `packet.ItemList.entries[].unk_u32_1`

- declared: `include/Item.hexpat` CDataItemList.unk_u32_1; values 21644, distinct 4 (informative 3), sessions 41, range 0..2184603; flags -
- best: **CharacterID** in S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES:packet.MemberList.entries[].CharacterListElement.BaseInfo.CharacterID (41/41, agree 41/41, other 0.98, chance 0.00)
- also: HostCharacterID in S2C_PARTY_PARTY_JOIN_NTC:packet.HostCharacterID (41/41, agree 41/41, other 0.98, chance 0.00)
- also: LeaderCharacterID in S2C_PARTY_PARTY_JOIN_NTC:packet.LeaderCharacterID (41/41, agree 41/41, other 0.98, chance 0.00)
- example: 2144504: `stream1-marked.pcapng_tcp-stream-35/12035_S2C_ITEM_GET_STORAGE_ITEM_LIST_RES_2019-07-06T11_05_44.3285729-07_00.10_3_2.json` -> `stream1-marked.pcapng_tcp-stream-35/12073_S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES_2019-07-06T11_05_46.8135750-07_00.31_4_2.json`
- example: 2144504: `stream10-musicplayer-marked.pcapng_tcp-stream-9/10350_S2C_ITEM_GET_STORAGE_ITEM_LIST_RES_2019-07-15T09_48_41.3040759-07_00.10_3_2.json` -> `stream10-musicplayer-marked.pcapng_tcp-stream-9/10388_S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES_2019-07-15T09_48_43.7797060-07_00.31_4_2.json`

### S2C_ITEM_GET_STORAGE_ITEM_LIST_RES `packet.ItemList.entries[].unk_u32_2`

- declared: `include/Item.hexpat` CDataItemList.unk_u32_2; values 21644, distinct 8 (informative 7), sessions 41, range 0..14463443; flags -
- best: **PawnID** in S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES:packet.PawnEquipItemList.entries[].PawnID (83/83, agree 41/41, other 0.96, chance 0.00)
- also: PawnId in S2C_PAWN_GET_MYPAWN_LIST_RES:packet.PawnList.entries[].PawnId (83/83, agree 41/41, other 0.96, chance 0.00)
- also: mPawnId in C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ:packet.m_Data.mCheckPawnHistory[].mPawnId (61/83, agree 21/41, other 0.95, chance 0.00)
- example: 14367695: `stream1-marked.pcapng_tcp-stream-35/12035_S2C_ITEM_GET_STORAGE_ITEM_LIST_RES_2019-07-06T11_05_44.3285729-07_00.10_3_2.json` -> `stream1-marked.pcapng_tcp-stream-35/12044_S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES_2019-07-06T11_05_45.0302529-07_00.29_0_2.json`
- example: 14367695: `stream10-musicplayer-marked.pcapng_tcp-stream-9/10350_S2C_ITEM_GET_STORAGE_ITEM_LIST_RES_2019-07-15T09_48_41.3040759-07_00.10_3_2.json` -> `stream10-musicplayer-marked.pcapng_tcp-stream-9/10359_S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES_2019-07-15T09_48_42.0023610-07_00.29_0_2.json`

### S2C_AREA_GET_SPOT_INFO_LIST_RES `packet.unk_list_1.entries[].unk_s64`

- declared: `include/Area.hexpat` CDataAreaUnkU32BoolS64.unk_s64; values 116, distinct 25 (informative 25), sessions 26, range 1562616000..1574193600; flags -
- best: **epoch_s** in (timestamp epoch_s, capture time -10 y/+2 y) (26/26, agree 26/26, other 0.00, chance 0.00)
- also: NextReloadTime in S2C_QUEST_GET_QUEST_PARTY_BONUS_LIST_RES:packet.NextReloadTime (18/26, agree 18/26, other 0.04, chance 0.00)
- also: BeginDateTime in S2C_LOADING_INFO_LOADING_GET_INFO_RES:packet.LoadingInfoScheduleList.entries[].BeginDateTime (5/26, agree 5/26, other 0.19, chance 0.00)
- example: 1564084800: `stream21-failedlogin-marked.pcapng_tcp-stream-48/13720_S2C_AREA_GET_SPOT_INFO_LIST_RES_2019-07-25T12_32_15.6003539-07_00.23_11_2.json` -> `-`
- example: 1562616000: `stream3-party-experiments-marked.pcapng_tcp-stream-47/13147_S2C_AREA_GET_SPOT_INFO_LIST_RES_2019-07-08T10_36_28.8993890-07_00.23_11_2.json` -> `-`

### S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES `packet.unk_list_0.entries[].unk_s64`

- declared: `include/Area.hexpat` CDataAreaUnkU32U32S64.unk_s64; values 578, distinct 11 (informative 11), sessions 21, range 1552078219..1570125181; flags -
- best: **epoch_s** in (timestamp epoch_s, capture time -10 y/+2 y) (144/144, agree 21/21, other 0.00, chance 0.00)
- example: 1552078219: `stream21-failedlogin-marked.pcapng_tcp-stream-48/12456_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-25T12_30_08.6921489-07_00.23_8_2.json` -> `-`
- example: 1562086330: `stream21-failedlogin-marked.pcapng_tcp-stream-48/12456_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-25T12_30_08.6921489-07_00.23_8_2.json` -> `-`

### S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES `packet.unk_list_0.entries[].unk_u32_0`

- declared: `include/Area.hexpat` CDataAreaUnkU32U32S64.unk_u32_0; values 578, distinct 7 (informative 7), sessions 21, range 1081..1089; flags global-values
- best: **ReleaseList** in S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES:packet.ReleaseAreaInfoSetList.entries[].ReleaseList.entries[].m_unValue (144/144, agree 21/21, other 1.00, chance 0.25)
- also: mHp in C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mCondition.mHp (2/144, agree 1/21, other 0.42, chance 0.01)
- also: Param02 in S2C_QUEST_GET_SET_QUEST_LIST_RES:packet.SetQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 (0/144, agree 0/21, other 0.42, chance 0.00)
- example: 1081: `stream21-failedlogin-marked.pcapng_tcp-stream-48/12456_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-25T12_30_08.6921489-07_00.23_8_2.json` -> `stream21-failedlogin-marked.pcapng_tcp-stream-48/12456_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-25T12_30_08.6921489-07_00.23_8_2.json`
- example: 1082: `stream21-failedlogin-marked.pcapng_tcp-stream-48/12456_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-25T12_30_08.6921489-07_00.23_8_2.json` -> `stream21-failedlogin-marked.pcapng_tcp-stream-48/12456_S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES_2019-07-25T12_30_08.6921489-07_00.23_8_2.json`

### C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ `packet.m_Data.bitStream.unk_u32_13508[].value`

- declared: `include/CharacterData.hexpat` CharacterBinSaveData.bitStream; values 752, distinct 5 (informative 4), sessions 41, range 0..14454766; flags -
- best: **PawnID** in S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES:packet.PawnEquipItemList.entries[].PawnID (61/61, agree 21/21, other 0.98, chance 0.00)
- also: PawnId in S2C_PAWN_GET_MYPAWN_LIST_RES:packet.PawnList.entries[].PawnId (61/61, agree 21/21, other 0.98, chance 0.00)
- also: mPawnId in S2C_CHARACTER_DECIDE_CHARACTER_ID_RES:packet.Bin.mCheckPawnHistory[].mPawnId (60/61, agree 20/21, other 0.98, chance 0.00)
- example: 14310734: `stream21-failedlogin-marked.pcapng_tcp-stream-48/13783_C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ_2019-07-25T12_32_37.9225881-07_00.9_1_1.json` -> `stream21-failedlogin-marked.pcapng_tcp-stream-48/12347_S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES_2019-07-25T12_29_59.7463090-07_00.29_0_2.json`
- example: 14313101: `stream21-failedlogin-marked.pcapng_tcp-stream-48/13783_C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ_2019-07-25T12_32_37.9225881-07_00.9_1_1.json` -> `stream21-failedlogin-marked.pcapng_tcp-stream-48/12347_S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES_2019-07-25T12_29_59.7463090-07_00.29_0_2.json`

### S2C_CHARACTER_DECIDE_CHARACTER_ID_RES `packet.Bin.bitStream.unk_u32_13508[].value`

- declared: `include/CharacterData.hexpat` CharacterBinSaveData.bitStream; values 672, distinct 5 (informative 4), sessions 41, range 0..14454766; flags global-values
- best: **PawnID** in S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES:packet.PawnEquipItemList.entries[].PawnID (61/62, agree 21/21, other 0.98, chance 0.00)
- also: PawnId in S2C_PAWN_GET_MYPAWN_LIST_RES:packet.PawnList.entries[].PawnId (61/62, agree 21/21, other 0.98, chance 0.00)
- also: mPawnId in S2C_CHARACTER_DECIDE_CHARACTER_ID_RES:packet.Bin.mCheckPawnHistory[].mPawnId (60/62, agree 20/21, other 0.97, chance 0.00)
- example: 14310734: `stream21-failedlogin-marked.pcapng_tcp-stream-47/12137_S2C_CHARACTER_DECIDE_CHARACTER_ID_RES_2019-07-25T12_29_48.8616731-07_00.2_0_2.json` -> `stream21-failedlogin-marked.pcapng_tcp-stream-48/12347_S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES_2019-07-25T12_29_59.7463090-07_00.29_0_2.json`
- example: 14313101: `stream21-failedlogin-marked.pcapng_tcp-stream-47/12137_S2C_CHARACTER_DECIDE_CHARACTER_ID_RES_2019-07-25T12_29_48.8616731-07_00.2_0_2.json` -> `stream21-failedlogin-marked.pcapng_tcp-stream-48/12347_S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES_2019-07-25T12_29_59.7463090-07_00.29_0_2.json`

## Medium candidates

| Packet | Key path | Declared | Distinct (inf.) | Best match | Share | Agree | Other | Chance | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES | `packet.CycleContentsNewsList.entries[].CycleContentsRankList.entries[].unk_u32` | `S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES-pattern.cpp` CDataCycleContentsRank | 5 (4) | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 4/4 | 1/1 | 1.00 | 0.06 | global-values |
| S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | `packet.TutorialQuestList.entries[].Param.unk_u64` | `include/Quest.hexpat` CDataQuestList | 6 (5) | (timestamp epoch_s, capture time -10 y/+2 y) | 5/5 | 1/1 | 0.00 | 0.00 |  |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_5` | `include/Shop.hexpat` CDataGoodsRequirement | 7 (6) | S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES:packet.CycleContentsNewsList.entries[].EnemyInfo.entries[].GroupId | 6/6 | 1/1 | 0.00 | 0.16 |  |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List0.entries[].unk_u32_0` | `include/Stage.hexpat` CDataAreaChangeUnk0 | 4 (4) | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 4/4 | 1/1 | 1.00 | 0.00 | global-values |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 7 (6) | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 102/143 | 31/41 | 0.71 | 0.06 | global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_List[].unk_u16_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 84 (9) | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 6/9 | 6/9 | 0.67 | 0.06 | global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 4 (3) | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 2/3 | 1/1 | 0.67 | 0.00 | global-values |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.unk_order_list_7.entries[].unk_u32` | `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC-pattern.cpp` CDataQuestJoinLobbyUnkOrderList | 4 (4) | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 40/80 | 20/20 | 0.50 | 0.06 | global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 7 (6) | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 39/78 | 20/21 | 0.50 | 0.06 | global-values |
| S2C_QUEST_REWARD_BOX_LIST_NUM_NTC | `packet.unk_u16_0` | `S2C_QUEST_REWARD_BOX_LIST_NUM_NTC-pattern.cpp` S2C_QUEST_REWARD_BOX_LIST_NUM_NTC | 13 (4) | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 2/4 | 1/1 | 0.50 | 0.06 | global-values |

## Weak candidates

Matches too thin to name anything (few or small values, or a low share); listed for the consumer trace (basis 1).

| Packet | Key path | Distinct (inf.) | Basis | Best match | Share | Agree | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES | `packet.unk_serverResult` | 1 (1) | informative | L2C_GET_ERROR_MESSAGE_LIST_NTC:packet.ErrorMessage.entries[].ErrorID | 41/41 | 41/41 | constant,lt3-distinct,few-informative,global-values |
| S2C_QUEST_REWARD_BOX_LIST_NUM_NTC | `packet.unk_u16_1` | 1 (1) | informative | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.BaseWalletPoint.entries[].Value | 41/41 | 41/41 | constant,lt3-distinct,few-informative,global-values |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_u16` | 15 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 536/536 | 41/41 | small-enum,few-informative,global-values |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_u8_1` | 2 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 41/41 | 41/41 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u16` | 15 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 349/349 | 41/41 | small-enum,few-informative,global-values |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_u16` | 15 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 426/426 | 41/41 | small-enum,few-informative,global-values |
| S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES | `packet.PartyQuestProgressInfo.QuestOrderList.entries[].unk_u32_list.entries[]` | 22 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 821/821 | 41/41 | few-informative,global-values |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Detail.unk_u16_1` | 4 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 104/104 | 41/41 | small-enum,few-informative,global-values |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.WorldManageQuestOrderList.entries[].Param.unk_u32_list.entries[]` | 21 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 820/820 | 41/41 | few-informative,global-values |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_List_0.entries[].unk_u32_0` | 16 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 615/615 | 41/41 | small-enum,few-informative,global-values |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_List_1.entries[].unk_u8` | 2 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 41/41 | 41/41 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_u16` | 1 (0) | all-nonbinary | L2C_GP_COURSE_GET_INFO_RES:packet.Effects.entries[].Param0 | 41/41 | 41/41 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_u32_1` | 1 (1) | informative | L2C_GET_ERROR_MESSAGE_LIST_NTC:packet.ErrorMessage.entries[].ErrorID | 41/41 | 41/41 | constant,lt3-distinct,few-informative,global-values |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_u32_2` | 1 (0) | all-nonbinary | S2C_QUEST_GET_SET_QUEST_LIST_RES:packet.SetQuestList.entries[].Detail.BaseAreaPoint | 41/41 | 41/41 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_STAMP_BONUS_CHECK_RES | `packet.unk_List.entries[].unk_u32_1` | 1 (0) | all-nonbinary | L2C_GP_COURSE_GET_INFO_RES:packet.Effects.entries[].EffectUID | 39/39 | 39/39 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_STAMP_BONUS_GET_LIST_RES | `packet.DailyGroupList.entries[].unk_u32_1` | 1 (0) | all-nonbinary | L2C_GP_COURSE_GET_INFO_RES:packet.Effects.entries[].EffectUID | 39/39 | 39/39 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_USER_LIST_JOIN_NTC | `packet.LobbyMemberInfoList.entries[].unk_u8` | 3 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 52/52 | 35/35 | small-enum,few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.unk_List[].unk_u8` | 17 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 578/578 | 34/34 | few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_ElementList[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 99/99 | 33/33 | small-enum,few-informative,global-values |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u16` | 2 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 31/31 | 31/31 | small-enum,lt3-distinct,few-informative,global-values |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 90/90 | 31/31 | small-enum,few-informative,global-values |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_1` | 2 (0) | all-nonbinary | C2S_PROFILE_SET_SHORTCUT_LIST_REQ:packet.ShortcutList.entries[].ShortcutID | 28/28 | 28/28 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u16` | 15 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 274/274 | 27/27 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_2` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 27/27 | 27/27 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipVisualList[].unk_ElementList[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 65/65 | 26/26 | small-enum,few-informative,global-values |
| S2C_QUEST_FORT_DEFENSE_NTC | `packet.SituationInfoDetailList.entries[].unk_u32_u32_list.entries[].unk_u32_0` | 5 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 96/96 | 24/24 | small-enum,few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_ElementList[].unk_u16` | 18 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 84/84 | 23/23 | few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_List[].unk_u8_0` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 35/35 | 22/22 | small-enum,few-informative,global-values |
| S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES | `packet.PartyQuestProgressInfo.QuestOrderList.entries[].DeliveryItemArray.entries[].unk_u16_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 22/22 | 22/22 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Param.DeliveryItemList.entries[].unk_u16_1` | 4 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 25/25 | 22/22 | small-enum,few-informative,global-values |
| S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES | `packet.unk_list_0.entries[].unk_u32_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 21/21 | 21/21 | constant,small-enum,lt3-distinct,few-informative,global-values |
| C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ | `packet.m_Data.bitStream.unk_u32_13572[].value` | 5 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 61/61 | 21/21 | small-enum,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.Bin.bitStream.unk_u32_13572[].value` | 5 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 62/62 | 21/21 | small-enum,few-informative,global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_List_0.entries[].unk_u8_0` | 3 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 21/21 | 21/21 | small-enum,few-informative,global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_List_1.entries[].unk_u16` | 11 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 184/184 | 21/21 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_List_1.entries[].unk_u8_1` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 41/41 | 21/21 | small-enum,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u16` | 5 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 101/101 | 21/21 | small-enum,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 21/21 | 21/21 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_u8_1` | 2 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 21/21 | 21/21 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u16` | 5 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 103/103 | 21/21 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 21/21 | 21/21 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_4` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 21/21 | 21/21 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_LIST_RES | `packet.PawnList.entries[].unk_u32_2` | 2 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 21/21 | 21/21 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_QUEST_GET_MAIN_QUEST_LIST_RES | `packet.MainQuestList.entries[].unk_u32_list.entries[]` | 3 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 41/41 | 21/21 | small-enum,few-informative,global-values |
| S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | `packet.TutorialQuestList.entries[].Param.DeliveryItemList.entries[].unk_u16_0` | 4 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 21/21 | 21/21 | small-enum,few-informative,global-values |
| S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | `packet.TutorialQuestList.entries[].Param.DeliveryItemList.entries[].unk_u16_1` | 4 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 41/41 | 21/21 | small-enum,few-informative,global-values |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_state.unk_u32_0` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 40/40 | 20/20 | small-enum,few-informative,global-values |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_u32_2` | 3 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 40/40 | 20/20 | small-enum,few-informative,global-values |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.unk_list_3.entries[].unk_u8` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestOrderConditionParamList.entries[].Param01 | 20/20 | 20/20 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.unk_u32` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 20/20 | 20/20 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.unk_order_list_7.entries[].unk_u8` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 20/20 | 20/20 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_1.entries[].unk_u16` | 10 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 118/118 | 20/20 | small-enum,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.unk_List.entries[].unk_u16` | 10 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 118/118 | 20/20 | small-enum,few-informative,global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_ElementList.entries[].unk_u16` | 7 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 100/100 | 20/20 | small-enum,few-informative,global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 60/60 | 20/20 | small-enum,few-informative,global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_List_0.entries[].unk_u16_1` | 2 (0) | all-nonbinary | C2S_PROFILE_SET_SHORTCUT_LIST_REQ:packet.ShortcutList.entries[].ShortcutID | 20/20 | 20/20 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_ElementList.entries[].unk_u16` | 2 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 20/20 | 20/20 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 59/59 | 20/20 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_1.entries[].unk_u16` | 7 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 100/100 | 20/20 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_List_0.entries[].unk_u16` | 7 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 100/100 | 20/20 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_3` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 20/20 | 20/20 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_LIST_RES | `packet.PawnList.entries[].unk_u32_0` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 20/20 | 20/20 | small-enum,few-informative,global-values |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.TutorialQuestOrderList.entries[].Param.QuestLog.QuestTalkInfoList.entries[].unk_u32` | 3 (2) | informative | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.SoloQuestOrderList.entries[].QuestId | 40/40 | 20/20 | few-informative,global-values |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.TutorialQuestOrderList.entries[].Param.unk_u64` | 2 (1) | informative | (timestamp epoch_s, capture time -10 y/+2 y) | 20/20 | 20/20 | lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u16` | 2 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 19/19 | 19/19 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 56/56 | 19/19 | small-enum,few-informative,global-values |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_List_0.entries[].unk_u16_1` | 2 (0) | all-nonbinary | C2S_PROFILE_SET_SHORTCUT_LIST_REQ:packet.ShortcutList.entries[].ShortcutID | 19/19 | 19/19 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_1` | 2 (0) | all-nonbinary | C2S_PROFILE_SET_SHORTCUT_LIST_REQ:packet.ShortcutList.entries[].ShortcutID | 18/18 | 18/18 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.unk_u8_1` | 2 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 17/17 | 16/16 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_List[].unk_u8_1` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 26/26 | 14/14 | small-enum,few-informative,global-values |
| S2C_QUEST_GET_AREA_BONUS_LIST_RES | `packet.AreaBonusList.entries[].unk_u16` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 10/10 | 10/10 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u16` | 15 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 117/117 | 9/9 | small-enum,few-informative,global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u16` | 9 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 53/53 | 9/9 | small-enum,few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipVisualList[].unk_ElementList[].unk_u16` | 6 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 13/13 | 8/8 | small-enum,few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipVisualList[].unk_List[].unk_u8_0` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 10/10 | 8/8 | small-enum,few-informative,global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 12/12 | 5/5 | small-enum,few-informative,global-values |
| S2C_LOBBY_LOBBY_CHAT_MSG_NTC | `packet.unk_u8` | 3 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 3/3 | 3/3 | small-enum,few-informative,global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u16` | 3 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 6/6 | 3/3 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 9/9 | 3/3 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_List_0.entries[].unk_u16_1` | 7 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 7/7 | 3/3 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_List_1.entries[].unk_u16` | 21 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 31/31 | 3/3 | few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_List_1.entries[].unk_u8` | 17 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 51/51 | 3/3 | few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_u16` | 15 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 42/42 | 3/3 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_u16` | 15 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 42/42 | 3/3 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_u8_1` | 1 (0) | all-nonbinary | S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC:packet.m_PlayerInfo.m_unActNo | 3/3 | 3/3 | constant,small-enum,lt3-distinct,few-informative,global-values |
| C2S_SKILL_GET_ACQUIRABLE_ABILITY_LIST_REQ | `packet.unk_u32` | 1 (1) | informative | S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES:packet.MemberList.entries[].CharacterListElement.BaseInfo.CharacterID | 2/2 | 2/2 | constant,lt3-distinct,few-informative,global-values |
| C2S_SKILL_GET_ACQUIRABLE_SKILL_LIST_REQ | `packet.unk_u32` | 1 (1) | informative | S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES:packet.MemberList.entries[].CharacterListElement.BaseInfo.CharacterID | 2/2 | 2/2 | constant,lt3-distinct,few-informative,global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_1` | 2 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 2/2 | 2/2 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 6/6 | 2/2 | small-enum,few-informative,global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_0` | 1 (1) | informative | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestFlagList.entries[].FlagId | 2/2 | 2/2 | constant,lt3-distinct,few-informative,global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipVisualList[].unk_List[].unk_u8_1` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 4/4 | 2/2 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_ElementList.entries[].unk_u16` | 4 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 5/5 | 2/2 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_List_0.entries[].unk_u8_0` | 3 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 3/3 | 2/2 | small-enum,few-informative,global-values |
| S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES | `packet.Items.entries[].unk_u32_0` | 2 (0) | all-nonbinary | S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC:packet.m_PlayerInfo.m_unActNo | 2/2 | 2/2 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | `packet.UpdateItemList.entries[].ItemInfo.unk_u32_1` | 2 (1) | informative | S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES:packet.MemberList.entries[].CharacterListElement.BaseInfo.CharacterID | 2/2 | 2/2 | lt3-distinct,few-informative,global-values |
| C2S_CHARACTER_CHARACTER_PENALTY_REVIVE_REQ | `packet.unk_u32` | 1 (1) | informative | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.inc | 1/1 | 1/1 | constant,lt3-distinct,few-informative |
| C2S_DISPEL_GET_DISPEL_ITEM_SETTING_REQ | `packet.unk_u32` | 1 (0) | all-nonbinary | S2C_QUEST_GET_QUEST_COMPLETE_LIST_RES:packet.QuestIdList.entries[].QuestId | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative |
| C2S_GP_GP_SHOP_DISPLAY_BUY_REQ | `packet.unk_u32` | 7 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 6/6 | 1/1 | small-enum,few-informative,global-values |
| C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC | `packet.unk_u32` | 9 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mCondition.mCommonWork | 7/7 | 1/1 | small-enum,few-informative |
| C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC | `packet.unk_u32` | 9 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mCondition.mCommonWork | 7/7 | 1/1 | small-enum,few-informative |
| C2S_LOBBY_LOBBY_CHAT_MSG_REQ | `packet.unk_u32_0` | 4 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 2/2 | 1/1 | small-enum,few-informative |
| C2S_LOBBY_LOBBY_CHAT_MSG_REQ | `packet.unk_u8` | 2 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative |
| C2S_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_REQ | `packet.unk_u8` | 1 (0) | all-nonbinary | C2S_PROFILE_SET_SHORTCUT_LIST_REQ:packet.ShortcutList.entries[].ShortcutID | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_u32_0` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].KeyId | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_u32_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES | `packet.DispelBaseItemList.entries[].LotItemList.entries[].ItemLot.unk_u8` | 1 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mCondition.mRegionRateBit | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative |
| S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES | `packet.CycleContentsNewsList.entries[].CycleContentsRankList.entries[].unk_u8` | 2 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_ElementList[].unk_u32` | 1 (1) | informative | C2S_LOBBY_LOBBY_DATA_MSG_REQ:packet.Data.msg.ctrlAction.mCondition.mHp | 1/1 | 1/1 | constant,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_PawnInfo.unk_List[].unk_u8_0` | 5 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mCondition.mRegionRateBit | 5/5 | 1/1 | small-enum,few-informative |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_PawnInfo.unk_List[].unk_u8_1` | 2 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_List_0.entries[].unk_u8_1` | 3 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 2/2 | 1/1 | small-enum,few-informative,global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 3/3 | 1/1 | small-enum,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_List_0.entries[].unk_u16_0` | 1 (1) | informative | C2S_QUEST_QUEST_PROGRESS_REQ:packet.KeyId | 1/1 | 1/1 | constant,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_List_0.entries[].unk_u16_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.FixedRewardItemList.entries[].ItemId | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_List_0.entries[].unk_u8_1` | 2 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative |
| S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | `packet.UpdateItemList.entries[].ItemInfo.unk_ElementList.entries[].unk_u16` | 2 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative |
| S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | `packet.UpdateItemList.entries[].ItemInfo.unk_ElementList.entries[].unk_u8` | 2 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u16` | 5 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 3/3 | 1/1 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u8` | 4 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 3/3 | 1/1 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_1` | 2 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestOrderConditionParamList.entries[].Param01 | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_0` | 2 (0) | all-nonbinary | S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC:packet.m_PlayerInfo.m_unActNo | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_1` | 3 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 2/2 | 1/1 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_List_1.entries[].unk_u8_0` | 3 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 3/3 | 1/1 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_List_1.entries[].unk_u8_1` | 2 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 2/2 | 1/1 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_List.entries[].unk_u32_1` | 1 (1) | informative | L2C_GP_COURSE_GET_INFO_RES:packet.Effects.entries[].Param0 | 1/1 | 1/1 | constant,lt3-distinct,few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_List.entries[].unk_u32_2` | 1 (1) | informative | L2C_GET_CHARACTER_LIST_RES:packet.CharacterList.entries[].EditInfo.VoicePitch | 1/1 | 1/1 | constant,lt3-distinct,few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_List.entries[].unk_u32_3` | 3 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 2/2 | 1/1 | small-enum,few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_List.entries[].unk_u32_4` | 4 (1) | informative | L2C_GP_COURSE_GET_INFO_RES:packet.Effects.entries[].Param0 | 1/1 | 1/1 | few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_PawnList.entries[].unk_Name.value` | 2 (2) | informative | S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES:packet.Items.entries[].Name.value | 2/2 | 1/1 | lt3-distinct,few-informative |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_PawnList.entries[].unk_u32_3` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_PawnList.entries[].unk_u8` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestOrderConditionParamList.entries[].Param01 | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u16` | 13 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 12/12 | 1/1 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u16` | 2 (0) | all-nonbinary | C2S_PROFILE_SET_SHORTCUT_LIST_REQ:packet.ShortcutList.entries[].ShortcutID | 2/2 | 1/1 | small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_1` | 1 (0) | all-nonbinary | S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC:packet.m_PlayerInfo.m_unActNo | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_1` | 2 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 1/1 | 1/1 | small-enum,lt3-distinct,few-informative |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_0` | 1 (1) | informative | S2C_AREA_GET_AREA_BASE_INFO_LIST_RES:packet.AreaBaseInfoList.entries[].ClanAreaPointBorder | 1/1 | 1/1 | constant,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_2` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_3` | 1 (0) | all-nonbinary | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestLayoutFlagSetInfoList.entries[].SetInfoList.entries[].GroupId | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_4` | 1 (0) | all-nonbinary | L2C_GP_COURSE_GET_INFO_RES:packet.Effects.entries[].Param0 | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Detail.unk_u32_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_QUEST_COMPLETE_LIST_RES:packet.QuestIdList.entries[].QuestId | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Detail.unk_u32_6` | 1 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative |
| S2C_QUEST_GET_MAIN_QUEST_LIST_RES | `packet.MainQuestList.entries[].unk_u64` | 2 (1) | informative | (timestamp epoch_s, capture time -10 y/+2 y) | 1/1 | 1/1 | lt3-distinct,few-informative |
| S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES | `packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestLog.QuestTalkInfoList.entries[].unk_u32` | 2 (1) | informative | S2C_QUEST_SET_PRIORITY_QUEST_NTC:packet.PriorityQuestList.entries[].QuestId | 1/1 | 1/1 | lt3-distinct,few-informative |
| S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES | `packet.PartyQuestProgressInfo.QuestOrderList.entries[].unk_u64` | 2 (1) | informative | (timestamp epoch_s, capture time -10 y/+2 y) | 1/1 | 1/1 | lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_INFO_LIST_RES | `packet.SetQuestInfoList.entries[].DeliveryItemList.entries[].unk_u16_1` | 1 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 1/1 | 1/1 | constant,small-enum,lt3-distinct,few-informative,global-values |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_s64_0` | 2 (1) | informative | (timestamp epoch_s, capture time -10 y/+2 y) | 1/1 | 1/1 | lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_s64_1` | 2 (1) | informative | (timestamp epoch_s, capture time -10 y/+2 y) | 1/1 | 1/1 | lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_4` | 4 (1) | informative | S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC:packet.m_Base.m_ContextEquipVisualList[].m_usItemID | 1/1 | 1/1 | few-informative,global-values |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_s64_0` | 2 (1) | informative | (timestamp epoch_s, capture time -10 y/+2 y) | 1/1 | 1/1 | lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_s64_1` | 2 (1) | informative | (timestamp epoch_s, capture time -10 y/+2 y) | 1/1 | 1/1 | lt3-distinct,few-informative |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List0.entries[].unk_u32_2` | 4 (0) | all-nonbinary | C2S_PARTY_SEND_BINARY_MSG_NTC:packet.Data.ctrlAction.mEnemyStatusCtrl.mEnemyBitCtrlCollision | 2/2 | 1/1 | small-enum,few-informative |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List1.entries[].unk_u32` | 1 (1) | informative | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.WorldManageQuestOrderList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param01 | 1/1 | 1/1 | constant,lt3-distinct,few-informative,global-values |
| S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES | `packet.DispelBaseItemList.entries[].unk_u32` | 97 (97) | informative | C2S_LOBBY_LOBBY_DATA_MSG_REQ:packet.Data.msg.ctrlAction.mCondition.mStamina | 96/97 | 1/1 | dense-reference |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_List_1.entries[].unk_u8_0` | 6 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestOrderConditionParamList.entries[].Param01 | 70/71 | 27/27 | small-enum,few-informative,global-values |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_1` | 3 (0) | all-nonbinary | S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES:packet.TutorialQuestList.entries[].Param.QuestProcessStateList.entries[].CheckCommandList.entries[].entries[].Param02 | 17/18 | 16/16 | small-enum,few-informative,global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_List_1.entries[].unk_u8` | 17 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 336/357 | 21/21 | few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_1.entries[].unk_u8` | 17 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 320/340 | 20/20 | few-informative,global-values |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.unk_List.entries[].unk_u8` | 17 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 320/340 | 20/20 | few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_1.entries[].unk_u8` | 17 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 320/340 | 20/20 | few-informative,global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_List_0.entries[].unk_u8` | 17 (0) | all-nonbinary | S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC:packet.MainQuestIdList.entries[].QuestId | 320/340 | 20/20 | few-informative,global-values |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_u8` | 6 (0) | all-nonbinary | L2C_GP_COURSE_GET_INFO_RES:packet.Effects.entries[].EffectUID | 18/20 | 16/16 | small-enum,few-informative,global-values,dense-reference |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_u8[]` | 16 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 240/280 | 20/20 | small-enum,few-informative,global-values |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List0.entries[].unk_u32_1` | 14 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 11/14 | 1/1 | small-enum,few-informative,global-values |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.unk_u8[]` | 19 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 13/17 | 1/1 | few-informative,global-values |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_List_1.entries[].unk_List.entries[].unk_u8` | 120 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 3608/4879 | 41/41 | few-informative,global-values |
| S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | `packet.TutorialQuestList.entries[].Param.unk_u32_list.entries[]` | 17 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 204/287 | 41/41 | few-informative,global-values |
| C2S_LOBBY_LOBBY_CHAT_MSG_REQ | `packet.unk_u32_1` | 53 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 34/51 | 1/1 | few-informative,global-values |
| S2C_LOBBY_LOBBY_CHAT_MSG_NTC | `packet.unk_u32_1` | 53 (0) | all-nonbinary | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 34/51 | 1/1 | few-informative,global-values |
| S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES | `packet.unk_list_1.entries[].unk_u32` | 4 (4) | informative | S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES:packet.ReleaseAreaInfoSetList.entries[].ReleaseList.entries[].m_unValue | 62/103 | 21/41 | global-values,dense-reference |
| S2C_AREA_GET_SPOT_INFO_LIST_RES | `packet.unk_list_1.entries[].unk_u32` | 4 (4) | informative | S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES:packet.ReleaseAreaInfoSetList.entries[].ReleaseList.entries[].m_unValue | 62/104 | 21/26 | global-values,dense-reference |
| S2C_PAWN_GET_MYPAWN_LIST_RES | `packet.PawnList.entries[].unk_u32_1` | 3 (2) | informative | L2C_GET_CHARACTER_LIST_RES:packet.CharacterList.entries[].EditInfo.VoicePitch | 21/41 | 21/21 | few-informative,global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_PawnList.entries[].unk_u32_0` | 2 (2) | informative | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].BaseExp.entries[].Value | 1/2 | 1/1 | lt3-distinct,few-informative,global-values |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_List_0.entries[].unk_u16_0` | 8 (7) | informative | S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES:packet.ReleaseAreaInfoSetList.entries[].ReleaseList.entries[].m_unValue | 60/121 | 20/21 | global-values,dense-reference |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_3` | 12 (7) | informative | S2C_SHOP_GET_SHOP_GOODS_LIST_RES:packet.GoodsParamList.entries[].Price | 3/7 | 0/1 |  |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_List_0.entries[].unk_u16_0` | 16 (12) | informative | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 5/12 | 1/3 | global-values |
| S2C_QUEST_FORT_DEFENSE_NTC | `packet.SituationInfoDetailList.entries[].unk_u32_u32_list.entries[].unk_u32_1` | 36 (29) | informative | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 288/696 | 0/24 | global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_List[].unk_u16_0` | 198 (142) | informative | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 127/315 | 10/30 | global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.unk_List[].unk_u16` | 43 (3) | informative | S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES:packet.PartyQuestProgressInfo.QuestOrderList.entries[].BaseGold.entries[].Value | 2/5 | 2/5 | global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u32_0` | 16 (8) | informative | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 60/160 | 0/20 | global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipVisualList[].unk_List[].unk_u16_0` | 59 (43) | informative | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 19/51 | 7/17 | global-values |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_List_0.entries[].unk_u32_1` | 9 (4) | informative | S2C_CHARACTER_DECIDE_CHARACTER_ID_RES:packet.CharacterInfo.WalletPointList.entries[].Value | 58/164 | 19/41 | global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_0` | 3 (3) | informative | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 20/60 | 0/20 | global-values |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_List.entries[].unk_u32_0` | 7 (6) | informative | L2C_GET_ERROR_MESSAGE_LIST_NTC:packet.ErrorMessage.entries[].ErrorID | 2/6 | 0/1 | global-values |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_0` | 6 (4) | informative | S2C_ITEM_GET_STORAGE_ITEM_LIST_RES:packet.ItemList.entries[].ItemId | 3/10 | 0/4 | global-values |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_List_0.entries[].unk_u16_0` | 20 (17) | informative | S2C_STAGE_GET_STAGE_LIST_RES:packet.StageInfoList.entries[].StageNo | 63/264 | 1/21 | global-values |

## Unexplained by correlation

No named field of the same session holds their values at share >= 0.2 (mostly constants, 0/1 flags and small enums).

| Packet | Key path | Declared | Distinct | Range | Flags |
| --- | --- | --- | --- | --- | --- |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_List_1.entries[].unk_List.entries[].unk_u32` | `include/Server.hexpat` CDataGameSetting_unk_2 | 173 | 0..226000000 | global-values |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_0` | `include/Shop.hexpat` CDataGoodsRequirement | 29 | 16..5034 | global-values |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.unk_u32x5.unk_u32_0` | `include/Pawn.hexpat` CDataPawnInfo_unk_0 | 3 | 0..30000 | few-informative,global-values |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 19 | 1054..23638 | global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipVisualList[].unk_ElementList[].unk_u32` | `include/Context.hexpat` EquipElementParam | 72 | 9196..25716 | global-values |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_u32` | `include/Shop.hexpat` CDataGoodsParam | 47 | 17073..25707 | global-values |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 61 | 1053..25750 | global-values,dense-reference |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 6 | 1054..22965 |  |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 80 | 1054..23708 | global-values |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_ElementList[].unk_u32` | `include/Context.hexpat` EquipElementParam | 509 | 1053..25763 | global-values,dense-reference |
| C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC | `packet.unk_zero` | `C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC-pattern.cpp` C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC | `packet.unk_zero` | `C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC-pattern.cpp` C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_INSTANCE_ENEMY_KILL_REQ | `packet.unk_bool` | `C2S_INSTANCE_ENEMY_KILL_REQ-pattern.cpp` C2S_INSTANCE_ENEMY_KILL_REQ | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| C2S_INSTANCE_GET_DROP_ITEM_REQ | `packet.unk_bool` | `C2S_INSTANCE_GET_DROP_ITEM_REQ-pattern.cpp` C2S_INSTANCE_GET_DROP_ITEM_REQ | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_INSTANCE_GET_GATHERING_ITEM_REQ | `packet.unk_bool` | `C2S_INSTANCE_GET_GATHERING_ITEM_REQ-pattern.cpp` C2S_INSTANCE_GET_GATHERING_ITEM_REQ | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_INSTANCE_GET_GATHERING_ITEM_REQ | `packet.unk_u32` | `C2S_INSTANCE_GET_GATHERING_ITEM_REQ-pattern.cpp` C2S_INSTANCE_GET_GATHERING_ITEM_REQ | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ | `packet.unk_bool` | `C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ-pattern.cpp` C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| C2S_PARTY_SEND_BINARY_MSG_NTC | `packet.Data.ctrlAction.unk_0x3C[]` | `C2S_PARTY_SEND_BINARY_MSG_NTC-pattern.cpp` C2S_PARTY_SEND_BINARY_MSG_NTC | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_BOX_GACHA_BOX_GACHA_LIST_RES | `packet.BoxGachaList.entries[].SettlementList.entries[].unk_u32` | `S2C_BOX_GACHA_BOX_GACHA_LIST_RES-pattern.cpp` CDataBoxGachaSettlementInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_BOX_GACHA_BOX_GACHA_LIST_RES | `packet.BoxGachaList.entries[].unk_bool` | `S2C_BOX_GACHA_BOX_GACHA_LIST_RES-pattern.cpp` CDataBoxGachaInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.unk_u8` | `S2C_CHARACTER_DECIDE_CHARACTER_ID_RES-pattern.cpp` S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES | `packet.DispelBaseItemList.entries[].LotItemList.entries[].ItemLot.unk_bool` | `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES-pattern.cpp` CDataDispelLotItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES | `packet.DispelBaseItemList.entries[].unk_u16_0` | `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES-pattern.cpp` CDataDispelBaseItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES | `packet.DispelBaseItemList.entries[].unk_u16_1` | `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES-pattern.cpp` CDataDispelBaseItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES | `packet.unk_bool` | `S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES-pattern.cpp` S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES | `packet.unk_serverListCount` | `S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES-pattern.cpp` S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES | `packet.unk_bool` | `S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES-pattern.cpp` S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_LOBBY_LOBBY_CHAT_MSG_NTC | `packet.unk_u32_0` | `S2C_LOBBY_LOBBY_CHAT_MSG_NTC-pattern.cpp` S2C_LOBBY_LOBBY_CHAT_MSG_NTC | 6 | 0..31261998 | few-informative |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_s64` | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragora | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_state.unk_s64` | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragoraUnkState | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_state.unk_u32_1` | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragoraUnkState | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_u32_0` | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragora | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_u32_1` | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragora | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.MandragoraList.entries[].unk_u8` | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragora | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES | `packet.unk_list_3.entries[].unk_u32` | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragoraUnkU8U32 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_MY_ROOM_FURNITURE_LIST_GET_RES | `packet.MyRoomOption.unk_u32` | `S2C_MY_ROOM_FURNITURE_LIST_GET_RES-pattern.cpp` CDataMyRoomOption | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_RES | `packet.unk_bool` | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_RES-pattern.cpp` S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_RES | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_QUEST_PLAY_END_NTC | `packet.unk_s32` | `S2C_QUEST_PLAY_END_NTC-pattern.cpp` S2C_QUEST_PLAY_END_NTC | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.unk_u8_0` | `S2C_SHOP_GET_SHOP_GOODS_LIST_RES-pattern.cpp` S2C_SHOP_GET_SHOP_GOODS_LIST_RES | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_STAGE_GET_STAGE_LIST_RES | `packet.StageInfoList.entries[].StageAttribute.unk_bool_0` | `S2C_STAGE_GET_STAGE_LIST_RES-pattern.cpp` CDataStageAttribute | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_STAGE_GET_STAGE_LIST_RES | `packet.StageInfoList.entries[].StageAttribute.unk_bool_1` | `S2C_STAGE_GET_STAGE_LIST_RES-pattern.cpp` CDataStageAttribute | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_STAMP_BONUS_GET_LIST_RES | `packet.StampBonusTotal.entries[].StampBonus.entries[].unk_u32` | `S2C_STAMP_BONUS_GET_LIST_RES-pattern.cpp` S2C_STAMP_BONUS_GET_LIST_RES | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES | `packet.unk_list_1.entries[].unk_bool` | `include/Area.hexpat` CDataAreaUnkU32BoolS64 | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_AREA_GET_SPOT_INFO_LIST_RES | `packet.unk_list_1.entries[].unk_bool` | `include/Area.hexpat` CDataAreaUnkU32BoolS64 | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC | `packet.UpdateCharacterList.entries[].unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_GET_MY_INFO_RES | `packet.CreateParam.ClanServerParam.MasterInfo.CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES | `packet.MemberList.entries[].CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NTC | `packet.MemberData.CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES | `packet.EntryItem.EntryMemberList.entries[].CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES | `packet.EntryItemList.entries[].EntryMemberList.entries[].CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_FRIEND_GET_FRIEND_LIST_RES | `packet.FriendInfoList.entries[].CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_LOBBY_LOBBY_JOIN_RES | `packet.LobbyMemberInfoList.entries[].unk_u8` | `include/Character.hexpat` CDataLobbyMemberInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PARTY_PARTY_JOIN_NTC | `packet.PartyMember.entries[].CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_JOIN_PARTY_PAWN_NTC | `packet.PartyMember.CharacterListElement.unk_u8` | `include/Character.hexpat` CDataCharacterListElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ | `packet.m_Data.bitStream.mOption.unk_bit_09` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ | `packet.m_Data.bitStream.mOption.unk_bit_96` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ | `packet.m_Data.bitStream.mOption.unk_bit_97` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ | `packet.m_Data.bitStream.mOption.unk_bit_98` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ | `packet.m_Data.bitStream.mOption.unk_u8_37` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ | `packet.m_Data.bitStream.unk_bit_13637` | `include/CharacterData.hexpat` CharacterBinSaveData | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.Bin.bitStream.mOption.unk_bit_09` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.Bin.bitStream.mOption.unk_bit_96` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.Bin.bitStream.mOption.unk_bit_97` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.Bin.bitStream.mOption.unk_bit_98` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.Bin.bitStream.mOption.unk_u8_37` | `include/CharacterData.hexpat` CharacterBinSaveData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.Bin.bitStream.unk_bit_13637` | `include/CharacterData.hexpat` CharacterBinSaveData | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| C2S_CONTEXT_GET_SET_CONTEXT_REQ | `packet.m_Base.unk_u32` | `include/Context.hexpat` CDataContextSetBase | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_CONTEXT_SET_CONTEXT_NTC | `packet.m_SetInfo.m_Additional.unk_u32[]` | `include/Context.hexpat` CDataContextSetAdditional | 9 | 0..4178097349 |  |
| C2S_CONTEXT_SET_CONTEXT_NTC | `packet.m_SetInfo.m_Base.unk_u32` | `include/Context.hexpat` CDataContextSetBase | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 17 | 1054..23638 | dense-reference |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 13 | 1054..23638 | dense-reference |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u16` | `include/Context.hexpat` EquipElementParam | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 1 | 9318..9318 | constant,lt3-distinct,few-informative,dense-reference |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u8` | `include/Context.hexpat` EquipElementParam | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 21 | 1054..23641 | dense-reference |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u16` | `include/Context.hexpat` EquipElementParam | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 2 | 9255..9290 | lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_Base.m_ContextEquipVisualList[].unk_List[].unk_u16_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 23 | 1..3184 | few-informative,dense-reference |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_PlayerInfo.unk_u32_0` | `include/Context.hexpat` CDataContextPlayerInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC | `packet.m_PlayerInfo.unk_u32_1` | `include/Context.hexpat` CDataContextPlayerInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_ElementList[].unk_u16` | `include/Context.hexpat` EquipElementParam | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_Base.m_ContextEquipPerformanceList[].unk_ElementList[].unk_u8` | `include/Context.hexpat` EquipElementParam | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_PawnInfo.unk_u8[]` | `include/Context.hexpat` CDataContextPawnInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_PlayerInfo.unk_u32_0` | `include/Context.hexpat` CDataContextPlayerInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC | `packet.m_PlayerInfo.unk_u32_1` | `include/Context.hexpat` CDataContextPlayerInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_SET_CONTEXT_BASE_NTC | `packet.m_Base.unk_u32` | `include/Context.hexpat` CDataContextSetBase | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CONTEXT_SET_CONTEXT_NTC | `packet.m_SetInfo.m_Additional.unk_u32[]` | `include/Context.hexpat` CDataContextSetAdditional | 8 | 45416..4178097349 |  |
| S2C_CONTEXT_SET_CONTEXT_NTC | `packet.m_SetInfo.m_Base.unk_u32` | `include/Context.hexpat` CDataContextSetBase | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_ElementList.entries[].unk_u16` | `include/Context.hexpat` EquipElementParam | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 2 | 9197..16065 | lt3-distinct,few-informative,dense-reference |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_List_0.entries[].unk_u8_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_List_0.entries[].unk_u8_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | `packet.UpdateItemList.entries[].ItemInfo.unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 2 | 23705..23706 | lt3-distinct,few-informative |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_List_0.entries[].unk_u8_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_List_0.entries[].unk_u8_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u16` | `include/Context.hexpat` EquipElementParam | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u8` | `include/Context.hexpat` EquipElementParam | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u16_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_0` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_List_0.entries[].unk_u8_1` | `include/Context.hexpat` CDataContextEquipData_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_ElementList.entries[].unk_u32` | `include/Context.hexpat` EquipElementParam | 9 | 11720..24721 | dense-reference |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_List.entries[].unk_bool` | `include/Craft.hexpat` CDataCraftSettingUnkElement | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_PawnList.entries[].unk_u32_1` | `include/Craft.hexpat` CDataCraftSettingUnkPawn | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CRAFT_GET_CRAFT_SETTING_RES | `packet.unk_PawnList.entries[].unk_u32_2` | `include/Craft.hexpat` CDataCraftSettingUnkPawn | 2 | 10000002..10000006 | lt3-distinct,few-informative |
| S2C_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES | `packet.RecipeList.entries[].CraftMaterialList.entries[].unk_bool` | `include/Craft.hexpat` CDataMDataCraftMaterial | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_REQ | `packet.Param.EntryRecruitList.entries[].unk_u32` | `include/EntryBoard.hexpat` CDataEntryRecruitData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_REQ | `packet.SearchParam.unk_u32_0` | `include/EntryBoard.hexpat` CDataEntryBoardItemSearchParameter | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_REQ | `packet.SearchParam.unk_u32_1` | `include/EntryBoard.hexpat` CDataEntryBoardItemSearchParameter | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NTC | `packet.MemberData.unk_u32` | `include/EntryBoard.hexpat` CDataEntryMemberData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES | `packet.EntryItem.EntryMemberList.entries[].unk_u32` | `include/EntryBoard.hexpat` CDataEntryMemberData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES | `packet.EntryItem.Param.EntryRecruitList.entries[].unk_u32` | `include/EntryBoard.hexpat` CDataEntryRecruitData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES | `packet.EntryItem.unk_bool` | `include/EntryBoard.hexpat` CDataEntryItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES | `packet.EntryItemList.entries[].EntryMemberList.entries[].unk_u32` | `include/EntryBoard.hexpat` CDataEntryMemberData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES | `packet.EntryItemList.entries[].Param.EntryRecruitList.entries[].unk_u32` | `include/EntryBoard.hexpat` CDataEntryRecruitData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES | `packet.EntryItemList.entries[].unk_bool` | `include/EntryBoard.hexpat` CDataEntryItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].GpCourseValidList.entries[].unk_MtString.value` | `include/GP.hexpat` CDataGPCourseValid | 2 | .. | lt3-distinct,few-informative |
| S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES | `packet.Items.entries[].unk_MtString.value` | `include/GP.hexpat` CDataGPShopDisplayLineup | 35 | .. |  |
| S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES | `packet.Items.entries[].unk_u32_1` | `include/GP.hexpat` CDataGPShopDisplayLineup | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES | `packet.Items.entries[].unk_u32_2` | `include/GP.hexpat` CDataGPShopDisplayLineup | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES | `packet.Items.entries[].unk_u32_3` | `include/GP.hexpat` CDataGPShopDisplayLineup | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_GACHA_GACHA_LIST_RES | `packet.GachaList.entries[].DrawGroups.entries[].GachaSettlementList.entries[].unk_u32` | `include/Gacha.hexpat` CDataGachaSettlementInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_INSTANCE_ENEMY_REPOP_NTC | `packet.EnemyData.EnemyInfo.unk_bool` | `include/Instance.hexpat` CDataStageLayoutEnemyPresetEnemyInfoClient | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_INSTANCE_GET_DROP_ITEM_LIST_RES | `packet.ItemList.entries[].unk_bool` | `include/Instance.hexpat` CDataGatheringItemElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_INSTANCE_GET_DROP_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u32` | `include/Instance.hexpat` CDataGatheringItemElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_INSTANCE_GET_ENEMY_SET_LIST_RES | `packet.EnemyList.entries[].EnemyInfo.unk_bool` | `include/Instance.hexpat` CDataStageLayoutEnemyPresetEnemyInfoClient | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES | `packet.ItemList.entries[].unk_bool` | `include/Instance.hexpat` CDataGatheringItemElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u32` | `include/Instance.hexpat` CDataGatheringItemElement | 3 | 0..116255 | few-informative |
| S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_RES | `packet.GatheringItemList.entries[].unk_bool` | `include/Instance.hexpat` CDataGatheringItemElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_RES | `packet.GatheringItemList.entries[].unk_u32` | `include/Instance.hexpat` CDataGatheringItemElement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_GET_POST_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u32_0` | `include/Item.hexpat` CDataItemList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_GET_POST_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u32_1` | `include/Item.hexpat` CDataItemList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_GET_POST_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u32_2` | `include/Item.hexpat` CDataItemList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_GET_POST_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u8` | `include/Item.hexpat` CDataItemList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_GET_STORAGE_ITEM_LIST_RES | `packet.ItemList.entries[].unk_u8` | `include/Item.hexpat` CDataItemList | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | `packet.UpdateItemList.entries[].ItemInfo.unk_u32_0` | `include/Item.hexpat` CDataItemList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | `packet.UpdateItemList.entries[].ItemInfo.unk_u32_2` | `include/Item.hexpat` CDataItemList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC | `packet.UpdateItemList.entries[].ItemInfo.unk_u8` | `include/Item.hexpat` CDataItemList | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| L2C_GET_CHARACTER_LIST_RES | `packet.CharacterList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_1` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CHARACTER_DECIDE_CHARACTER_ID_RES | `packet.CharacterInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_1` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_1` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.EquipItemList.entries[].unk_u8_1` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | `packet.VisualEquipItemList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_JOB_GET_JOB_CHANGE_LIST_RES | `packet.JobChangeInfo.entries[].EquipItemList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_1` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_MYPAWN_DATA_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipDataList.entries[].EquipList.entries[].unk_u8_1` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_PAWN_GET_RENTED_PAWN_DATA_RES | `packet.PawnInfo.CharacterEquipViewDataList.entries[].EquipList.entries[].unk_u8_0` | `include/Login.hexpat` CDataEquipItemInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_FORT_DEFENSE_NTC | `packet.FortDefenseNoticeDataList.entries[].Common.unk_u64` | `include/Quest.hexpat` CDataCycleContentsNoticeData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES | `packet.CycleContentsNewsList.entries[].EnemyInfo.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].Param.QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].Param.unk_u64` | `include/Quest.hexpat` CDataQuestList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_Struct_0.unk_bool_0` | `include/Quest.hexpat` CDataTimeGainQuestList_unk_0 | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_Struct_0.unk_bool_1` | `include/Quest.hexpat` CDataTimeGainQuestList_unk_0 | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_Struct_0.unk_u32` | `include/Quest.hexpat` CDataTimeGainQuestList_unk_0 | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_bool_0` | `include/Quest.hexpat` CDataTimeGainQuestList | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_bool_1` | `include/Quest.hexpat` CDataTimeGainQuestList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_bool_2` | `include/Quest.hexpat` CDataTimeGainQuestList | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_bool_3` | `include/Quest.hexpat` CDataTimeGainQuestList | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_END_CONTENTS_GROUP_RES | `packet.TimeGainQuestList.entries[].unk_bool_4` | `include/Quest.hexpat` CDataTimeGainQuestList | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Contents.unk_u16_0` | `include/Quest.hexpat` CDataQuestContents | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Contents.unk_u16_1` | `include/Quest.hexpat` CDataQuestContents | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Detail.unk_u32_0` | `include/Quest.hexpat` CDataLightQuestDetail | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Detail.unk_u32_2` | `include/Quest.hexpat` CDataLightQuestDetail | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Detail.unk_u32_3` | `include/Quest.hexpat` CDataLightQuestDetail | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Detail.unk_u32_4` | `include/Quest.hexpat` CDataLightQuestDetail | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Detail.unk_u32_5` | `include/Quest.hexpat` CDataLightQuestDetail | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Param.BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LIGHT_QUEST_LIST_RES | `packet.LightQuestList.entries[].Param.unk_u64` | `include/Quest.hexpat` CDataQuestList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LOT_QUEST_LIST_RES | `packet.LotQuestList.entries[].Contents.unk_u16_0` | `include/Quest.hexpat` CDataQuestContents | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LOT_QUEST_LIST_RES | `packet.LotQuestList.entries[].Contents.unk_u16_1` | `include/Quest.hexpat` CDataQuestContents | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LOT_QUEST_LIST_RES | `packet.LotQuestList.entries[].Param.BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LOT_QUEST_LIST_RES | `packet.LotQuestList.entries[].Param.DeliveryItemList.entries[].unk_u16_0` | `include/Quest.hexpat` CDataQuestDeliveryItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LOT_QUEST_LIST_RES | `packet.LotQuestList.entries[].Param.DeliveryItemList.entries[].unk_u16_1` | `include/Quest.hexpat` CDataQuestDeliveryItem | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_LOT_QUEST_LIST_RES | `packet.LotQuestList.entries[].Param.unk_u64` | `include/Quest.hexpat` CDataQuestList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_MAIN_QUEST_LIST_RES | `packet.MainQuestList.entries[].BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_MAIN_QUEST_LIST_RES | `packet.MainQuestList.entries[].QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_MAIN_QUEST_LIST_RES | `packet.MainQuestList.entries[].QuestLog.QuestTalkInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestTalkInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES | `packet.PartyQuestProgressInfo.QuestOrderList.entries[].BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES | `packet.PartyQuestProgressInfo.QuestOrderList.entries[].DeliveryItemArray.entries[].unk_u16_0` | `include/Quest.hexpat` CDataQuestDeliveryItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES | `packet.PartyQuestProgressInfo.QuestOrderList.entries[].QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_INFO_LIST_RES | `packet.SetQuestInfoList.entries[].DeliveryItemList.entries[].unk_u16_0` | `include/Quest.hexpat` CDataQuestDeliveryItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_INFO_LIST_RES | `packet.SetQuestInfoList.entries[].QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_INFO_LIST_RES | `packet.SetQuestInfoList.entries[].unk_u64` | `include/Quest.hexpat` CDataSetQuestInfoList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Detail.unk_quest_exp_list.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Detail.unk_u16_0` | `include/Quest.hexpat` CDataSetQuestDetail | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Param.BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Param.DeliveryItemList.entries[].unk_u16_0` | `include/Quest.hexpat` CDataQuestDeliveryItem | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Param.QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Param.QuestLog.QuestTalkInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestTalkInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_SET_QUEST_LIST_RES | `packet.SetQuestList.entries[].Param.unk_u64` | `include/Quest.hexpat` CDataQuestList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | `packet.TutorialQuestList.entries[].Param.BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | `packet.TutorialQuestList.entries[].Param.QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES | `packet.TutorialQuestList.entries[].Param.QuestLog.QuestTalkInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestTalkInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.TutorialQuestOrderList.entries[].Param.BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.TutorialQuestOrderList.entries[].Param.QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.WorldManageQuestOrderList.entries[].Param.unk_u64` | `include/Quest.hexpat` CDataQuestOrderList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.unk_order_list_7.entries[].Param.BaseExp.entries[].unk_u8` | `include/Quest.hexpat` CDataQuestExp | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.unk_order_list_7.entries[].Param.QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 6 | 3058..3090 | dense-reference |
| S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC | `packet.unk_order_list_7.entries[].Param.unk_u64` | `include/Quest.hexpat` CDataQuestOrderList | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_PLAY_END_NTC | `packet.ContentsPlayEnd.unk_u32_0` | `include/Quest.hexpat` CDataContentsPlayEnd | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_PLAY_END_NTC | `packet.ContentsPlayEnd.unk_u32_1` | `include/Quest.hexpat` CDataContentsPlayEnd | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_PLAY_END_NTC | `packet.ContentsPlayEnd.unk_u32_2` | `include/Quest.hexpat` CDataContentsPlayEnd | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC | `packet.PlayStartData.QuestEnemyInfoList.entries[].unk_u32` | `include/Quest.hexpat` CDataQuestEnemyInfo | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC | `packet.PlayStartData.unk_bool_0` | `include/Quest.hexpat` CDataContentsPlayStartData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC | `packet.PlayStartData.unk_bool_1` | `include/Quest.hexpat` CDataContentsPlayStartData | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC | `packet.PlayStartData.unk_bool_2` | `include/Quest.hexpat` CDataContentsPlayStartData | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_bool` | `include/Server.hexpat` CDataGameSetting | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_SERVER_GET_GAME_SETTING_RES | `packet.GameSetting.unk_u32_0` | `include/Server.hexpat` CDataGameSetting | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_bool_0` | `include/Shop.hexpat` CDataGoodsRequirement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_bool_1` | `include/Shop.hexpat` CDataGoodsRequirement | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_2` | `include/Shop.hexpat` CDataGoodsRequirement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_6` | `include/Shop.hexpat` CDataGoodsRequirement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_RequirementList.entries[].unk_u32_7` | `include/Shop.hexpat` CDataGoodsRequirement | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_SHOP_GET_SHOP_GOODS_LIST_RES | `packet.GoodsParamList.entries[].unk_bool` | `include/Shop.hexpat` CDataGoodsParam | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List0.entries[].unk_u8_0` | `include/Stage.hexpat` CDataAreaChangeUnk0 | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List0.entries[].unk_u8_1` | `include/Stage.hexpat` CDataAreaChangeUnk0 | 2 | 0..1 | 0-1,lt3-distinct,few-informative |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List1.entries[].unk_bool_0` | `include/Stage.hexpat` CDataAreaChangeUnk1 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_STAGE_AREA_CHANGE_RES | `packet.unk_List1.entries[].unk_bool_1` | `include/Stage.hexpat` CDataAreaChangeUnk1 | 1 | 0..0 | constant,0-1,lt3-distinct,few-informative |
| S2C_STAMP_BONUS_CHECK_RES | `packet.unk_List.entries[].unk_u32_0` | `include/Stamp.hexpat` CDataStampBonusCheckRes_unk_0 | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_STAMP_BONUS_GET_LIST_RES | `packet.DailyGroupList.entries[].StampBonusDaily.entries[].StampBonus.entries[].unk_u32` | `include/Stamp.hexpat` CDataStampBonus | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |
| S2C_STAMP_BONUS_GET_LIST_RES | `packet.DailyGroupList.entries[].unk_u32_0` | `include/Stamp.hexpat` CDataStampBonusDailyGroup | 1 | 1..1 | constant,0-1,lt3-distinct,few-informative |

## Declared unknowns without data

Value-bearing `unk_*` declarations that no exported JSON file holds (packet not captured, branch not taken, or a path the resolver could not follow).

- `S2C_AREA_GET_SPOT_INFO_LIST_RES-pattern.cpp` S2C_AREA_GET_SPOT_INFO_LIST_RES.unk_list_2
- `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES-pattern.cpp` CDataDispelLotCrest.unk_u8_0
- `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES-pattern.cpp` CDataDispelLotCrest.unk_u8_1
- `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES-pattern.cpp` CDataDispelLotCrestUnk.unk_u16
- `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES-pattern.cpp` CDataDispelLotCrestUnk.unk_u8
- `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragoraUnkItem.unk_u16
- `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES-pattern.cpp` CDataMyMandragoraUnkItem.unk_u32
- `S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES-pattern.cpp` CDataCycleContentsUnk.unk_s64_0
- `S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES-pattern.cpp` CDataCycleContentsUnk.unk_s64_1
- `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC-pattern.cpp` CDataQuestJoinLobbyUnk.unk_u32
- `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC-pattern.cpp` CDataQuestJoinLobbyUnkElement.unk_bool
- `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC-pattern.cpp` CDataQuestJoinLobbyUnkElement.unk_s32_0
- `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC-pattern.cpp` CDataQuestJoinLobbyUnkElement.unk_s32_1
- `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC-pattern.cpp` CDataQuestJoinLobbyUnkElement.unk_u32
- `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC-pattern.cpp` CDataQuestJoinLobbyUnkElement.unk_u32_list
- `include/Context.hexpat` CDataContextEnemyStatus.unk_u32
- `include/Craft.hexpat` CDataCraftProgress.unk_u16
- `include/Craft.hexpat` CDataCraftProgress.unk_u32_list
- `include/Instance.hexpat` GatheringItemListRes_unk_0.unk_u32
- `include/Instance.hexpat` GatheringItemListRes_unk_1.unk_u16
- `include/Instance.hexpat` GatheringItemListRes_unk_1.unk_u32
- `include/Quest.hexpat` CDataContentsPlayStartData.unk_u8_list
- `include/Quest.hexpat` CDataQuestUnkU32Bool.unk_bool
- `include/Quest.hexpat` CDataQuestUnkU32Bool.unk_u32
- `include/Quest.hexpat` CDataQuestUnkU32S64.unk_s64
- `include/Quest.hexpat` CDataQuestUnkU32S64.unk_u32
- `include/Quest.hexpat` CDataQuestUnkU32U16.unk_u16
- `include/Quest.hexpat` CDataQuestUnkU32U16.unk_u32
- `include/Quest.hexpat` CDataTimeGainQuestList_unk_0.unk_u32_list
- `include/Quest.hexpat` CDataTimeGainQuestList_unk_0.unk_u8_list
- `include/nNetMsg.hexpat` CtrlAction.unk_0x3C
- `include/nNetMsg.hexpat` CtrlAction.unk_0x3D
- `include/nNetMsg.hexpat` GameNormal.unk_u32
- `include/nNetMsg.hexpat` GameNormal.unk_uid_0
- `include/nNetMsg.hexpat` GameNormal.unk_uid_1
