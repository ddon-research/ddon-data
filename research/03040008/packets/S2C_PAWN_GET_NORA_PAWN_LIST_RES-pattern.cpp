#pragma endian big

#define b8 bool
#define f64 double

struct MtTypedArray<T>
{
    u32 ArraySize;
    T Arr[ArraySize];
};

struct MtString
{
    u16 strLen;
    char string[strLen];
};

struct CPacket
{
    u8 Group;
    u16 Id;
    u8 SubId;
    u8 Source;
    u32 PacketCounter;
};

struct CDataPawnCraftSkill
{
    u8 Type;
    u32 Level;
};

struct CDataPawnListData
{
    u8 Job;
    u32 Level;
    u32 CraftRank;
    MtTypedArray<CDataPawnCraftSkill> PawnCraftSkillList;
    u32 CommentSize;
    u64 LatestReturnDate;
};

struct CDataRegisterdPawnList
{
    s32 PawnId;
    MtString Name;
    u8 Sex;
    u32 RentalCost;
    u64 Updated;
    CDataPawnListData PawnListData;
};

struct CPacket_S2C_GET_NORA_PAWN_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataRegisterdPawnList> NoraPawnList;
};

CPacket_S2C_GET_NORA_PAWN_LIST_RES S2C_GET_NORA_PAWN_LIST_RES @0x00;