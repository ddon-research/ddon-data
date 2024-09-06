#pragma endian big

#define b8 bool
#define f64 double

struct MtTypedArray<T>
{
    u32 ArraySize;
    T Arr[ArraySize];
};

struct MtString
{
    u16 strLen;
    char string[strLen];
};

struct CPacket
{
    u8 Group;
    u16 Id;
    u8 SubId;
    u8 Source;
    u32 PacketCounter;
};

struct CDataCommonU32
{
    u32 value;
};

struct CDataFurnitureLayout
{
    u32 ItemID;
    u32 unOmID;
    u8 LayoutID;
};

struct CDataMyRoomOption
{
    MtTypedArray<CDataCommonU32> BgmAcquirementNoList;
    u32 BgmAcquirementNo;
    u32 Unk0;
};

struct CPacket_S2C_MY_ROOM_FURNITURE_LIST_GET_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataFurnitureLayout> FurnitureList;
    CDataMyRoomOption MyRoomOption;
};

CPacket_S2C_MY_ROOM_FURNITURE_LIST_GET_RES S2C_MY_ROOM_FURNITURE_LIST_GET_RES @0x00;