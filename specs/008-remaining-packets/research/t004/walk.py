"""008 T004: independent stdlib walk of batches B1 and B4 (client 03040008).

usage (from D:/ddon-data):
  python -X utf8 -I specs/008-remaining-packets/research/t004/walk.py stats [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t004/walk.py check [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t004/walk.py fits [id ...]
  python -X utf8 -I specs/008-remaining-packets/research/t004/walk.py dump <id> [n]

The decoder, the fit rule (ends within the last 15 bytes) and the three modes are T003's
(`../t003/walk.py`, loaded by path); this file only supplies the B1/B4 layouts: the PC
reader/writer width sequences of T001-triage.tsv with the pattern's field names, so `check`
compares the exported JSON leaf by leaf. `dump` prints the decoded tree of the first n files.
"""
import importlib.util
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("t003walk", os.path.join(_here, "..", "t003", "walk.py"))
W = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W)
L, S, LU32, RES = W.L, W.S, W.LU32, W.RES

LAYOUT_ID = [("StageId", "u32"), ("LayerNo", "u8"), ("GroupId", "u32")]   # CDataStageLayoutId (Instance.hexpat)
OM = [S("LayoutId", *LAYOUT_ID), ("PosId", "u32")]                        # inline in the 62 writers
OM_STATE = [S("LayoutId", *LAYOUT_ID), ("PosId", "u32"), ("State", "u8")]  # CDataSeasonDungeonOmState, PC 0x766790
OBJECTIVE = [("Type", "u8"), ("Priority", "u8"), ("Param1", "u32"), ("Param2", "u32"),
             ("str", "ObjectiveLabel")]                                    # CDataSoulOrdealObjective, PC 0x779090
REWARD_ITEM = [("RewardIndex", "u32"), ("Amount", "u32")]                  # CDataSoulOrdealRewardItem, PC 0x769240/0x77f9d0
GATHER = [("Id", "u32"), ("ItemId", "u32"), ("Num", "u32"), ("unk_u32", "u32"), ("unk_bool", "bool")]
COMMON_U32 = [("m_unValue", "u32")]                                        # CDataCommonU32 (Packet.hexpat)

# CDataMailAttachmentList (Mail.hexpat, PC 0x76e2f0)
ATT = [S("AttachmentInfo", ("AttachmentId", "u64"), ("IsReceived", "bool"))]
OPTION_COURSE = ATT + [("OptionCourseId", "u32"), ("OptionCourseLineupId", "u32"), ("Time", "u32")]
MAIL_ATT = [L("ItemList", *ATT, ("ItemId", "u32"), ("Num", "u16")),
            L("GPList", *ATT, ("Num", "u32"), ("Type", "u32")),
            L("OptionCourseList", *OPTION_COURSE),
            L("LegendPawnList", *ATT, ("PawnId", "u32"), ("str", "Name"))]

# group 72 DAILY_MISSION (include/DailyMission.hexpat)
DM_REWARD = [("MissionId", "u32"), ("unk_u32", "u32"), ("unk_s64_0", "s64"), ("unk_s64_1", "s64"),
             L("ItemList", ("ItemId", "u32"), ("Num", "u32")),
             L("WalletPointList", ("Type", "u32"), ("Value", "u32")),
             ("str", "unk_str"), S("AttachmentList", *MAIL_ATT)]         # PC 0x762640
DM_MISSION = [("MissionId", "u32"), ("Purpose", "u32"), ("TargetNum", "u32"), S("Reward", *DM_REWARD),
              ("str", "Text"), ("str", "IconUrl"), ("str", "ImageUrl"), ("Progress", "u32"), ("State", "u8"),
              ("StartDate", "s64"), ("EndDate", "s64"), ("SortNo", "u32")]  # PC 0x762530
DM_UNK = [("unk_u32", "u32"),
          L("unk_list", S("OptionCourseInfo", *OPTION_COURSE), ("str", "unk_str"))]  # PC 0x7626e0 / 0x7627f0

