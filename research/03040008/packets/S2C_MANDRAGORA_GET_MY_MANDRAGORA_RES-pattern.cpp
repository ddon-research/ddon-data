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

struct CDataCommonU8
{
    u8 Unk0;
};

struct CDataMyMandragoraFurnitureItem
{
    u32 MandragoraId;
    u32 FurnitureItemId;
};

struct CDataMyMandragoraResUnk1Unk7Unk2
{
    u32 Unk0;
    u16 Unk1;
};

struct CDataMyMandragoraResUnk1Unk7
{
    u32 Unk0;
    u32 Unk1;
    MtTypedArray<CDataMyMandragoraResUnk1Unk7Unk2> Unk2;
    s64 Unk3;
};

struct CDataMyMandragora
{
    u32 Unk0;
    u8 Unk1;
    u32 MandragoraIdMaybe;
    MtString MandragoraName;
    u32 Unk4;
    s64 Unk5;
    u32 Unk6;
    CDataMyMandragoraResUnk1Unk7 Unk7;
};

struct CDataMyMandragoraCraftCategory
{
    u8 CategoryId;
    MtString CategoryName; // UTF-8 encoded
};

struct CDataMyMandragoraResUnk3
{
    u8 Unk0;
    u32 Unk1;
};

struct CDataMyMandragoraFertilizerItem
{
    u32 ItemId;
    u32 ItemNum;
};

struct CDataMyMandragoraBreedType
{
    u32 BreedId;
    MtString BreedName;
    u32 DiscoveredBreedNumMaybe;
};

struct CDataMyMandragoraRarityLevel
{
    u32 RarityId;
    MtString Rarity;
};

struct CPacket_S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataMyMandragoraFurnitureItem> MandragoraFurnitureItemList;
    MtTypedArray<CDataMyMandragora> MandragoraList;
    MtTypedArray<CDataMyMandragoraCraftCategory> MandragoraCraftCategoriesMaybe;
    MtTypedArray<CDataMyMandragoraResUnk3> Unk3;
    MtTypedArray<CDataMyMandragoraFertilizerItem> MandragoraFertilizerItemList;
    u32 MandragoraCultivationMaterialMaxMaybe;
    MtTypedArray<CDataMyMandragoraBreedType> MandragoraBreedTypeList;
    MtTypedArray<CDataMyMandragoraRarityLevel> RarityLevelList;
    MtTypedArray<CDataCommonU8> FreeMandragoraIdListMaybe;
    u32 Unk9;
};

CPacket_S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES @0x00;
