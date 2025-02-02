#define f32 float

struct MtObject
{
};

struct MtVector4
{
    float x;
    float y;
    float z;
    float w;
};

struct MtColor
{
    u32 r;
    u32 g;
    u32 b;
    u32 a;
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

struct cCharacterEditColorDef : cCharacterEditPaletteBase
{
    bool mUse;
    MtVector4 mColor;
    MtColor mUIColor;
};
struct rTbl2<cCharacterEditColorDef> : rTbl2Base
{
    u32 mDataNum;
    cCharacterEditColorDef mpData[mDataNum];
};

struct rCharacterEditColorDef : rTbl2<cCharacterEditColorDef>
{
};

rCharacterEditColorDef rcharactereditcolordef_at_0x00 @0x00;