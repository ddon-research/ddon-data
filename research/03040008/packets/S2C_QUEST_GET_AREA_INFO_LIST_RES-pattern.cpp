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

struct CDataAreaInfoList
{
    u32 AreaId;
    u8 Weather;
    u8 UndiscoveredQuestNum;
    u8 HighDiffcultyQuestNum;
    b8 IsBonus;
};

struct CPacket_S2C_GET_AREA_INFO_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataAreaInfoList> AreaInfoList;
};

CPacket_S2C_GET_AREA_INFO_LIST_RES S2C_GET_AREA_INFO_LIST_RES @0x00;