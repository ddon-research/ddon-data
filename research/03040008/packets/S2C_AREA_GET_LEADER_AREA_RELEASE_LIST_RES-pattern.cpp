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

struct CDataReleaseAreaInfoSet
{
    u32 AreaID;
    MtTypedArray<CDataCommonU32> ReleaseList;
};

struct CPacket_S2C_GET_LEADER_AREA_RELEASE_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataReleaseAreaInfoSet> ReleaseAreaInfoSetList;
};

CPacket_S2C_GET_LEADER_AREA_RELEASE_LIST_RES S2C_GET_LEADER_AREA_RELEASE_LIST_RES @0x00;