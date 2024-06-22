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

struct CDataAreaBaseInfo
{
    u32 AreaID;
    u32 Rank;
    u32 CurrentPoint;
    u32 NextPoint;
    u32 WeekPoint;
    b8 CanRankUp;
    u32 ClanAreaPoint;
    u32 ClanAreaPointBorder;
    b8 CanReceiveSupply;
};

struct CPacket_S2C_GET_AREA_BASE_INFO_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataAreaBaseInfo> m_AreaBaseInfoList;
};

CPacket_S2C_GET_AREA_BASE_INFO_LIST_RES S2C_GET_AREA_BASE_INFO_LIST_RES @0x00;