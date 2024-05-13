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
    MtString m_wstrOnetimeToken;
    u8 m_ucPlatform;
};

CPacket_C2L_LOGIN_REQ cpacket_c2l_login_req_at_0x00 @0x00;