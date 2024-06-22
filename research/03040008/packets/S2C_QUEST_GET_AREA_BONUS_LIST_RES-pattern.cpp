#pragma endian big

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

struct CDataAreaBonus
{
    u32 AreaId;
    u16 GoldRatio;
    u16 ExpRatio;
    u16 RimRatio;
    u16 AreaPointRatio;
    u16 UnknownRatio;
};

struct CPacket_S2C_GET_AREA_BONUS_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataAreaBonus> m_AreaBonusList;
};

CPacket_S2C_GET_AREA_BONUS_LIST_RES S2C_GET_AREA_BONUS_LIST_RES @0x00;