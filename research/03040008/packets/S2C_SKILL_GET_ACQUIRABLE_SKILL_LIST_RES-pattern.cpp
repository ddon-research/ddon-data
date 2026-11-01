#pragma endian big

#define b8 bool

struct MtTypedArray<T>
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

struct CDataSkillLevelParam
{
    u8 Lv;
    u32 RequireJobLevel;
    u32 RequireJobPoint;
    b8 IsRelease;
};

struct CDataSkillParam
{
    u32 SkillNo;
    u8 Job;
    u8 Type;
    MtTypedArray<CDataSkillLevelParam> Param;
};

struct nUserSession_CPacket_S2C_GET_ACQUIRABLE_SKILL_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataSkillParam> SkillParamList;
};

nUserSession_CPacket_S2C_GET_ACQUIRABLE_SKILL_LIST_RES nusersession_cpacket_s2c_get_acquirable_skill_list_res_at_0x00 @0x00;