#pragma endian big

#define b8 bool
#define StageInfoVec MtTypedArray<CDataStageInfo>
#define CStageAttribute CDataStageAttribute

struct MtTypedArray<T>
{
    u32 ArraySize;
    T Arr[ArraySize];
};

struct CPacket
{
    u8 Group;
    u16 Id;
    u8 SubId;
    u8 Source;
    u32 PacketCounter;
};

struct CDataStageAttribute
{
    b8 IsSolo;
    b8 IsEnablePartyFunc;
    b8 IsAdventureCountKeep;
    b8 IsEnableCraft;
    b8 IsEnableStorage;
    b8 IsEnableStorageInCharge;
    b8 IsNotSessionReturn;
    b8 IsEnableBaggage;
    b8 IsClanBase;
    b8 Unknown1;
    b8 Unknown2;
};

struct CDataStageInfo
{
    u32 ID;
    u32 StageNo;
    u32 RandomStageGroupID;
    u32 Type;
    CStageAttribute StageAttribute;
    b8 IsAutoSetBloodEnemy;
};

struct CPacket_S2C_GET_STAGE_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    StageInfoVec StageInfoList;
};

CPacket_S2C_GET_STAGE_LIST_RES S2C_GET_STAGE_LIST_RES @0x00;