# group 59 INFINITY_DELIVERY (include/InfinityDelivery.hexpat)
ID_EVENT = [("EventId", "u32"), ("str", "EventName"), ("StartDate", "s64"), ("EndDate", "s64"),
            ("unk_s64_0", "s64"), ("unk_s64_1", "s64")]                   # PC 0x769fe0
ID_RANKING = [("Rank", "u32"), ("CharacterId", "u32"), ("str", "CharacterName"), ("Point", "u32"),
              ("ClanId", "u32"), ("str", "ClanName")]                      # PC 0x76a850
ID_STATUS = [("str", "CategoryName"), ("unk_u64_0", "u64"), ("unk_u64_1", "u64"), ("str", "PointUnit"),
             L("RankingList", *ID_RANKING), ("str", "unk_str"), ("unk_u32_0", "u32"), ("unk_u32_1", "u32"),
             ("unk_u32_2", "u32"), ("TallyDate", "s64"), L("unk_list_0", *COMMON_U32),
             L("unk_list_1", *COMMON_U32)]                                 # PC 0x769de0
ID_CATEGORY = [("EventId", "u32"), ("str", "EventName"), ("str", "unk_str"), ("str", "Description"),
               ("str", "IconUrl"), ("str", "ImageUrl"),
               L("DeliveryCategoryList", ("CategoryId", "u32"), ("str", "CategoryName"))]  # PC 0x76a170
ID_REWARD_ITEM = [("ItemId", "u32"), ("Num", "u32"), ("unk_u32_0", "u32"), ("unk_u32_1", "u32")]  # PC 0x7699f0
ID_INFO = [S("Event", *ID_EVENT), ("unk_u8", "u8"),
           L("DeliveryItemList", ("ItemId", "u32"), ("MaxNum", "u16"), ("Point", "u32")),
           S("Status", *ID_STATUS), ("str", "RequiredPointSuffix"),
           L("PointRewardList", ("unk_u8_0", "u8"), ("RewardId", "u32"), ("unk_u8_1", "u8"), ("RequiredPoint", "u32"),
             L("ItemList", *ID_REWARD_ITEM)),
           L("RankingRewardList", ("unk_u8", "u8"), ("RewardId", "u32"), ("Rank", "u32"), L("ItemList", *ID_REWARD_ITEM)),
           ("unk_bool", "bool")]                                           # PC 0x769b10

