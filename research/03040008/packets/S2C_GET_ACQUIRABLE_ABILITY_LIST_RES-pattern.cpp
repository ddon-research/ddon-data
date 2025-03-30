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

struct CDataAbilityLevelParam
{
  u8 Lv;
  u32 RequireJobLevel;
  u32 RequireJobPoint;
  b8 IsRelease;
};

struct CDataAbilityParam
{
  u32 AbilityNo;
  u8 Job;
  u8 Category;
  u8 SortCategory;
  u8 Type;
  u32 Cost;
  MtTypedArray<CDataAbilityLevelParam> Param;
};

struct nUserSession_CPacket_S2C_GET_ACQUIRABLE_ABILITY_LIST_RES : CPacket
{
  u32 Error;
  if(Error != 0){
    s16 Result;
  }else{
    s32 Result;
  }
  MtTypedArray<CDataAbilityParam> AbilityParamList;
};

nUserSession_CPacket_S2C_GET_ACQUIRABLE_ABILITY_LIST_RES nusersession_cpacket_s2c_get_acquirable_ability_list_res_at_0x00 @ 0x00;