// 11.89.16 S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 1. PC handler 0x7f2a20
// (group-11 table key 16/89; notice class "cQuestSvNotJoinLobbyQuestInfo" 0x1a13bad), packet ctor
// 0x78bda0, reader 0x817340 (V). PS4 counterpart by code: CPacket_S2C_JOIN_LOBBY_QUEST_INFO_NOTICE
// ::ReadPacket 0x19d62c0 (same lists minus PC rows 6-7). No error field on PC (P11a G3).
// Every list is a u32-count list. Lists 1, 2, 3, 5, 6 and 8 are empty in every capture, so the
// CDataLightQuestDetail and CDataSetQuestDetail layouts rest on the PC code only.
// packet-id: 11.89.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma pattern_limit 3200000
#pragma array_limit 3200000
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

// CDataLightQuestDetail: PC 0x76d1c0 reads 7 x u32 (V); PS4 has 6 (m_unAreaId, m_unBaseAreaPoint,
// m_unGetCP, m_unOrderLimit, m_unClearNum, m_unBoardType). Which of the 7 is new is unresolved,
// so all stay unk_*.
struct CDataLightQuestDetail {
    u32 unk_u32_0;
    u32 unk_u32_1;
    u32 unk_u32_2;
    u32 unk_u32_3;
    u32 unk_u32_4;
    u32 unk_u32_5;
    u32 unk_u32_6;
};

// Row 1, PC list 0x76d350.
struct CDataLightQuestOrderList {
    CDataQuestOrderList Param;
    CDataLightQuestDetail Detail;
};

// CDataSetQuestDetail: PC 0x778040 (V): u32 x4, list WalletPoint, list QuestExp, u16, u16, u8 x5,
// bool. PS4 has u16 x5 (UndiscoveryGoldRatio, UndiscoveryExpRatio, UndiscoveryRimRatio,
// LeaderCompleteNum, RepeatRewardType) where PC reads two lists and two u16: which u16 survive is
// unresolved.
struct CDataSetQuestDetail {
    u32 ImageId;
    u32 ClearCount;
    u32 ClearCharacterNum;
    u32 BaseAreaPoint;
    MtTypedArray<CDataWalletPoint> unk_wallet_point_list;   // PC 0x77c5a0, Season 3
    MtTypedArray<CDataQuestExp> unk_quest_exp_list;         // PC 0x76c780, Season 3
    u16 unk_u16_0;
    u16 unk_u16_1;
    u8 RepeatRewardValue;
    u8 RepeatRewardCompleteNum;
    u8 RandomRewardNum;
    u8 ChargeRewardNum;
    u8 ProgressBonusNum;
    bool IsDiscovery;
};

// Row 2, PC list 0x7785f0.
struct CDataSetQuestOrderList {
    u32 DistributeId;
    CDataQuestOrderList Param;
    CDataSetQuestDetail Detail;
};

// Row 3 (0x76eb40) and row 8 (0x77b2a0).
struct CDataMainQuestOrderList {
    CDataQuestOrderList Param;
};

// Row 4, PC list 0x77b790.
struct CDataTutorialQuestOrderList {
    CDataQuestOrderList Param;
    u8 EnableCancel;
};

// Row 5, PC list 0x76dc20.
struct CDataLotQuestOrderList {
    CDataQuestOrderList Param;
    u8 LotQuestType;
};

// Row 6 element, PC list 0x770b90 (V; Season 3, no PS4 counterpart).
struct CDataQuestJoinLobbyUnkElement {
    u32 unk_u32;
    s32 unk_s32_0;
    s32 unk_s32_1;
    MtTypedArray<CDataCommonU32> unk_u32_list;          // PC 0x75e8e0
    bool unk_bool;
    MtTypedArray<CDataQuestOrderList> unk_order_list;   // PC 0x770ab0
};

// Row 6, PC list 0x7709a0 (V; Season 3).
struct CDataQuestJoinLobbyUnk {
    u32 unk_u32;
    MtTypedArray<CDataQuestJoinLobbyUnkElement> unk_list;
};

// Row 7 element, PC list 0x76efd0 (V; Season 3; server lead: WildHuntQuestOrderList).
struct CDataQuestJoinLobbyUnkOrderList {
    CDataQuestOrderList Param;
    u32 unk_u32;
    u8 unk_u8;
};

// Row 9, PC list 0x77ce60.
struct CDataWorldManageQuestOrderList {
    CDataQuestOrderList Param;
    u8 IsTutorialGuide;
};

// Row 10, PC list 0x766a00.
struct CDataExpiredQuestList {
    u32 QuestScheduleId;
    u32 QuestId;
};

// Rows 11-12, PC list 0x773f80.
struct CDataQuestId {
    u32 QuestId;
};

// Row 13, PC list 0x7735b0.
struct CDataPriorityQuest {
    u32 QuestScheduleId;
    u32 QuestId;
    MtTypedArray<CDataQuestAnnounce> QuestAnnounceList;   // PC 0x773820
    MtTypedArray<CDataQuestProgressWork> WorkList;        // PC 0x7754a0
};

// Row 14, PC list 0x7592d0.
struct CDataAreaRank {
    u32 AreaID;
    u32 Rank;
};

// Row 15, PC 0x773d30 (struct, not a list).
struct CDataQuestDefine {
    u8 OrderMaxNum;
    u8 ChargeAddOrderNum;
    u8 RewardBoxMaxNum;
    u16 CycleContentsPlaydataRemainDay;
};

struct S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataLightQuestOrderList> LightQuestOrderList;
    MtTypedArray<CDataSetQuestOrderList> SetQuestOrderList;
    MtTypedArray<CDataMainQuestOrderList> MainQuestOrderList;
    MtTypedArray<CDataTutorialQuestOrderList> TutorialQuestOrderList;
    MtTypedArray<CDataLotQuestOrderList> LotQuestOrderList;
    MtTypedArray<CDataQuestJoinLobbyUnk> unk_list_6;                        // Season 3
    MtTypedArray<CDataQuestJoinLobbyUnkOrderList> unk_order_list_7;         // Season 3
    MtTypedArray<CDataMainQuestOrderList> TimeLimitedQuestOrderList;
    MtTypedArray<CDataWorldManageQuestOrderList> WorldManageQuestOrderList;
    MtTypedArray<CDataExpiredQuestList> ExpiredQuestList;
    MtTypedArray<CDataQuestId> MainQuestIdList;
    MtTypedArray<CDataQuestId> TutorialQuestIdList;
    MtTypedArray<CDataPriorityQuest> PriorityQuestList;
    MtTypedArray<CDataAreaRank> AreaRankList;
    CDataQuestDefine QuestDefine;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC packet @ 0x00;
