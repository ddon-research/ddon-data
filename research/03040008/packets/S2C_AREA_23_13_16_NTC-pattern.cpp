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

struct CPacket_S2C_AREA_23_13_16_NTC : CPacket
{
    u32 AreaId;
    u32 AreaPoints;
};

CPacket_S2C_AREA_23_13_16_NTC S2C_AREA_23_13_16_NTC @0x00;