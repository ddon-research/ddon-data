// Group 11 QUEST CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11a-old-patterns.md
// section 1 (wire table, CDataQuestOrderList, CDataQuestProcessState), sections 3-5 and the
// shared-structure table. "PC 0x..." is the reader VA in the PC 03040008 database (image base
// 0x400000); "PS4" names the PS4 02020005 DWARF type (binaries/PS4_02020005/DDOORBIS.elf.h).
// Marks: V = read in IDA, I = inferred. `unk_*` = Season 3 field without a PS4 counterpart; its
// name is open. Field names without the m_ prefix are the earlier patterns' names (most mirror the
// PS4 DWARF names); server C# names are leads only and appear only as "server: <name>".
// Enums come from PS4 DWARF only; values without a DWARF name are UNK_<value>.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"

// nQuestScript::COMMAND_CHECK_LIST (PS4 DWARF; all 210 values equal, the sentinels COMMAND_CHECK
// 0, _END and _NUM are left out; P11a G6, V).
enum COMMAND_CHECK_LIST : u16 {
    COMMAND_CHECK_TALK_NPC = 0x1,
    COMMAND_CHECK_DIE_ENEMY = 0x2,
    COMMAND_CHECK_SCE_HIT_IN = 0x3,
    COMMAND_CHECK_HAVE_ITEM = 0x4,
    COMMAND_CHECK_DELIVER_ITEM = 0x5,
    COMMAND_CHECK_EM_DIE_LIGHT = 0x6,
    COMMAND_CHECK_QST_FLAG_ON = 0x7,
    COMMAND_CHECK_QST_FLAG_OFF = 0x8,
    COMMAND_CHECK_MY_QST_FLAG_ON = 0x9,
    COMMAND_CHECK_MY_QST_FLAG_OFF = 0xA,
    COMMAND_CHECK_PADDING_00 = 0xB,
    COMMAND_CHECK_PADDING_01 = 0xC,
    COMMAND_CHECK_PADDING_02 = 0xD,
    COMMAND_CHECK_STAGE_NO = 0xE,
    COMMAND_CHECK_EVENT_END = 0xF,
    COMMAND_CHECK_PRT = 0x10,
    COMMAND_CHECK_CLEARCOUNT = 0x11,
    COMMAND_CHECK_SCE_FLAG_ON = 0x12,
    COMMAND_CHECK_SCE_FLAG_OFF = 0x13,
    COMMAND_CHECK_TOUCH_ACT_TO_NPC = 0x14,
    COMMAND_CHECK_ORDER_DECIDE = 0x15,
    COMMAND_CHECK_IS_END_CYCLE = 0x16,
    COMMAND_CHECK_IS_INTERRUPT_CYCLE = 0x17,
    COMMAND_CHECK_IS_FAILED_CYCLE = 0x18,
    COMMAND_CHECK_IS_END_RESULT = 0x19,
    COMMAND_CHECK_NPC_TALK_AND_ORDER_UI = 0x1A,
    COMMAND_CHECK_NPC_TOUCH_AND_ORDER_UI = 0x1B,
    COMMAND_CHECK_STAGE_NO_NOT_EQ = 0x1C,
    COMMAND_CHECK_WARLEVEL = 0x1D,
    COMMAND_CHECK_TALK_NPC_WITHOUT_MARKER = 0x1E,
    COMMAND_CHECK_HAVE_MONEY = 0x1F,
    COMMAND_CHECK_SET_QUEST_CLEAR_NUM = 0x20,
    COMMAND_CHECK_MAKE_CRAFT = 0x21,
    COMMAND_CHECK_PLAY_EMOTION = 0x22,
    COMMAND_CHECK_IS_END_TIMER = 0x23,
    COMMAND_CHECK_IS_ENEMY_FOUND = 0x24,
    COMMAND_CHECK_RANDOM_EQ = 0x25,
    COMMAND_CHECK_RANDOM_NOT_EQ = 0x26,
    COMMAND_CHECK_RANDOM_LESS = 0x27,
    COMMAND_CHECK_RANDOM_NOT_GREATER = 0x28,
    COMMAND_CHECK_RANDOM_GREATER = 0x29,
    COMMAND_CHECK_RANDOM_NOT_LESS = 0x2A,
    COMMAND_CHECK_CLEARCOUNT_02 = 0x2B,
    COMMAND_CHECK_INGAME_TIME_RANGE_EQ = 0x2C,
    COMMAND_CHECK_INGAME_TIME_RANGE_NOT_EQ = 0x2D,
    COMMAND_CHECK_PL_HP = 0x2E,
    COMMAND_CHECK_EM_HP_NOT_LESS = 0x2F,
    COMMAND_CHECK_EM_HP_LESS = 0x30,
    COMMAND_CHECK_WEATHER_EQ = 0x31,
    COMMAND_CHECK_WEATHER_NOT_EQ = 0x32,
    COMMAND_CHECK_PL_JOB_EQ = 0x33,
    COMMAND_CHECK_PL_JOB_NOT_EQ = 0x34,
    COMMAND_CHECK_PL_SEX_EQ = 0x35,
    COMMAND_CHECK_PL_SEX_NOT_EQ = 0x36,
    COMMAND_CHECK_SCE_HIT_OUT = 0x37,
    COMMAND_CHECK_WAIT_ORDER = 0x38,
    COMMAND_CHECK_OM_SET_TOUCH = 0x39,
    COMMAND_CHECK_OM_RELEASE_TOUCH = 0x3A,
    COMMAND_CHECK_JOB_LEVEL_NOT_LESS = 0x3B,
    COMMAND_CHECK_JOB_LEVEL_LESS = 0x3C,
    COMMAND_CHECK_MY_QST_FLAG_ON_FROM_FSM = 0x3D,
    COMMAND_CHECK_SCE_HIT_IN_WITHOUT_MARKER = 0x3E,
    COMMAND_CHECK_SCE_HIT_OUT_WITHOUT_MARKER = 0x3F,
    COMMAND_CHECK_KEY_ITEM_POINT = 0x40,
    COMMAND_CHECK_IS_NOT_END_TIMER = 0x41,
    COMMAND_CHECK_IS_MAIN_QUEST_CLEAR = 0x42,
    COMMAND_CHECK_DOGMA_ORB = 0x43,
    COMMAND_CHECK_IS_ENEMY_FOUND_FOR_ORDER = 0x44,
    COMMAND_CHECK_IS_TUTORIAL_FLAG_ON = 0x45,
    COMMAND_CHECK_QUEST_OM_SET_TOUCH = 0x46,
    COMMAND_CHECK_QUEST_OM_RELEASE_TOUCH = 0x47,
    COMMAND_CHECK_NEW_TALK_NPC = 0x48,
    COMMAND_CHECK_NEW_TALK_NPC_WITHOUT_MARKER = 0x49,
    COMMAND_CHECK_IS_TUTORIAL_QUEST_CLEAR = 0x4A,
    COMMAND_CHECK_IS_MAIN_QUEST_ORDER = 0x4B,
    COMMAND_CHECK_IS_TUTORIAL_QUEST_ORDER = 0x4C,
    COMMAND_CHECK_IS_TOUCH_PAWN_DUNGEON_OM = 0x4D,
    COMMAND_CHECK_IS_OPEN_DOOR_OM_QUEST_SET = 0x4E,
    COMMAND_CHECK_EM_DIE_FOR_RANDOM_DUNGEON = 0x4F,
    COMMAND_CHECK_NPC_HP_NOT_LESS = 0x50,
    COMMAND_CHECK_NPC_HP_LESS = 0x51,
    COMMAND_CHECK_IS_ENEMY_FOUND_WITHOUT_MARKER = 0x52,
    COMMAND_CHECK_IS_EVENT_BOARD_ACCEPTED = 0x53,
    COMMAND_CHECK_WORLD_MANAGE_QUEST_FLAG_ON = 0x54,
    COMMAND_CHECK_WORLD_MANAGE_QUEST_FLAG_OFF = 0x55,
    COMMAND_CHECK_TOUCH_EVENT_BOARD = 0x56,
    COMMAND_CHECK_OPEN_ENTRY_RAID_BOSS = 0x57,
    COMMAND_CHECK_OEPN_ENTRY_FORT_DEFENSE = 0x58,
    COMMAND_CHECK_DIE_PLAYER = 0x59,
    COMMAND_CHECK_PARTY_NUM_NOT_LESS_WTIHOUT_PAWN = 0x5A,
    COMMAND_CHECK_PARTY_NUM_NOT_LESS_WITH_PAWN = 0x5B,
    COMMAND_CHECK_LOST_MAIN_PAWN = 0x5C,
    COMMAND_CHECK_SP_TALK_NPC = 0x5D,
    COMMAND_CHECK_OEPN_JOB_MASTER = 0x5E,
    COMMAND_CHECK_TOUCH_RIM_STONE = 0x5F,
    COMMAND_CHECK_GET_ACHIEVEMENT = 0x60,
    COMMAND_CHECK_DUMMY_NOT_PROGRESS = 0x61,
    COMMAND_CHECK_DIE_RAID_BOSS = 0x62,
    COMMAND_CHECK_CYCLE_TIMER_ZERO = 0x63,
    COMMAND_CHECK_CYCLE_TIMER = 0x64,
    COMMAND_CHECK_QUEST_NPC_TALK_AND_ORDER_UI = 0x65,
    COMMAND_CHECK_QUEST_NPC_TOUCH_AND_ORDER_UI = 0x66,
    COMMAND_CHECK_IS_FOUND_RAID_BOSS = 0x67,
    COMMAND_CHECK_QUEST_OM_SET_TOUCH_WITHOUT_MARKER = 0x68,
    COMMAND_CHECK_QUEST_OM_RELEASE_TOUCH_WITHOUT_MARKER = 0x69,
    COMMAND_CHECK_TUTORIAL_TALK_NPC = 0x6A,
    COMMAND_CHECK_IS_LOGIN = 0x6B,
    COMMAND_CHECK_IS_PLAY_END_FIRST_SEASON_END_CREDIT = 0x6C,
    COMMAND_CHECK_IS_KILLED_TARGET_ENEMY_SET_GROUP = 0x6D,
    COMMAND_CHECK_IS_KILLED_TARGET_EM_SET_GRP_NO_MARKER = 0x6E,
    COMMAND_CHECK_IS_LEFT_CYCLE_TIMER = 0x6F,
    COMMAND_CHECK_OM_END_TEXT = 0x70,
    COMMAND_CHECK_QUEST_OM_END_TEXT = 0x71,
    COMMAND_CHECK_OPEN_AREA_MASTER = 0x72,
    COMMAND_CHECK_HAVE_ITEM_ALL_BAG = 0x73,
    COMMAND_CHECK_OPEN_NEWSPAPER = 0x74,
    COMMAND_CHECK_OPEN_QUEST_BOARD = 0x75,
    COMMAND_CHECK_STAGE_NO_WITHOUT_MARKER = 0x76,
    COMMAND_CHECK_TALK_QUEST_NPC_UNIT_MARKER = 0x77,
    COMMAND_CHECK_TOUCH_QUEST_NPC_UNIT_MARKER = 0x78,
    COMMAND_CHECK_IS_EXIST_SECOND_PAWN = 0x79,
    COMMAND_CHECK_IS_ORDER_JOB_TUTORIAL_QUEST = 0x7A,
    COMMAND_CHECK_IS_OPEN_WAREHOUSE = 0x7B,
    COMMAND_CHECK_IS_MYQUEST_LAYOUT_FLAG_ON = 0x7C,
    COMMAND_CHECK_IS_MYQUEST_LAYOUT_FLAG_OFF = 0x7D,
    COMMAND_CHECK_IS_OPEN_WAREHOUSE_REWARD = 0x7E,
    COMMAND_CHECK_IS_ORDER_LIGHT_QUEST = 0x7F,
    COMMAND_CHECK_IS_ORDER_WORLD_QUEST = 0x80,
    COMMAND_CHECK_IS_LOST_MAIN_PAWN = 0x81,
    COMMAND_CHECK_IS_FULL_ORDER_QUEST = 0x82,
    COMMAND_CHECK_IS_BAD_STATUS = 0x83,
    COMMAND_CHECK_CHECK_AREA_RANK = 0x84,
    COMMAND_CHECK_PADDING_133 = 0x85,
    COMMAND_CHECK_ENABLE_PARTY_WARP = 0x86,
    COMMAND_CHECK_IS_HUGEBLE = 0x87,
    COMMAND_CHECK_IS_DOWN_ENEMY = 0x88,
    COMMAND_CHECK_OPEN_AREA_MASTER_SUPPLIES = 0x89,
    COMMAND_CHECK_OPEN_ENTRY_BOARD = 0x8A,
    COMMAND_CHECK_NOTICE_INTERRUPT_CONTENTS = 0x8B,
    COMMAND_CHECK_OPEN_RETRY_SELECT = 0x8C,
    COMMAND_CHECK_IS_PL_WEAKENING = 0x8D,
    COMMAND_CHECK_NOTICE_PARTY_INVITE = 0x8E,
    COMMAND_CHECK_IS_KILLED_AREA_BOSS = 0x8F,
    COMMAND_CHECK_IS_PARTY_REWARD = 0x90,
    COMMAND_CHECK_IS_FULL_BAG = 0x91,
    COMMAND_CHECK_OPEN_CRAFT_EXAM = 0x92,
    COMMAND_CHECK_LEVEL_UP_CRAFT = 0x93,
    COMMAND_CHECK_IS_CLEAR_LIGHT_QUEST = 0x94,
    COMMAND_CHECK_OPEN_JOB_MASTER_REWARD = 0x95,
    COMMAND_CHECK_TOUCH_ACT_QUEST_NPC = 0x96,
    COMMAND_CHECK_IS_LEADER_AND_JOIN_PAWN = 0x97,
    COMMAND_CHECK_IS_ACCEPT_LIGHT_QUEST = 0x98,
    COMMAND_CHECK_IS_RELEASE_WARP_POINT = 0x99,
    COMMAND_CHECK_IS_SET_PLAYER_SKILL = 0x9A,
    COMMAND_CHECK_IS_ORDER_MY_QUEST = 0x9B,
    COMMAND_CHECK_IS_NOT_ORDER_MY_QUEST = 0x9C,
    COMMAND_CHECK_HAS_MYPAWN = 0x9D,
    COMMAND_CHECK_IS_FAVORITE_WARP_POINT = 0x9E,
    COMMAND_CHECK_CRAFT = 0x9F,
    COMMAND_CHECK_IS_KILLED_TARGET_ENEMY_SET_GROUP_GM_MAIN = 0xA0,
    COMMAND_CHECK_IS_KILLED_TARGET_ENEMY_SET_GROUP_GM_SUB = 0xA1,
    COMMAND_CHECK_HAS_USED_KEY = 0xA2,
    COMMAND_CHECK_IS_CYCLE_FLAG_OFF_PERIOD = 0xA3,
    COMMAND_CHECK_IS_ENEMY_FOUND_GM_MAIN = 0xA4,
    COMMAND_CHECK_IS_ENEMY_FOUND_GM_SUB = 0xA5,
    COMMAND_CHECK_IS_LOGIN_BUG_FIXED_ONLY = 0xA6,
    COMMAND_CHECK_IS_SEARCH_CLAN = 0xA7,
    COMMAND_CHECK_IS_OPEN_AREA_LIST_UI = 0xA8,
    COMMAND_CHECK_IS_RELEASE_WARP_POINT_ANYONE = 0xA9,
    COMMAND_CHECK_DEVIDE_PLAYER = 0xAA,
    COMMAND_CHECK_NOW_PHASE = 0xAB,
    COMMAND_CHECK_IS_RELEASE_PORTAL = 0xAC,
    COMMAND_CHECK_IS_GET_APPRAISE_ITEM = 0xAD,
    COMMAND_CHECK_IS_SET_PARTNER_PAWN = 0xAE,
    COMMAND_CHECK_IS_PRESENT_PARTNER_PAWN = 0xAF,
    COMMAND_CHECK_IS_RELEASE_MY_ROOM = 0xB0,
    COMMAND_CHECK_IS_EXIST_DIVIDE_PLAYER = 0xB1,
    COMMAND_CHECK_NOT_DIVIDE_PLAYER = 0xB2,
    COMMAND_CHECK_IS_GATHER_PARTY_IN_STAGE = 0xB3,
    COMMAND_CHECK_IS_FINISHED_ENEMY_DIVIDE_ACTION = 0xB4,
    COMMAND_CHECK_IS_OPEN_DOOR_OM_QUEST_SET_NO_MARKER = 0xB5,
    COMMAND_CHECK_IS_FINISHED_EVENT_ORDER_NUM = 0xB6,
    COMMAND_CHECK_IS_PRESENT_PARTNER_PAWN_NO_MARKER = 0xB7,
    COMMAND_CHECK_IS_OM_BROKEN_LAYOUT = 0xB8,
    COMMAND_CHECK_IS_OM_BROKEN_QUEST = 0xB9,
    COMMAND_CHECK_IS_HOLDING_PERIOD_CYCLE_CONTENTS = 0xBA,
    COMMAND_CHECK_IS_NOT_HOLDING_PERIOD_CYCLE_CONTENTS = 0xBB,
    COMMAND_CHECK_IS_RESET_INSTANCE_AREA = 0xBC,
    COMMAND_CHECK_CHECK_MOON_AGE = 0xBD,
    COMMAND_CHECK_IS_ORDER_PAWN_QUEST = 0xBE,
    COMMAND_CHECK_IS_TAKE_PICTURES = 0xBF,
    COMMAND_CHECK_IS_STAGE_FOR_MAIN_QUEST = 0xC0,
    COMMAND_CHECK_IS_RELEASE_PAWN_EXPEDITION = 0xC1,
    COMMAND_CHECK_OPEN_PP_MODE = 0xC2,
    COMMAND_CHECK_PP_NOT_LESS = 0xC3,
    COMMAND_CHECK_OPEN_PP_SHOP = 0xC4,
    COMMAND_CHECK_TOUCH_CLAN_BOARD = 0xC5,
    COMMAND_CHECK_IS_ONE_OFF_GATHER = 0xC6,
    COMMAND_CHECK_IS_OM_BROKEN_LAYOUT_NO_MARKER = 0xC7,
    COMMAND_CHECK_IS_OM_BROKEN_QUEST_NO_MARKER = 0xC8,
    COMMAND_CHECK_KEY_ITEM_POINT_EQ = 0xC9,
    COMMAND_CHECK_IS_EMOTION = 0xCA,
    COMMAND_CHECK_IS_EQUIP_COLOR = 0xCB,
    COMMAND_CHECK_IS_EQUIP = 0xCC,
    COMMAND_CHECK_IS_TAKE_PICTURES_NPC = 0xCD,
    COMMAND_CHECK_SAY_MESSAGE = 0xCE,
    COMMAND_CHECK_IS_TAKE_PICTURES_WITHOUT_PAWN = 0xCF,
    COMMAND_CHECK_IS_LINKAGE_ENEMY_FLAG = 0xD0,
    COMMAND_CHECK_IS_LINKAGE_ENEMY_FLAG_OFF = 0xD1,
    COMMAND_CHECK_IS_RELEASE_SECRET_ROOM = 0xD2
};

