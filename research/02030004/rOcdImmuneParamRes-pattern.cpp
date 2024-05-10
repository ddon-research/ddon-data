#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};
struct cOcdImmuneParamRes : MtObject
{
    u32 mOcdUID;
    f32 mImmuneRate;
    u32 mImmuneNum;
};

struct rTbl2<cOcdImmuneParamRes> : rTbl2Base
{
    u32 mDataNum;
    cOcdImmuneParamRes mpData[mDataNum];
};

struct rOcdImmuneParamRes : rTbl2<cOcdImmuneParamRes>
{
};
rOcdImmuneParamRes rocdimmuneparamres_at_0x00 @0x00;