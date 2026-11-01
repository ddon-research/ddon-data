#pragma endian big

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct CPacket_C2S_CLAN_GET_MY_INFO_REQ : CPacket
{
};

CPacket_C2S_CLAN_GET_MY_INFO_REQ C2S_CLAN_GET_MY_INFO_REQ @0x00;
