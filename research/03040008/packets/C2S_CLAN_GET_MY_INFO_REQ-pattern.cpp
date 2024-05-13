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

CPacket_C2S_CLAN_GET_MY_INFO_REQ cpacket_c2s_clan_get_my_info_req_at_0x00 @0x00;
