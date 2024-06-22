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

struct CPacket_C2S_GET_AREA_MASTER_INFO_REQ : CPacket
{
    u32 AreaID;
};

CPacket_C2S_GET_AREA_MASTER_INFO_REQ C2S_GET_AREA_MASTER_INFO_REQ @0x00;