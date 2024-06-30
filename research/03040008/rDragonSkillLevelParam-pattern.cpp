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

struct cDragonSkillLevelParam : MtObject
{
    u8 mId;
    u8 mLv;
    u32 mUnknown;
};

struct rDragonSkillLevelParam : rTbl2<cDragonSkillLevelParam>
{
};

rDragonSkillLevelParam DragonSkillLevelParam @0x00;