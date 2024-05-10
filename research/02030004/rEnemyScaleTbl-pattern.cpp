#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct MtVector3
{
    float x;
    float y;
    float z;
};

struct cEmScaleTable : MtObject
{
    u32 mBoneNo;
    f32 mFrame;
    MtVector3 mScale;
};

struct rTbl2<cEmScaleTable> : rTbl2Base
{
    u32 mDataNum;
    cEmScaleTable mpData[mDataNum];
};

struct rEmScaleTable : rTbl2<cEmScaleTable>
{
};

rEmScaleTable remscaletable_at_0x00 @0x00;