LAYOUTS = {
    # ---- B1: group 62 SEASON_DUNGEON ----
    "62.26.16": [S("OmState", *OM_STATE)],
    "62.12.16": OM,
    "62.18.1": OM,
    "62.18.2": RES(("Type", "u8"),
                   L("ElementParamList", ("TrialId", "u32"), ("str", "TrialName"),
                     L("TrialCost", ("ItemId", "u32"), ("Num", "u16")),
                     L("TrialRewards", ("unk_u32", "u32"),
                       L("RewardList", ("ItemId", "u32"), ("Num", "u32"), ("unk_u32_1", "u32"),
                         ("unk_u8_0", "u8"), ("unk_u8_1", "u8"), ("unk_bool_0", "bool"), ("unk_bool_1", "bool"),
                         ("unk_bool_2", "bool")))),
                   ("unk_bool_0", "bool"), ("unk_u8_0", "u8"), ("unk_bool_1", "bool"), ("unk_u8_1", "u8")),
    "62.16.16": [L("Objectives", *OBJECTIVE)],
    "62.14.16": [("str", "TrialName"), ("TrialId", "u32"), L("ObjectiveList", *OBJECTIVE)],
    "62.15.16": [("EndState", "u8"), S("OmState", *OM_STATE), ("TrialId", "u32")],
    "62.20.1": [("TrialId", "u32")] + OM,
    "62.20.2": RES(),
    "62.22.16": [],
    "62.23.16": [("Ready", "bool")],
    "62.24.1": [("TrialId", "u32"), L("TrialCost", ("str", "ItemUId"), ("Num", "u32"))] + OM,
    "62.24.2": RES(),
    "62.33.1": OM,
    "62.33.2": RES(L("ItemRewards", *GATHER),
                   L("BuffRewards", ("BuffEffect", "u32"), ("BuffId", "u32"), ("str", "BuffName"), ("Level", "u32"))),
    "62.34.1": OM + [L("RewardList", *REWARD_ITEM)],
    "62.34.2": RES(L("RewardList", *REWARD_ITEM)),
    "62.35.1": OM + [("BuffId", "u32"), ("unk_u32", "u32")],
    "62.35.2": RES(),
    "62.40.16": OM,
    # ---- B4: group 71 BATTLE_CONTENT ----
    "71.22.1": [],
    "71.22.2": RES(L("BattleContentInfoList", ("GameMode", "u32"), ("str", "ContentName"),
                     L("BattleContentStageList", ("Id", "u32"), ("str", "StageName"), ("Mode", "u32")),
                     L("BattleContentStageProgressionList", ("Id", "u32"), ("Tier", "u32"),
                       L("ConnectionList", *COMMON_U32)),
                     L("RareItemAppraisalList", *COMMON_U32), L("ItemTakeawayList", *COMMON_U32)),
                   L("BattleContentStatusList",
                     S("BattleContentSituationData", ("GameMode", "u32"), ("StartTime", "s64"),
                       ("RewardReceived", "bool"), ("unk_bool", "bool"), ("RewardBonus", "u8"),
                       ("ReportReset", "u32"), ("ReportSearchResults", "u32"), ("unk_u32_0", "u32"),
                       ("unk_u8", "u8"), ("unk_s64", "s64"), ("ContentId", "u32"), ("unk_u32_1", "u32")),
                     L("BattleContentAvailableRewardsList", ("Id", "u32"), ("Amount", "u8")))),
    # ---- B4: group 72 DAILY_MISSION ----
    "72.0.1": [],
    "72.0.2": RES(L("MissionList", *DM_MISSION), L("SpecialRewardList", *DM_MISSION), L("unk_list", *DM_UNK)),
    "72.1.16": [L("MissionIdList", *COMMON_U32)],
    "72.2.1": [L("MissionIdList", *COMMON_U32), ("StorageType", "u8")],
    "72.2.2": RES(),
    "72.3.1": [("unk_u8", "u8")],
    "72.3.2": RES(("unk_u8", "u8"), L("EventMissionList", *DM_MISSION), L("unk_list", *DM_UNK)),
    # ---- B4: group 59 INFINITY_DELIVERY ----
    "59.0.1": [],
    "59.0.2": RES(L("EventList", *ID_EVENT)),
    "59.4.1": [("CategoryId", "u32")],
    "59.4.2": RES(S("Status", *ID_STATUS)),
    "59.8.1": [],
    "59.8.2": RES(L("CategoryList", *ID_CATEGORY)),
    "59.9.1": [("CategoryId", "u32")],
    "59.9.2": RES(S("Info", *ID_INFO)),
}
W.LAYOUTS = LAYOUTS


def dump(pid, n):
    import collections
    for f in W.files_of(pid)[:n]:
        out, sl, _ = W.walk(f, LAYOUTS[pid], collections.defaultdict(list))
        print("==", os.path.relpath(f, W.RAW), "slack", sl)
        print(json.dumps(out, ensure_ascii=False, default=str))


def main():
    mode = sys.argv[1]
    if mode == "dump":
        dump(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
        return
    ids = sys.argv[2:] or list(LAYOUTS)
    if mode == "stats":
        W.stats(ids)
    elif mode == "fits":
        sys.exit(1 if W.fits(ids) else 0)
    else:
        sys.exit(1 if W.check(ids) else 0)


if __name__ == "__main__":
    main()