// nQuest::ORDER_CONDITION_TYPE (PS4 DWARF, __int32; P11a G6, V). _NUM (0xF) left out.
enum ORDER_CONDITION_TYPE : u32 {
    ORDER_CONDITION_TYPE_NONE = 0x0,
    ORDER_CONDITION_TYPE_MAX_LEVEL = 0x1,
    ORDER_CONDITION_TYPE_JOB_LEVEL = 0x2,
    ORDER_CONDITION_TYPE_SOLO = 0x3,
    ORDER_CONDITION_TYPE_MAIN_QUEST_CLEAR = 0x6,
    ORDER_CONDITION_TYPE_TUTORIAL_QUEST_CLEAR = 0x7,
    ORDER_CONDITION_TYPE_END_QUEST_CLEAR = 0x8,
    ORDER_CONDITION_TYPE_AREAMASTER_RANK = 0x9,
    ORDER_CONDITION_TYPE_SOLO_WITH_PAWN = 0xA,
    ORDER_CONDITION_TYPE_TUTOR_QUEST_GROUP_01 = 0xB,
    ORDER_CONDITION_TYPE_TUTOR_QUEST_GROUP_02 = 0xC,
    ORDER_CONDITION_TYPE_PARTNER_PAWN = 0xE
};

// nQuest::CYCLE_CONTENTS_CATEGORY (PS4 DWARF, __int32; P11a G6, V).
enum CYCLE_CONTENTS_CATEGORY : s32 {
    CYCLE_CONTENTS_CATEGORY_NONE = 0x0,
    CYCLE_CONTENTS_CATEGORY_FORT_DEFENSE = 0x1,
    CYCLE_CONTENTS_CATEGORY_RAID_BOSS = 0x3
};

