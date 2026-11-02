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

// CDataLightQuestDetail, CDataSetQuestDetail, CDataQuestId (rows 11-12, PC 0x773f80) and
// CDataPriorityQuest (row 13, PC 0x7735b0) live in Quest.hexpat since 006 T005b (moved unchanged).

// Row 1, PC list 0x76d350.
struct CDataLightQuestOrderList {
    CDataQuestOrderList Param;
    CDataLightQuestDetail Detail;
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
    // T014b V (consumer); I (role: package sequence key): 0x597310 stores element +4 at
    // cPackageSequence +8; 0x5983a0 finds an existing sequence by (+4 PackageId, +8 this value) and
    // stores it at task +584 (0x9d2b10) for every order of the element
    u32 unk_u32;
    // T014b V (consumer); I (name): 0x597310 stores element +8 at cPackageSequence +16; when the
    // sequence exists 0x5983a0 writes it to +16 clamped to +12 (unk_s32_1), i.e. a current count
    // bounded by a maximum
    s32 Progress;
    // T014b V (consumer); I (name): 0x597310 stores element +12 at cPackageSequence +12, the upper
    // bound 0x5983a0 applies to +16 (unk_s32_0)
    s32 ProgressMax;
    // T014b V (consumer); I (name): 0x597310 makes one dti
    // cPackageQuestManager::cPackageSequence::cClientNpc object per list entry with the u32 at +4
    // (DTI name; the property mClientInfo of rPackageQuestInfo 0xabe130 is the resource
    // counterpart)
    MtTypedArray<CDataCommonU32> ClientNpcList;          // PC 0x75e8e0
    // T014b open (not read), kept unk: 0x5983a0 and 0x597310 read element +4, +8, +12, +16 (list)
    // and +40 (order list) but not +36; the sequence ctor sets its own +36 to 0
    bool unk_bool;
    MtTypedArray<CDataQuestOrderList> unk_order_list;   // PC 0x770ab0
};

// Row 6, PC list 0x7709a0 (V; Season 3).
struct CDataQuestJoinLobbyUnk {
    // T014b V (consumer); I (name): 0xbd73c0 passes packet +116 to 0x5983a0 of quest manager kind
    // 11, which allocates dti cPackageQuestManager::cPackageSequence objects (0x597310) and stores
    // this u32 at sequence +4 and at task +580 (0x9d2b10) (...)
    u32 PackageId;
    MtTypedArray<CDataQuestJoinLobbyUnkElement> unk_list;
};

// Row 7 element, PC list 0x76efd0 (V; Season 3; server lead: WildHuntQuestOrderList).
struct CDataQuestJoinLobbyUnkOrderList {
    CDataQuestOrderList Param;
    // T014b open (V store; no reader of the member found), kept unk: the notice callback 0xbd73c0
    // (registered for dti__1502 at 0xbcefa3, code not made a function; read as raw instructions)
    // passes packet +136 to registTask 0x597160 of quest manager kind 12 (...)
    u32 unk_u32;
    // T014b open (V store; no reader of the member found), kept unk: stored by 0x64dc20 at task
    // param +404 beside unk_u32 (+408); 0x5da6b0 stores 0 there for another list, so it reads as a
    // kind selector for the u32; no reader found
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
