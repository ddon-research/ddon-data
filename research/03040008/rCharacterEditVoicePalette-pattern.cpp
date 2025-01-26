struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cCharacterEditPaletteBase : MtObject
{
    u32 mIconNo;
    u32 mReleaseVersion;
    u32 mFlag;
};

struct cCharacterEditVoicePalette : cCharacterEditPaletteBase
{
    u32 mUID;
    u32 mVoiceFlag;
    u16 mNameIndex;
};

struct rTbl2<Class> : rTbl2Base
{
    u32 mDataNum;
    cCharacterEditVoicePalette mpData[mDataNum];
};

struct rCharacterEditVoicePalette : rTbl2<cCharacterEditVoicePalette>
{
};

rCharacterEditVoicePalette rcharactereditvoicepalette_at_0x00 @0x00;