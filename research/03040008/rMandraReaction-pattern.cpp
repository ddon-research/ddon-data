#pragma endian little

struct rMandraReaction_InfoBinary_MotDataBinary
{
    s16 MotNoMaybe;
};

struct rMandraReaction_InfoBinary
{
    u32 MotDataCount;
    rMandraReaction_InfoBinary_MotDataBinary MotData[MotDataCount];
};

struct rMandraReaction
{
    char magicString[4];
    u32 version;
    u32 InfoCount;
    u32 RuntimeAllocationSize;
    rMandraReaction_InfoBinary Info[InfoCount];
};

rMandraReaction rmandrareaction_at_0x00 @0x00;