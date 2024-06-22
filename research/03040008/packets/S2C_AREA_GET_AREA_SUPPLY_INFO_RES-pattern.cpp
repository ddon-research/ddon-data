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

struct CDataRewardItemInfo
{
    u32 Index;
    u32 ItemId;
    u8 Num;
};

struct CPacket_S2C_GET_AREA_SUPPLY_INFO_RES : CPacket
{
    u32 Error;
    s32 Result;
    u8 SupplyGrade;
    MtTypedArray<CDataRewardItemInfo> RewardItemInfoList;
};

CPacket_S2C_GET_AREA_SUPPLY_INFO_RES S2C_GET_AREA_SUPPLY_INFO_RES @0x00;