// nQuest::CYCLE_CONTENTS_SUB_CATEGORY (PS4 DWARF, __int32). 1005-1009 and 3007 are not in PS4
// DWARF (P11a G6, 12); whether Season 3 added them is unresolved. Server lead names:
// 1005 FORT_DEFENSE_DACREIM, 1006 FORT_DEFENSE_JIFULE, 1007 FORT_DEFENSE_FORST_MIST,
// 1008 FORT_DEFENSE_FLAME_DESPAIR, 1009 FORT_DEFENSE_ACRE_SELUND, 3007 RAID_DRAGON_AWAKENED.
enum CYCLE_CONTENTS_SUB_CATEGORY : s32 {
    CYCLE_CONTENTS_SUB_CATEGORY_NONE = 0x0,
    CYCLE_CONTENTS_SUB_CATEGORY_FORT_DEFENSE_NORMAL = 0x3E9,  // 1001
    CYCLE_CONTENTS_SUB_CATEGORY_FORT_DEFENSE_NEST = 0x3EA,    // 1002
    CYCLE_CONTENTS_SUB_CATEGORY_FORT_DEFENSE_BORD = 0x3EB,    // 1003
    CYCLE_CONTENTS_SUB_CATEGORY_FORT_DEFENSE_SHRINE = 0x3EC,  // 1004
    UNK_1005 = 0x3ED,
    UNK_1006 = 0x3EE,
    UNK_1007 = 0x3EF,
    UNK_1008 = 0x3F0,
    UNK_1009 = 0x3F1,
    CYCLE_CONTENTS_SUB_CATEGORY_RAID_FOREST = 0xBBA,          // 3002
    CYCLE_CONTENTS_SUB_CATEGORY_RAID_GOLD_DRAGON = 0xBBB,     // 3003
    CYCLE_CONTENTS_SUB_CATEGORY_RAID_ZULU = 0xBBC,            // 3004
    CYCLE_CONTENTS_SUB_CATEGORY_RAID_FOREST_GOLD = 0xBBD,     // 3005
    CYCLE_CONTENTS_SUB_CATEGORY_RAID_ZULU_SECOND = 0xBBE,     // 3006
    UNK_3007 = 0xBBF
};

// CDataRewardItem: PC list reader 0x7771b0 {u32, u16} (V); PS4 CDataRewardItem, same.
struct CDataRewardItem {
    u32 ItemId;
    u16 Num;
};

