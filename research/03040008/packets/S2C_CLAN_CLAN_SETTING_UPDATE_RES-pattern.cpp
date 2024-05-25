#pragma endian big

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct CPacket_S2C_CLAN_SETTING_UPDATE_RES : CPacketDataBase
{
  u32 m_usError;
  s32 m_nResult;
};

