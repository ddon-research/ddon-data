#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cLargeCameraParam : MtObject
{
    u32 mEmId;
    f32 mRange1;
    f32 mRange2;
    u32 mCamera;
    bool mGroup;
};
struct rTbl2<cLargeCameraParam> : rTbl2Base
{
    u32 mDataNum;
    cLargeCameraParam mpData[mDataNum];
};

struct rLargeCameraParam : rTbl2<cLargeCameraParam>
{
};

rLargeCameraParam rlargecameraparam_at_0x00 @0x00;