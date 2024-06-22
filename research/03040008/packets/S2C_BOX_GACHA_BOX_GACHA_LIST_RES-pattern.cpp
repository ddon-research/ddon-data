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

struct CDataBoxGachaSettlementInfo
{
    u32 DrawId;
    u32 Id;
    u32 Price;
    u32 BasePrice;
    u8 DrawNum;
    u8 BonusNum;
    u32 PurchaseNum;
    u32 PurchaseMaxNum;
    u32 SpecialPriceNum;
    u32 SpecialPriceMaxNum;
    u32 Unknown1;
};

struct CDataBoxGachaItemInfo
{
    u32 ItemId;
    u32 ItemNum;
    u32 ItemStock;
    u32 Rank;
    u32 Effect;
    f64 Probability;
    u16 DrawNum;
};

struct CDataBoxGachaInfo
{
    u32 Id;
    s64 Begin;
    s64 End;
    bool Unknown1;
    MtString Name;
    MtString Description;
    MtString Detail;
    u8 WeightDispType;
    MtString FreeSpaceText;
    MtString ListAddr;
    MtString ImageAddr;
    MtTypedArray<CDataBoxGachaSettlementInfo> SettlementList;
    MtTypedArray<CDataBoxGachaItemInfo> BoxGachaSets;
};

struct CPacket_S2C_BOX_GACHA_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataBoxGachaInfo> BoxGachaList;
};

CPacket_S2C_BOX_GACHA_LIST_RES S2C_BOX_GACHA_LIST_RES @0x00;