// CDataQuestEnemyInfo: PC list reader 0x773d90 {u32, u32, u16, bool} (V); PS4 {u32 m_unGroupId,
// u16 m_usLv, b8 m_bIsPartyRecommend}. The first u32 is GroupId, the second is Season 3 (T001c 5,
// V by consumer match): PC 0x9d2590 (= PS4 cQuestTask::setEnemyInfoParam 0x54dc30) copies element
// +4 to the mEnemyGroupId slot and element +8 to a new trailing member of
// cQuestTask::cEnemyGroupInfo, part of its dedupe key. P11a §1.3 ("Season 3 u32 first") is
// contradicted (C).
struct CDataQuestEnemyInfo {
    u32 GroupId;   // PS4 m_unGroupId
    // T014b I (consumer, earlier): T001c 5 (Quest.hexpat): PC 0x9d2590 (= PS4
    // cQuestTask::setEnemyInfoParam 0x54dc30) copies it to a new trailing member of
    // cQuestTask::cEnemyGroupInfo, part of its dedupe key; no name
    u32 unk_u32;   // Season 3; trailing member of cQuestTask::cEnemyGroupInfo (dedupe key)
    u16 Lv;
    bool IsPartyRecommend;
};

// CDataQuestProgressWork: PC list reader 0x7754a0 {u32, s32 x4} (V); PS4 same name.
struct CDataQuestProgressWork {
    u32 CommandNo;
    s32 Work01;
    s32 Work02;
    s32 Work03;
    s32 Work04;
};

// CDataQuestCommand: PC list reader 0x7738f0 {u16, s32 x4} (V); PS4 CDataQuestCommand.
struct CDataQuestCommand {
    u16 Command;
    s32 Param01;
    s32 Param02;
    s32 Param03;
    s32 Param04;
};

// The same wire shape read in the list of lists 0x757f20 -> 0x7738f0 (V); the u16 viewed as
// nQuestScript::COMMAND_CHECK_LIST.
struct CDataQuestCommandCheck {
    COMMAND_CHECK_LIST Command;
    s32 Param01;
    s32 Param02;
    s32 Param03;
    s32 Param04;
};

// CDataQuestProcessState: PC list reader 0x775310, element 0x775420 (V); PS4 same name.
struct CDataQuestProcessState {
    u16 ProcessNo;
    u16 SequenceNo;
    u16 BlockNo;
    MtTypedArray<CDataQuestProgressWork> WorkList;
    MtTypedArray<MtTypedArray<CDataQuestCommandCheck> > CheckCommandList;
    MtTypedArray<CDataQuestCommand> ResultCommandList;
};

// CDataQuestAnnounce: u32 lists (PC 0x773820 in CDataQuestLog, V). The earlier enum
// QUEST_ANNOUNCE_TYPE has no PS4 DWARF source (P11a G6): plain u32.
struct CDataQuestAnnounce {
    u32 AnnounceNo;
};

// CDataQuestTalkInfo element of PC list 0x7757e0 {u32, u32, u16, bool} (V); PS4 TalkInfo lacks
// the leading u32.
struct CDataQuestTalkInfo {
    // T014b V (consumer); name V (nQuest::QUEST_ID): PC quest-task setters copy each TalkInfo
    // element: element +4 (this field) is wrapped by nQuest::QUEST_ID::QUEST_ID_0 and its value
    // passed as the 5th argument of addTalkData 0x9ce880 (PS4 cQuestPersonalData::addTalkData
    // 0x54f100: (...)
    u32 QuestId;    // Season 3 (no PS4 counterpart)
    u32 TalkNo;
    u16 NpcId;
    bool IsOneOnly;
};

// CDataQuestLog: PC 0x774850 = list u32 (0x773820) + list CDataQuestTalkInfo (0x7757e0) (V).
struct CDataQuestLog {
    MtTypedArray<CDataQuestAnnounce> QuestAnnounceList;
    MtTypedArray<CDataQuestTalkInfo> QuestTalkInfoList;
};

// u32 lists with separate PC readers 0x773eb0 / 0x774350 (V); PS4 CDataQuestFlag /
// CDataQuestLayoutFlag.
struct CDataQuestFlag {
    u32 FlagId;
};

struct CDataQuestLayoutFlag {
    u32 FlagId;
};

// CDataQuestOrderConditionParam: PC list 0x774890 {u32, s32, s32} (V).
struct CDataQuestOrderConditionParam {
    ORDER_CONDITION_TYPE Type;
    s32 Param01;
    s32 Param02;
};

// CDataQuestLayoutFlagSetInfo: PC list 0x774420 {u32, list {u32, u32}} (V).
struct CDataQuestSetInfo {
    u32 StageNo;
    u32 GroupId;
};

struct CDataQuestLayoutFlagSetInfo {
    u32 LayoutFlagNo;
    MtTypedArray<CDataQuestSetInfo> SetInfoList;
};

// CDataQuestExp (name from the earlier patterns, no PS4 type): PC list 0x76c780 {u8, u8, u32} (V).
// The second u8 had the enum ExpType, which has no PS4 DWARF source (P11a G6; server lead:
// 1 ExperiencePoints, 2 ClanPoints, 3 PlayPoints): plain u8.
struct CDataQuestExp {
    // T014b open (no consumer found), kept unk: 0x64dd10 reads only the element +5 (Type); the
    // setTaskParam variants 0x9d2ce0, 0x9d32f0, 0x9d41d0 and 0x9d3f10 do not read the BaseExp list
    // (CDataQuestList +44, CDataQuestOrderList +48)
    u8 unk_u8;
    u8 Type;
    u32 Value;
};

// Season 3 list element {u32, s64}: PC list 0x775900 (V; the s64 is R.s64), no PS4 counterpart.
struct CDataQuestUnkU32S64 {
    // T014b V (role); name I: CDataQuestOrderList list +328 (reader 0x774a70 -> 0x775900).
    // setTaskParam 0x9d32f0 loops over it: when 0x64d200(task, +4) is false it calls
    // cQuestTaskParam::setTimer(task, +4, max(0, (s32)+8 - now)), now = server time at sGame (...)
    u32 TimerIdx;
    // T014b V (role); name I: 0x9d32f0 subtracts the server time (sGame +0xB28) from the low dword
    // of +8 and passes the result, clamped at 0, as setTimer's sec: the absolute end time of quest
    // timer +4
    s64 EndTime;
};

// Season 3 list element {u32, u16, u16, u16}: PC list 0x762fb0 (V widths), no PS4 counterpart in
// CDataQuestOrderList. Basis for the names: the PS4 CDataQuestList element CDataDeliveryItem
// {u32 m_unItemId, u16 m_usNum} (DWARF; T005 1.1 row 23); ItemId and Num are I by position (the PC
// element adds two u16); the two added u16 have no basis and stay unk.
struct CDataQuestDeliveryItem {
    u32 ItemId;      // I (position, PS4 m_unItemId)
    u16 Num;         // I (position, PS4 m_usNum)
    // T014b V (role: lookup key); I (name): setTaskParam 0x9d2ce0 copies the element into
    // cQuestTask::cDeliveryItemInfo (vtable 0x1c07288, DTI dti__55; PS4 has only mItemId/mItemNum)
    // +12 (...)
    u16 MsgTagKey0;   // Season 3; server: NeedNum (lead)
    // T014b V (role: lookup key); I (name): second number of the <QDEL NAME|NUM a b> message tag:
    // 0x9cf870 / 0x9cf8b0 match cDeliveryItemInfo +16 (this field) with it (see unk_u16_0)
    u16 MsgTagKey1;   // Season 3
};

