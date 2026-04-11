#pragma endian little

struct rMandraMotCombine_InfoBinary_MotDataBinary
{
    u16 MotIdMaybe;
    s16 Unk0;
    s16 Unk1;
    s16 Unk2;
    s16 Unk3;
    s16 Unk4;
    s16 Unk5;
    s16 Unk6;
    s16 Unk7;
    s16 Unk8;
    s16 Unk9;
    s16 Unk10;
    s16 Unk11;
    s16 Unk12;
    u8 UnkByte0;
    u8 UnkByte1;
    u8 UnkByte2;
    u8 UnkByte3;
};

struct rMandraMotCombine_InfoBinary
{
    u32 InfoIdMaybe;
    u32 MotDataCount;
    rMandraMotCombine_InfoBinary_MotDataBinary MotData[MotDataCount];
};

struct rMandraMotCombine
{
    char magicString[4];
    u32 version;
    u32 InfoCount;
    u32 RuntimeAllocationSize;
    rMandraMotCombine_InfoBinary Info[InfoCount];
};

rMandraMotCombine rmandramotcombine_at_0x00 @0x00;