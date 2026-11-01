// 11.15.2 S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 5. PC handler 0x7f0b70
// (string 0x1bc8458), ctor 0x78b350 (11, 15, 2), reader 0x815cb0 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_CYCLE_CONTENTS_NEWS_LIST_RES 0x2ebf90; its CDataCycleContentsNews ends after
// m_bIsCreateRanking and its CDataCycleContentsRank is {u8, u32, u32, u64}: the rest is Season 3.
// Body: s32 Error [, s32 Result, list] (P11a G1).
// packet-id: 11.15.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

// PC list 0x761850 {u32, u32, u16, u8}.
struct CDataCycleContentsNewsDetail {
    u32 QuestId;
    u32 BaseLevel;
    u16 ContentJoinItemRank;
    u8 SituationLevel;
};

// PC list 0x761d90, element 0x761e80 {u8, u32, u32, u64, u32, u8}; the last two are Season 3.
struct CDataCycleContentsRank {
    u8 Type;
    u32 Rank;
    u32 Score;
    u64 UpdateDate;
    u32 unk_u32;
    u8 unk_u8;
};

// PC list 0x774e80 {u32, s64, s64} (V; both R.s64), Season 3.
struct CDataCycleContentsUnk {
    u32 StageNo;               // name from the earlier pattern (I)
    s64 unk_s64_0;
    s64 unk_s64_1;
};

// PC list 0x7615e0.
struct CDataCycleContentsNews {
    u32 CycleContentsScheduleId;
    u64 Begin;
    u64 End;
    u8 Category;
    u32 CategoryType;          // CycleNo
    MtTypedArray<CDataRewardItem> RewardItemList;            // PC 0x7771b0
    MtTypedArray<CDataCycleContentsNewsDetail> DetailList;
    MtTypedArray<CDataCycleContentsRank> CycleContentsRankList;
    u32 TotalPoint;
    u32 PlayNum;
    bool IsCreateRanking;
    // Season 3 from here (no PS4 counterpart); the u64 names are the earlier pattern's (I).
    MtTypedArray<CDataQuestEnemyInfo> EnemyInfo;             // PC 0x773d90
    MtTypedArray<CDataCycleContentsUnk> unk_list;
    u64 Begin1;
    u64 Interval1;
    u64 Interval2;
    u64 Interval3;
    u64 Interval4;
    u64 End2;
};

struct S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCycleContentsNews> CycleContentsNewsList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES packet @ 0x00;