// CDataQuestOrderList: PC element reader 0x774a70 (lists 0x7749a0, 0x76eb40, 0x77b2a0, 0x770ab0;
// P11a 1, V). PS4 CDataQuestOrderList (Season 2 layout) has u32 BaseGold/BaseExp/BaseRim where PC
// reads two lists, two u64 (OrderDate, EndDistributionDate) where PC reads three, EnemyInfo and
// TalkInfo without their leading u32, and none of the three Season 3 lists marked below.
struct CDataQuestOrderList {
    u32 KeyId;
    u32 QuestScheduleId;
    u32 QuestId;
    u32 AreaId;
    u32 BaseLevel;
    u16 ContentJoinItemRank;
    MtTypedArray<CDataWalletPoint> BaseGold;   // PC 0x77c5a0; name I (PS4 u32 m_unBaseGold here)
    MtTypedArray<CDataQuestExp> BaseExp;       // PC 0x76c780; name I (PS4 u32 m_unBaseExp here)
    // The three u32 names are PS4's (I): PC replaced PS4's six u32s here with the two lists above
    // plus these three, so which PS4 fields survive is unresolved (R2 F5).
    u32 OrderNpcId;   // name I
    u32 NameMsgId;    // name I
    u32 DetailMsgId;  // name I
    // PC reads 3 x u64 (0x774b0c-0x774b75); PS4 has two. Which one is new is unresolved: the
    // names OrderDate / EndDistributionDate on the last two are I.
    // T014b I (consumer + value): PC reader 0x774a70 reads u64 at +80, +88, +96; PC 0x64d690 passes
    // +96 as EndDistributionDate (V) and +80 as the same new argument as the CDataQuestList first
    // u64 (-> cQuestTaskParam +376) (...)
    // R4 F3: V (consumer); I (name): getter 0x64d260 (caller 0x9d04c0) returns true when (+376 != 0
    // and +376 > now) or (+296 != 0 and +296 < now), now = the current-time qword at +2856 (as shop
    // 0x5fa060): a distribution-window test, +376 the start, +296 the end; server lead agrees
    u64 DistributionStartDate;
    u64 OrderDate;
    u64 EndDistributionDate;
    MtTypedArray<CDataRewardItem> FixedRewardItemList;
    MtTypedArray<CDataRewardItem> FixedRewardSelectItemList;
    // T014b I (consumer): PC 0x64d690 passes +144 as the same cQuestPoint list argument as
    // CDataQuestList.unk_u32_list
    MtTypedArray<u32> unk_u32_list;            // PC 0x75eec0, Season 3
    CDataQuestLog QuestLog;
    MtTypedArray<CDataQuestFlag> QuestFlagList;
    MtTypedArray<CDataQuestLayoutFlag> QuestLayoutFlagList;
    MtTypedArray<CDataQuestProcessState> QuestProcessStateList;
    MtTypedArray<CDataQuestOrderConditionParam> QuestOrderConditionParamList;
    MtTypedArray<CDataQuestEnemyInfo> QuestEnemyInfoList;
    MtTypedArray<CDataQuestLayoutFlagSetInfo> QuestLayoutFlagSetInfoList;
    MtTypedArray<CDataQuestUnkU32S64> unk_u32_s64_list;   // PC 0x775900, Season 3
    MtTypedArray<CDataQuestDeliveryItem> DeliveryItemArray; // PC 0x762fb0, Season 3 (name I)
    bool IsClientOrder;
    bool IsEnable;
    bool CanProgress;
};

// CDataPartyQuestProgressInfo: PC 0x771aa0 (P11a 3, V); PS4 CPartyQuestProgressInfo (DWARF), same
// u32-count lists. Users: 11.71.2, 11.120.16.
struct CDataQuestIdScheduleId {
    u32 QuestId;
    u32 QuestScheduleId;
};

// CDataDeliveredItem: PS4 {u32 m_unItemId, u16 m_usItemNum, u16 m_usNeedNum} (V names,
// DDOORBIS.elf.h:71939, TC1).
struct CDataDeliveredItem {
    u32 ItemId;
    u16 ItemNum;
    u16 NeedNum;
};

// PC lists 0x762e80 / 0x762d80; PS4 CDataDeliveredItemRecord.
struct CDataDeliveredItemRecord {
    u32 CharacterId;
    u32 QuestScheduleId;
    u16 ProcessNo;
    MtTypedArray<CDataDeliveredItem> DeliveredItemList;
};

// PC lists 0x774230 / 0x774140; PS4 CDataQuestKeyItemPointRecord.
struct CDataQuestKeyItemPoint {
    u8 PointID;
    u16 Point;
};

struct CDataQuestKeyItemPointRecord {
    u32 QuestScheduleId;
    u16 ProcessNo;
    MtTypedArray<CDataQuestKeyItemPoint> QuestKeyItemPointList;
};

struct CDataPartyQuestProgressInfo {
    MtTypedArray<CDataQuestOrderList> QuestOrderList;          // PC 0x7749a0
    MtTypedArray<CDataQuestIdScheduleId> SoloQuestOrderList;   // PC 0x774050
    MtTypedArray<CDataDeliveredItemRecord> DeliveredItemRecordList;
    MtTypedArray<CDataQuestKeyItemPointRecord> QuestKeyItemPointRecordList;
};

// ---------------------------------------------------------------------------------------------
// Spec 006 T005 additions (specs/006-packet-pattern-coverage/research/T005-quest.md sections 1,
// 44). Names are the PS4 02020005 DWARF member names without m_ (V) unless marked (I) with the
// basis; a Season 3 member without a PS4 counterpart is `unk_*`, with any server name as a lead.
// ---------------------------------------------------------------------------------------------

// CDataQuestList: PC reader 0x774530 (T005 1.1, V order and widths); PS4 CDataQuestList (=
// CQuestList, Read_CDataQuestList_ 0x1a249a0). A smaller reader than CDataQuestOrderList above.
// Season 3: PS4's u32 BaseGold/BaseExp/BaseRim become two lists, a second u64 and a u32 list
// appear; the talk info, enemy info and delivery item elements take their Season 3 shapes.
struct CDataQuestList {
    u32 KeyId;
    u32 QuestScheduleId;
    u32 QuestId;
    u32 BaseLevel;
    u16 ContentJoinItemRank;
    MtTypedArray<CDataWalletPoint> BaseWalletPoint;  // PC 0x77c5a0; name I (wallet points in place of PS4 BaseGold, BaseRim)
    MtTypedArray<CDataQuestExp> BaseExp;             // PC 0x76c780; name I (in place of PS4 u32 BaseExp)
    // PS4 has six u32 here (BaseGold, BaseExp, BaseRim, OrderNpcId, NameMsgId, DetailMsgId); PC
    // reads the two lists above plus three u32. Names I by position (the last three PS4 names).
    u32 OrderNpcId;   // name I
    u32 NameMsgId;    // name I
    u32 DetailMsgId;  // name I
    // PC reads 2 x u64, PS4 one (EndDistributionDate). Which one is new is unresolved (I).
    // T014b I (consumer + value; lead agrees): PC 0x64d620 passes +88 where PS4 passes
    // m_ullEndDistributionDate (-> cQuestTaskParam +296; EndDistributionDate V) and +80 as a new
    // trailing argument stored at cQuestTaskParam +376 (no PS4 member) (...)
    // R4 F3: V (consumer); I (name): getter 0x64d260 (caller 0x9d04c0) returns true when (+376 != 0
    // and +376 > now) or (+296 != 0 and +296 < now), now = the current-time qword at +2856 (as shop
    // 0x5fa060): a distribution-window test, +376 the start, +296 the end; server lead agrees
    u64 DistributionStartDate;               // Season 3 (I position); server: DistributionStartDate (lead)
    u64 EndDistributionDate;   // name I (position)
    MtTypedArray<CDataRewardItem> FixedRewardItemList;
    MtTypedArray<CDataRewardItem> FixedRewardSelectItemList;
    // T014b I (consumer): PC 0x64d700 wraps each u32 as mIdx of a cQuestPoint (DTI name in the PC
    // database) in a new cQuestTaskParam array (+384); no PS4 counterpart; values 1..93
    MtTypedArray<u32> unk_u32_list;                  // PC 0x75eec0, Season 3; server: ContentsReleaseList (lead)
    MtTypedArray<CDataQuestOrderConditionParam> QuestOrderConditionParamList;
    CDataQuestLog QuestLog;                          // PC 0x774850
    MtTypedArray<CDataQuestFlag> QuestFlagList;
    MtTypedArray<CDataQuestLayoutFlag> QuestLayoutFlagList;
    MtTypedArray<CDataQuestProcessState> QuestProcessStateList;
    MtTypedArray<CDataQuestEnemyInfo> QuestEnemyInfoList;
    MtTypedArray<CDataQuestLayoutFlagSetInfo> QuestLayoutFlagSetInfoList;
    MtTypedArray<CDataQuestDeliveryItem> DeliveryItemList;  // PC 0x762fb0 (Season 3 shape)
    bool IsClientOrder;
};

