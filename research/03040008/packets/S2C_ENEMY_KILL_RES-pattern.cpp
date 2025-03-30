#pragma endian big

struct MtTypedArr<T>
{
    u32 arraySize;
    T arr[arraySize];
};

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct nUserSession_CPacket_S2C_ENEMY_KILL_RES : CPacket
{
    u32 Error;
    u32 Result;
    u32 EnemyID;
    u32 KillNum;
};

nUserSession_CPacket_S2C_ENEMY_KILL_RES nusersession_cpacket_s2c_enemy_kill_res_at_0x00 @0x00;