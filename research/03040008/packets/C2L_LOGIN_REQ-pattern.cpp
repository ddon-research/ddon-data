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

struct CPacket_C2L_LOGIN_REQ : CPacket
{
    MtString OnetimeToken;
    u8 Platform;
};

CPacket_C2L_LOGIN_REQ C2L_LOGIN_REQ @0x00;