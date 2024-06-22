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

struct CDataSelectItemInfo
{
    u32 Index;
    u8 Num;
};

struct CPacket_C2S_GET_AREA_SUPPLY_REQ : CPacket
{
    u32 AreaID;
    u8 StorageType;
    MtTypedArray<CDataSelectItemInfo> SelectItemInfoList;
};

CPacket_C2S_GET_AREA_SUPPLY_REQ C2S_GET_AREA_SUPPLY_REQ @0x00;