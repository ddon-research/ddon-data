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

struct cDragonSkillEnhanceParam : MtObject
{
    u8 mUnknown;
};

struct rDragonSkillEnhanceParam : rTbl2<cDragonSkillEnhanceParam>
{
};

rDragonSkillEnhanceParam DragonSkillEnhanceParam @0x00;