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

struct cCraftSkillGainData : MtObject
{
    u32 mMainPoint;
    u32 mSubPoint;
    u32 mRate;
};

struct rCraftSkillGain : rTbl2<cCraftSkillGainData>
{
};

rCraftSkillGain rcraftskillgain_at_0x00 @0x00;