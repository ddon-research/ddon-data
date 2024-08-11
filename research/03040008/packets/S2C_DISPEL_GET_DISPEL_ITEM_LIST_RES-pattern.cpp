#pragma endian big

#define b8 bool

struct MtString
{
    u16 strLen;
    char string[strLen];
};

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct MtTypedArray<T>
{
    u32 ArraySize;
    T Arr[ArraySize];
};

enum WalletType : u8
{
    Gold = 0x01,                      // G
    RiftPoints = 0x02,                // R
    BloodOrbs = 0x03,                 // BO
    SilverTickets = 0x04,             // 枚
    GoldenGemstones = 0x05,           // 個
    RentalPoints = 0x06,              // RP
    ResetJobPoints = 0x07,            // JP_RESET => No icon, not testable, unsure
    ResetCraftSkills = 0x08,          // CP_RESET => No icon, not testable, unsure
    HighOrbs = 0x09,                  // HO
    DominionPoints = 0xA,             // DP
    AdventurePassPoints = 0xB,        // BP
    UnknownTickets = 0xC,             // 枚
    BitterBlackMazeResetTicket = 0xD, // 枚
    GoldenDragonMark = 0xE,           // 個
    SilverDragonMark = 0xF,           // 個
    RedDragonMark = 0x10              // 個
};

struct CDataWalletPoint
{
    WalletType Type;
    u32 Value;
};

struct CDataDispelBaseItemData
{
    u32 ItemID;
    u32 Num;
};

struct CDataDispelLotCrest
{
    u32 CrestItemId;
    u8 CrestItemRate;
    u16 Unknown;
};

struct CDataDispelLotColor
{
    u8 Color;
    u8 ColorRate;
};

struct CDataDispelLotPlus
{
    u8 Plus;
    u8 PlusRate;
};

struct CDataDispelLotItem
{
    u32 ItemId;
    u8 ItemRate;
    u8 CrestNum;
    u16 ItemNum;
    u16 Unknown;
};

struct CDataDispelLotData
{
    u32 Id;
    CDataDispelLotItem ItemLot;
    MtTypedArray<CDataDispelLotCrest> CrestLot;
    MtTypedArray<CDataDispelLotColor> ColorLot;
    MtTypedArray<CDataDispelLotPlus> PlusLot;
};

struct CDataDispelBaseItem
{
    u32 Id;
    u32 Unknown1;
    s64 Begin;
    s64 End;
    MtTypedArray<CDataDispelBaseItemData> BaseItemId;
    MtTypedArray<CDataWalletPoint> Cost;
    b8 IsHide;
    MtTypedArray<CDataDispelLotData> LotItemList;
    u32 SortId;
    MtString Label;
    u32 Category;
    u32 Unknown2;
};

struct CPacket_S2C_GET_DISPEL_ITEM_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;

    MtTypedArray<CDataDispelBaseItem> DispelBaseItemList;
};

CPacket_S2C_GET_DISPEL_ITEM_LIST_RES S2C_GET_DISPEL_ITEM_LIST_RES @0x00;