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

struct cCraftSkillStrData : MtObject
{
    u32 mMainRate;
    u32 mSubRate;
    u32 mMainGreatRate;
    u32 mSubGreatRate;
};

struct rCraftSkillStr : rTbl2<cCraftSkillStrData>
{
};

rCraftSkillStr rcraftskillstr_at_0x00 @0x00;