// CDataQuestContents: PC 0x773a20 (V); PS4 CDataQuestContents {u8 Type, s32 Param01-04}.
struct CDataQuestContents {
    u8 Type;
    s32 Param01;
    s32 Param02;
    s32 Param03;
    s32 Param04;
    // T014b open (not read), kept unk: reader 0x773a20 puts it at contents +24 (light element +408,
    // lot element +376). LIGHT_QUEST_LIST: handler 0x7f13f0 (not a function) keeps the packet at
    // conn sub +0x1A4; getters 0x86d830 / 0x86d840 (list) (...)
    u16 unk_u16_0;   // Season 3; server: Unk0 (lead)
    // T014b open (not read), kept unk: contents +26 (light element +410, lot +378); same consumers
    // as unk_u16_0, none reads it (Param04 at +20 is unread too)
    u16 unk_u16_1;   // Season 3; server: Unk1 (lead)
};

// CDataLightQuestDetail: PC 0x76d1c0 reads 7 x u32 (V); PS4 has 6 (m_unAreaId, m_unBaseAreaPoint,
// m_unGetCP, m_unOrderLimit, m_unClearNum, m_unBoardType). Which of the 7 is new is unresolved,
// so all stay unk_* (moved here from the 11.89.16 pattern, unchanged; server order AreaId,
// BoardId, GetAp, GetCp, OrderLimit, ClearNum, BoardType is a lead only).
struct CDataLightQuestDetail {
    // T014b V (consumer): 0x9d2af0: +4 -> taskParam +367; 0x64d690 stores
    // CDataQuestOrderList.AreaId to the same +367 (PS4 mAreaId)
    u32 AreaId;
    // T014b I (consumer): 0x9d2af0: +8 -> taskParam +368, a byte with no PS4 member (PS4
    // mRandomRewardNum is PC +369 per 0x64dd10); server lead BoardId, no code name
    u32 unk_u32_1;
    // T014b V (consumer): 0x9d2af0: +12 -> taskParam +312; PC setSetQuestDetail 0x64dd10 stores
    // CDataSetQuestDetail.BaseAreaPoint there (PS4 mAreaPoint = m_unBaseAreaPoint)
    u32 BaseAreaPoint;
    // T014b I (consumer, member order): 0x9d2af0: +16 -> dword +360, 4 bytes before BoardType +364;
    // PS4 mGetCP 480 is 4 bytes before mBoardType 484
    u32 GetCP;
    // T014b I (consumer, member order): 0x9d2af0: +20 -> word +356, right after ClearNum +354 (V);
    // PS4 mClearNum 474, mOrderLimit 476
    u32 OrderLimit;
    // T014b V (consumer): 0x9d2af0: +24 -> word +354; 0x64dd10 stores ClearCount there (PS4
    // mClearNum = m_unClearCount)
    u32 ClearNum;
    // T014b I (consumer, member order): 0x9d2af0: +28 -> byte +364, 3 bytes before AreaId +367; PS4
    // mBoardType 484, mAreaId 487
    u32 BoardType;
};

// CDataLightQuestList: element of PC list 0x76d250 (V); PS4 {m_Param, m_Detail, m_Contents}.
struct CDataLightQuestList {
    CDataQuestList Param;
    CDataLightQuestDetail Detail;
    CDataQuestContents Contents;
};

// CDataSetQuestDetail: PC 0x778040 (V): u32 x4, list WalletPoint, list QuestExp, u16, u16, u8 x5,
// bool. PS4 0x1a23b80 has u16 x5 (UndiscoveryGoldRatio, UndiscoveryExpRatio, UndiscoveryRimRatio,
// LeaderCompleteNum, RepeatRewardType) where PC reads two lists and two u16: which u16 survive is
// unresolved (moved here from the 11.89.16 pattern, unchanged).
struct CDataSetQuestDetail {
    u32 ImageId;
    u32 ClearCount;
    u32 ClearCharacterNum;
    u32 BaseAreaPoint;
    MtTypedArray<CDataWalletPoint> unk_wallet_point_list;   // PC 0x77c5a0, Season 3
    MtTypedArray<CDataQuestExp> unk_quest_exp_list;         // PC 0x76c780, Season 3
    // T014b I (elimination): 0x64dd10 does not read +60; of the five PS4 u16 the three ratios
    // became the wallet/exp lists (0x64dd10 applies them to mUndiscoveryGold/Rim/Exp) and
    // RepeatRewardType is +62, leaving LeaderCompleteNum (also unread by PS4 (...)
    u16 LeaderCompleteNum;
    // T014b V (consumer): 0x64dd10: +62 -> taskParam +204 beside +208 = RepeatRewardValue and +212
    // = the CompleteNum formula, as PS4 mRepeatBonus.mType = m_usRepeatRewardType
    u16 RepeatRewardType;
    u8 RepeatRewardValue;
    u8 RepeatRewardCompleteNum;
    u8 RandomRewardNum;
    u8 ChargeRewardNum;
    u8 ProgressBonusNum;
    bool IsDiscovery;
};

// CDataSetQuestList: element of PC list 0x7783d0 (V); PS4 {m_Param, m_Detail}.
struct CDataSetQuestList {
    CDataQuestList Param;
    CDataSetQuestDetail Detail;
};

// CDataTutorialQuestList: PC list 0x77b690 (V); PS4 {m_Param, u8 m_ucEnableCancel}.
struct CDataTutorialQuestList {
    CDataQuestList Param;
    u8 EnableCancel;
};

// CDataWorldManageQuestList: PC list 0x77cd60 (V); PS4 {m_Param, u8 m_ucIsTutorialGuide}.
struct CDataWorldManageQuestList {
    CDataQuestList Param;
    u8 IsTutorialGuide;
};

// CDataLotQuestList: element of PC list 0x76dae0 (V); PS4 {m_Param, CQuestContents m_Contents}.
struct CDataLotQuestList {
    CDataQuestList Param;
    CDataQuestContents Contents;
};

// CDataRewardItemDetail: PC list 0x7772a0 (V); PS4 {u32 ItemId, u16 Num, u8 Type}.
struct CDataRewardItemDetail {
    u32 ItemId;
    u16 Num;
    u8 Type;
};

// Season 3 member of CDataTimeGainQuestList: PC 0x75ed50 {u32, list u32, list 0x75edd0 {u32,
// bool}, bool, bool, list u8 0x75e9b0} (V shape), no PS4 counterpart; server: Restrictions
// (lead). Struct and field names open.
struct CDataQuestUnkU32Bool {
    // T014b open (not read), kept unk: CDataTimeGainQuestList_unk_0 list (element +412, count +416,
    // array +428) (...)
    u32 unk_u32;
    // T014b open (not read), kept unk: see unk_u32: only the list count is read (0xed89f0)
    bool unk_bool;
};

