#define f32 float

struct MtObject
{
};

struct cResource
{
    // char magicString[];
    u32 magicVersion;
};

struct rTbl2Base : cResource
{
};

struct rTbl2<T> : rTbl2Base
{
    u32 mDataNum;
    T mpData[mDataNum];
};

struct cCraftSkillBurstData : MtObject
{
    u32 mTotal;
    f32 mSpdRate1;
    f32 mSpdRate2;
    f32 mSpdRate3;
    f32 mSpdRate4;
};

struct rCraftSkillBurst : rTbl2<cCraftSkillBurstData>
{
};
rCraftSkillBurst rcraftskillburst_at_0x00 @0x00;