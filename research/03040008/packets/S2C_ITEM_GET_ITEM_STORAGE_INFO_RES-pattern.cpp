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

struct CDataGameItemStorage
{
    u8 StorageType;
};

struct CDataGameItemStorageInfo
{
    CDataGameItemStorage GameItemStorage;
    u16 UsedSlotNum;
    u16 MaxSlotNum;
};

struct CPacket_S2C_GET_ITEM_STORAGE_INFO_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataGameItemStorageInfo> GameItemStorageInfoList;
};

CPacket_S2C_GET_ITEM_STORAGE_INFO_RES S2C_ITEM_GET_ITEM_STORAGE_INFO_RES @0x00;