// server: Restrictions (lead)
struct CDataTimeGainQuestList_unk_0 {
    // T014b open (no consumer found), kept unk: struct +4 (element +388) is not read by 0xed89f0;
    // the u32/bool list (+412) only gates Quest_res 0x91 'Additional Equipment Rewards', whose text
    // comes from sQuestManager 0xbdf650, so its elements stay unread
    u32 unk_u32;
    // T014b V (consumer); I (name from UI text): 0xed89f0: when the list (element +392) is not
    // empty it adds Quest_res 0x94 QUEST_MSG_MISSION_INFO_NOEQUIP_ABILITY 'The following abilities
    // cannot be equipped' and prints each u32 through 0xb772b0 (ability-name lookup, ids up to
    // (...)
    MtTypedArray<u32> NoEquipAbilityList;
    MtTypedArray<CDataQuestUnkU32Bool> unk_u32_bool_list;   // PC 0x75edd0
    // T014b V (consumer); I (name from UI text): 0xed89f0: struct +48 (element +432) adds Quest_res
    // 0x92 QUEST_MSG_MISSION_INFO_NOEQUIP_ARMOR 'Armor cannot be equipped.'
    bool IsNoEquipArmor;
    // T014b V (consumer); I (name from UI text): 0xed89f0: struct +49 (element +433) adds Quest_res
    // 0x93 QUEST_MSG_MISSION_INFO_NOEQUIP_JEWELRY 'Jewelry cannot be equipped.'
    bool IsNoEquipJewelry;
    // T014b open (no consumer found), kept unk: struct +52 (element +436) is not read by 0xed89f0
    MtTypedArray<CDataCommonU8> unk_u8_list;                // PC 0x75e9b0
};

// Season 3 element of PC list 0x772ef0: {list CDataWalletPoint, list 0x7731b0 {u32, u16}} (V
// shape). Names open.
struct CDataQuestUnkU32U16 {
    // T014b I (consumer of the same layout): 0xed89f0 prints a {u32 +4, u16 +8} list found at quest
    // object +112 (+28 count, +40 array: the offsets of the CDataTimeGainQuestList_unk_1 element,
    // wallet list +4, this list +24) with Quest_res 0xB1 QUEST_MSG_UI_REWARD_TRADE_ITEM (...)
    u32 ItemId;
    // T014b I (consumer of the same layout): the u16 at +8 is the required count in Quest_res 0xB1
    // '%s x%d (Have: %d)' and is compared with the owned count (see unk_u32)
    u16 Num;
};

// server: RequiredItemsList (lead)
struct CDataTimeGainQuestList_unk_1 {
    MtTypedArray<CDataWalletPoint> unk_WalletPointList;
    MtTypedArray<CDataQuestUnkU32U16> unk_u32_u16_list;     // PC 0x7731b0
};

// CDataTimeGainQuestList: PC element 0x77b080 (V); PS4 0x1a248e0 {m_Param, u32 m_unPlayTimeSec,
// b8 x4 (IsNoTimeup, IsJoinCharacter, IsJoinPawn, IsJoinSupportPawn), u8 m_ucJoinPawnNum,
// MtTypedArray<CDataRewardItemDetail>}. Season 3: a fifth bool and two trailing members. Which bool
// is new is open, so the five stay unk_bool_0..4. Two candidate readings (I): PS4 position puts the
// PS4 names on bools 0-3 (new bool 4); the server lead orders them IsNoTimeup, Unk0,
// IsJoinCharacter, IsJoinPawn, Unk1. Capture stream85-marked tcp-stream-11 packet 138774 (11.10.2)
// has bool 1 false beside bools 2 and 3 true and JoinPawnNum 3, which favours the server order
// (bool 1 = IsJoinCharacter would be false); not settled by code (open item: the PC consumer of
// the element).
struct CDataTimeGainQuestList {
    CDataQuestList Param;
    u32 PlayTimeSec;
    // T014b open (no consumer found), kept unk: element +356 is not read by 0xed89f0 nor by the
    // other 16 callers of the getter 0x86b090
    bool unk_bool_0;           // PS4 position: IsNoTimeup; server: IsNoTimeup (lead)
    // T014b V (consumer); I (name from UI text): 0xed89f0 reads element +357 and, when set, shows
    // Quest_res 0x90 QUEST_MSG_MISSION_INFO_NOEQUIP_HEADER 'Equipment restrictions' followed by the
    // restriction lines from unk_Struct_0 (...)
    bool IsEquipRestriction;           // PS4 position: IsJoinCharacter; server: Unk0 (lead)
    // T014b I (consumer, role only): 0xed89f0: element +358 sets bit 1 and +359 sets bit 2 of a
    // mode word (GUI +6980), read next to JoinPawnNum (+361 -> GUI +6984) (...)
    bool unk_bool_2;           // PS4 position: IsJoinPawn; server: IsJoinCharacter (lead)
    // T014b I (consumer, role only): see unk_bool_2: element +359 is bit 2 of the same join mode
    // word
    bool unk_bool_3;           // PS4 position: IsJoinSupportPawn; server: IsJoinPawn (lead)
    // T014b open (no consumer found), kept unk: element +360 is not read by 0xed89f0 nor by the
    // other 16 callers of the getter 0x86b090
    bool unk_bool_4;           // PS4 position: new in Season 3; server: Unk1 (lead)
    u8 JoinPawnNum;
    MtTypedArray<CDataRewardItemDetail> RewardItemDetailList;
    CDataTimeGainQuestList_unk_0 unk_Struct_0;                    // Season 3, PC 0x75ed50; server: Restriction (lead)
    MtTypedArray<CDataTimeGainQuestList_unk_1> unk_List_0;        // Season 3, PC 0x772ef0; server: RequirementList (lead)
};

// CDataSetQuestInfoList: PC element 0x778230 (V); PS4 0x1a1e150. Season 3: a second u64 (which
// one is new: I), wallet and exp lists in place of PS4 u32 DiscoverRewardBonusGold/Exp/Rim, and a
// trailing condition list.
struct CDataSetQuestInfoList {
    u32 QuestScheduleId;
    u32 QuestId;
    // T014b I (consumer): PC 0xbd6b40 (counterpart of PS4
    // sQuestManagerExt::callbackGetSetQuestInfoList: ImageId % 0xC + 1 fallback,
    // QUEST_ID/SCHEDULE_ID): +24 -> nQuest +104 with the MtTime update check (PS4
    // mEndDistributionDate; EndDistributionDate V) (...)
    u64 DistributionStartDate;               // Season 3 (I position); server: OrderDate (lead)
    u64 EndDistributionDate;   // name I (position)
    u32 ImageId;
    u32 BaseLevel;
    u16 ContentJoinItemRank;
    u32 DiscoverRewardItemId;
    MtTypedArray<CDataWalletPoint> DiscoverRewardWalletPoint;  // name I (in place of PS4 DiscoverRewardBonusGold, BonusRim)
    MtTypedArray<CDataQuestExp> DiscoverRewardExp;             // name I (in place of PS4 DiscoverRewardBonusExp)
    u32 QuickPartyPopularity;
    MtTypedArray<CDataCommonU32> SelectRewardItemIdList;
    u8 RandomRewardNum;
    u8 ChargeRewardNum;
    u16 CompleteNum;
    bool IsDiscovery;
    MtTypedArray<CDataQuestEnemyInfo> QuestEnemyInfoList;
    MtTypedArray<CDataQuestLayoutFlagSetInfo> QuestLayoutFlagSetInfoList;
    MtTypedArray<CDataQuestDeliveryItem> DeliveryItemList;
    MtTypedArray<CDataQuestOrderConditionParam> unk_QuestOrderConditionParamList;  // Season 3
};

// CDataQuestId: PC list 0x773f80 (V); PS4 0x1a1ef20 {u32 m_unQuestId} (also 11.89.16 rows 11-12).
struct CDataQuestId {
    u32 QuestId;
};

// CDataPriorityQuest: PC list 0x7735b0 (V); PS4 0x1a1e9e0 (also 11.89.16 row 13).
struct CDataPriorityQuest {
    u32 QuestScheduleId;
    u32 QuestId;
    MtTypedArray<CDataQuestAnnounce> QuestAnnounceList;   // PC 0x773820
    MtTypedArray<CDataQuestProgressWork> WorkList;        // PC 0x7754a0
};

// CDataPriorityQuestSetting: PC list 0x773710 (V); PS4 {u32 m_unCharacterId, list}.
struct CDataPriorityQuestSetting {
    u32 CharacterId;
    MtTypedArray<CDataPriorityQuest> PriorityQuestList;
};

