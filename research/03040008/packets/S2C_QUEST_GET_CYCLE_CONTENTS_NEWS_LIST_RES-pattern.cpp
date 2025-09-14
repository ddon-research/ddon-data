#pragma endian big

#define b8 bool

struct MtTypedArray<T>
{
    u32 ArraySize;
    T Arr[ArraySize];
};

struct CPacket
{
    u8 Group;
    u16 Id;
    u8 SubId;
    u8 Source;
    u32 PacketCounter;
};

struct CDataRewardItem
{
    u32 ItemId;
    u16 Num;
};

struct CDataCycleContentsNewsDetail
{
    u32 QuestId;
    u32 BaseLevel;
    u16 ContentJoinItemRank;
    u8 SituationLevel;
};

struct CDataCycleContentsRank
{
    u8 Type;
    u32 Rank;
    u32 Score;
    u64 UpdateDate;
    u32 Unknown1;
    u8 Unknown2;
};

struct CDataQuestEnemyInfo
{
    u32 GroupId;
    u32 Unk0;
    u16 Lv;
    bool IsPartyRecommend;
};

struct CDataCycleContentsUnk
{
    u32 StageNo;
    u64 Unk1;
    u64 Unk2;
};

struct CDataCycleContentsNews
{
    u32 CycleContentsScheduleId;
    u64 Begin;
    u64 End;
    u8 Category;
    u32 CategoryType; // CycleNo
    MtTypedArray<CDataRewardItem> RewardItemList;
    MtTypedArray<CDataCycleContentsNewsDetail> DetailList;
    MtTypedArray<CDataCycleContentsRank> CycleContentsRankList;
    u32 TotalPoint;
    u32 PlayNum;
    b8 IsCreateRanking;
    MtTypedArray<CDataQuestEnemyInfo> EnemyInfo;
    MtTypedArray<CDataCycleContentsUnk> Unk0;
    u64 Begin1;
    u64 Interval1;
    u64 Interval2;
    u64 Interval3;
    u64 Interval4;
    u64 End2;
};

struct CPacket_S2C_GET_CYCLE_CONTENTS_NEWS_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;

    MtTypedArray<CDataCycleContentsNews> CycleContentsNewsList;
};

CPacket_S2C_GET_CYCLE_CONTENTS_NEWS_LIST_RES S2C_GET_CYCLE_CONTENTS_NEWS_LIST_RES @0x00;
