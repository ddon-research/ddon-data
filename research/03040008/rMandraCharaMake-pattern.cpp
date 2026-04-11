#pragma endian little

struct rMandraCharaMake_InfoBinary_CharDataBinary_SubRecord
{
    u8 Unk0;
    u8 Unk1;
    u16 Unk2;
    s16 Unk3;
    u16 Unk4;
};

struct rMandraCharaMake_InfoBinary_CharDataBinary
{
    u32 MandragoraSpeciesId;
    s16 Unk1;
    u16 Unk2;
    u16 Unk3;
    s16 Unk4; 
    u16 MandragoraSubspecies; // subspecies type e.g. value 3 seems to be Mandragora Houseplant, value 4 seems to be Mandra Flower
    u16 MandragoraSubspeciesColorVariant; // e.g. Color variations like Mandra Boquet - Yellow/Purple/White
    s16 MandragoraSpecialSpeciesUnknown;
    u16 Unk8;
    u16 Unk9;
    s16 Unk10;
    rMandraCharaMake_InfoBinary_CharDataBinary_SubRecord SubRecords[3];
};

struct rMandraCharaMake_InfoBinary
{
    u32 InfoIdMaybe;
    u32 CharDataCount;
    rMandraCharaMake_InfoBinary_CharDataBinary CharData[CharDataCount];
};

struct rMandraCharaMake
{
    char magicString[4];
    u32 version;
    u32 InfoCount;
    u32 RuntimeAllocationSize;
    rMandraCharaMake_InfoBinary Info[InfoCount];
};

rMandraCharaMake rmandracharamake_at_0x00 @0x00;