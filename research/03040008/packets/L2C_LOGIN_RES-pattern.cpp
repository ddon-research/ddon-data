#pragma endian big

struct MtString
{
    u16 strLen;
    char string[strLen];
};

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct CPacket_L2C_LOGIN_RES : CPacket
{

    u32 Error;
    u32 Result;
    MtString OnetimeToken;
    u8 pad[14];
};

CPacket_L2C_LOGIN_RES L2C_LOGIN_RES @0x00;