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

    u32 m_usError;
    u32 m_nResult;
    MtString m_wstrOnetimeToken;
    u32 Unknown1;
    u16 Unknown2;
    u32 Unknown3;
    u32 Unknown4;
};

CPacket_L2C_LOGIN_RES cpacket_l2c_login_res_at_0x00 @0x00;