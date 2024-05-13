#define f32 float
struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};
struct cEmWarpParam : MtObject
{
    f32 mWarpDist[3];
    f32 mGroundCheckDist;
    bool mIsGroundCheckExtend;
};
struct rTbl2<cEmWarpParam> : rTbl2Base
{
    u32 mDataNum;
    cEmWarpParam mpData[mDataNum];
};

struct rEmWarpParam : rTbl2<cEmWarpParam>
{
};
rEmWarpParam remwarpparam_at_0x00 @0x00;