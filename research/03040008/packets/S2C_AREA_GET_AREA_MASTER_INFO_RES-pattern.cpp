#pragma endian big

#define b8 bool
#define CDataCommonU32 u32

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

struct CDataSupplyItem
{
    u32 ItemID;
    u16 ItemNum;
};

struct CDataBorderSupplyItem
{
    u32 MinAreaPoint;
    MtTypedArray<CDataSupplyItem> SupplyItemList;
};

struct CDataAreaRankUpQuestInfo
{
    u32 Rank;
    u32 QuestID;
};

struct CPacket_S2C_GET_AREA_MASTER_INFO_RES : CPacket
{
    u32 Error;
    s32 Result;
    u32 AreaId;
    u32 Rank;
    u32 Point;
    u32 WeekPoint;
    u32 LastWeekPoint;
    u32 ToNextPoint;
    MtTypedArray<CDataCommonU32> ReleaseList;
    b8 CanReciveSupply;
    b8 CanRankUp;
    MtTypedArray<CDataBorderSupplyItem> SupplyItemInfoList;
    MtTypedArray<CDataAreaRankUpQuestInfo> AreaRankUpQuestInfoList;
};

CPacket_S2C_GET_AREA_MASTER_INFO_RES S2C_GET_AREA_MASTER_INFO_RES @0x00;