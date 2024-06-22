#pragma endian big

#define b8 bool
#define CDataCommonU32 u32

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

struct CDataAreaQuestHint
{
    u32 ScheduleID;
    u32 Price;
    b8 IsSold;
};

struct CPacket_S2C_GET_AREA_QUEST_HINT_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataAreaQuestHint> AreaQuestHintList;
};

CPacket_S2C_GET_AREA_QUEST_HINT_LIST_RES S2C_GET_AREA_QUEST_HINT_LIST_RES @0x00;