// CDataQuestContentsSituationInfo: PC list 0x773ab0 (V); PS4 0x1a19940.
struct CDataQuestContentsSituationInfo {
    u32 QuestScheduleId;
    u32 QuestId;
};

// CDataQuestPartyBonusInfo: PC 0x774de0 (V); PS4 0x1a2d3e0, same.
struct CDataQuestPartyBonusInfo {
    u32 QuestScheduleId;
    u32 QuestId;
    u16 GoldRatio;
    u16 ExpRatio;
    u16 RimRatio;
    u16 AreaPointRatio;
    u32 Dorb;
    bool IsReceived;
};

// CDataRewardBoxItem / CDataRewardBoxRecord: PC 0x777000 / list 0x777080 (V); PS4 same.
struct CDataRewardBoxItem {
    u32 ItemId;
    u16 Num;
    MtString UID;
    u8 Type;
    bool IsCharge;
    bool IsHelp;
};

struct CDataRewardBoxRecord {
    u32 ListNo;
    u32 QuestId;
    MtTypedArray<CDataRewardBoxItem> RewardItemList;
};

// CDataContentsPlayEnd: PC 0x75ef90 = 7 x u32 + list CDataRewardItemDetail (V); PS4 {u32 Gold,
// Exp, Rim, PlayTimeMillSec, list}. Season 3 adds three u32. Positions I: the only capture
// (T005 23) has the 7th u32 = 1,045,461 and the others 0, and PLAY_START to this notice is
// 1,058 s, so the 7th is the play time in ms; Gold, Exp, Rim keep the first three places.
struct CDataContentsPlayEnd {
    u32 Gold;              // name I (position)
    u32 Exp;               // name I (position)
    u32 Rim;               // name I (position)
    // T014b open (not read), kept unk: packet +0x24. The only consumers: handler 0x7f3270 (reads
    // +0x10) and the notice callback 0xbd49b0 (registered for dti 0x2189794 by sQuestManagerExt at
    // 0xbcee28 (...)
    u32 unk_u32_0;         // Season 3
    // T014b open (not read), kept unk: packet +0x28; see unk_u32_0 (callback 0xbd49b0 reads +0x30,
    // +0x38, +0x44 only)
    u32 unk_u32_1;         // Season 3
    // T014b open (not read), kept unk: packet +0x2C; see unk_u32_0
    u32 unk_u32_2;         // Season 3
    u32 PlayTimeMillSec;   // name I (capture timestamps)
    MtTypedArray<CDataRewardItemDetail> RewardItemDetailList;
};

// CDataContentsPlayStartData: PC 0x75f030 (V); PS4 0x1a2df70 lacks the three bools and the u8
// list (Season 3, names open).
struct CDataContentsPlayStartData {
    u32 KeyId;
    u32 QuestScheduleId;
    u32 QuestId;
    u32 BaseLevel;
    u8 StartPos;
    // T014b open (read, never used), kept unk: read at +21 by 0x75f030; the only caller, handler
    // 0x7f5830 (TIME_GAIN_QUEST_PLAY_START_NTC), uses +12 (via 0x7f5770), +16, +20, +22, +24, +44,
    // +64 and +23 (in 0x7f5770) (...)
    bool unk_bool_0;   // Season 3
    // T014b V (flow); open (stored, no reader): handler 0x7f5830 passes +22 to 0x4d0a10, which
    // stores it at QuestManager(8 = END_CONTENTS, PS4 cEndContentsManager) +233, beside +224
    // (StartPos, PS4 mStartPos) and +232 (set by 0x4d0a20 from 0x4cf6a0() == 2) (...)
    bool unk_bool_1;   // Season 3
    // T014b V (role); name I: 0x7f5770 (PC counterpart of PS4
    // cNetGameServer::OnPacket_S2C_TIME_GAIN_QUEST_PLAY_START_NOTICE 0x36e530:
    // sGame::startEndContents = 0xb61900, then the player and pawn-owner party loop) runs the loop
    // only when +23 == 1: for the own (...)
    bool IsRecoverOcd;   // Season 3
    MtTypedArray<CDataQuestProcessState> QuestProcessStateList;
    MtTypedArray<CDataQuestEnemyInfo> QuestEnemyInfoList;
    MtTypedArray<CDataQuestLayoutFlagSetInfo> QuestLayoutFlagSetInfoList;
    MtTypedArray<CDataCommonU32> QuestPhaseGroupIdList;
    // T014b open (read, never used), kept unk: read at +104 by 0x75e9b0 inside 0x75f030; handler
    // 0x7f5830 passes only +24, +44, +64 to 0x4d07a0 (PS4 cEndContentsManager::registMainTask takes
    // the same three lists); +84 and +104 are never addressed and are destroyed by 0x790380
    MtTypedArray<CDataCommonU8> unk_u8_list;   // Season 3, PC 0x75e9b0
};

// CDataCycleContentsNoticeData: PC 0x761970 (V); PS4 {u32 x4, u64 m_ullEnd, u8 x3, b8 x2, list}.
// Season 3: a second u64; which one is new is I.
struct CDataCycleContentsNoticeData {
    u32 CycleContentsScheduleId;
    u32 QuestScheduleId;
    u32 QuestId;
    u32 CategoryType;
    // T014b V (flow); open (stored, no reader): callback 0x48e9a0 reads per FortDefenseNoticeData
    // element (Common at +8): +12 CycleContentsScheduleId, +24 CategoryType (subcategory), +48
    // NoticeType (0x492610 = setCycleContentsPeriod), +52 IsGetReward (0x4925c0 = (...)
    u64 unk_u64;   // Season 3 (I position)
    u64 End;       // name I (position)
    u8 NoticeType;
    u8 IsSystemNotice;
    u8 PartyMemberNum;
    bool IsPlay;
    bool IsGetReward;
    MtTypedArray<CDataQuestProcessState> QuestProcessStateList;
};

// CDataFortDefenseNoticeData: element of PC list 0x766c00 (V); PS4 {CCycleContentsNoticeData
// m_Common}.
struct CDataFortDefenseNoticeData {
    CDataCycleContentsNoticeData Common;
};

// Season 3 element of PC list 0x77c780 {u32, u32} (V shape), names open.
struct CDataQuestUnkU32U32 {
    // T014b V (role); name I: FORT_DEFENSE_NTC (handler 0x7f047f, reader 0x815860) becomes notice
    // dti 0x21896b4, whose callback 0x48e9a0 (registered at 0x48e5fd (...)
    u32 Rank;
    // T014b V (role); name I: element +8 (getter 0xa3ae00) is formatted '%d' next to the rank label
    // 'S Rank: <VAL DP>' .. 'D Rank: <VAL DP>' in 0xed7c70 / 0xf57fa0: the DP threshold of that
    // rank (captures 0..19000) (...)
    u32 RankPoint;
};

// CDataQuestContentsSituationInfoDetail: PC 0x773c60 (V); PS4 same without the Season 3 list.
struct CDataQuestContentsSituationInfoDetail {
    u32 QuestScheduleId;
    u32 QuestId;
    u32 BaseLevel;
    u16 ContentJoinItemRank;
    u8 NoticeType;
    MtTypedArray<CDataQuestOrderConditionParam> QuestOrderConditionParamList;
    MtTypedArray<CDataRewardItem> RewardItemList;
    u32 ClearTimePointBonus;
    MtTypedArray<CDataQuestUnkU32U32> unk_u32_u32_list;   // Season 3, PC 0x77c780
    bool IsEnable;
};

// CDataItemUIDList: PC writer 0x77fd30 element {MtString, u32} (V); PS4 {m_wstrUID, u32 m_unNum}.
struct CDataItemUIDList {
    MtString UID;
    u32 Num;
};

// CDataGetRewardBoxItem: PC writer 0x77faf0 element {MtString} (V); PS4 {m_wstrUID}.
struct CDataGetRewardBoxItem {
    MtString UID;
};
