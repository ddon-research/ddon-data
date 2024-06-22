#pragma endian big

#define b8 bool

#define SpotEnemyInfoVec MtTypedArray<CDataSpotEnemyInfo>
#define SpotItemInfoVec MtTypedArray<CDataSpotItemInfo>

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

struct CDataSpotEnemyInfo
{
    u32 EnemyID;
    u8 EnemyLv;
};

struct CDataSpotItemInfo
{
    u32 ItemId;
    u8 PawnTakeRate;
};

struct CDataSpotInfoS3
{
    // These always correspond to the last spot ID in ams18 - ams21
    u32 SpotID;
    bool DeadlineReached;
    u64 Deadline;
};

struct CDataSpotInfo
{
    u32 SpotID;
    u32 TextIndex;
    u32 StageID;
    b8 IsRelease;
    b8 IsNew;
    SpotEnemyInfoVec SpotEnemyInfoList;
    SpotItemInfoVec SpotItemInfoList;
    u32 QuickPartyPopularity;
};

struct CPacket_S2C_GET_SPOT_INFO_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataSpotInfo> SpotInfoList;
    // new season 3-specific structures, some form of timed delivery / daily reset?
    u32 Unknown1;
    MtTypedArray<CDataSpotInfoS3> SpotInfoListSeason3;
};

CPacket_S2C_GET_SPOT_INFO_LIST_RES S2C_GET_SPOT_INFO_LIST_RES @0x00;