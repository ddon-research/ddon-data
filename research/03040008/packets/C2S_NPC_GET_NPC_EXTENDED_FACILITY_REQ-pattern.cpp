#pragma endian big

struct CPacket
{
    u8 Group;
    u16 Id;
    u8 SubId;
    u8 Source;
    u32 PacketCounter;
};

struct CPacket_C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ : CPacket
{
    u32 NpcID;
};

CPacket_C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ @0x00;