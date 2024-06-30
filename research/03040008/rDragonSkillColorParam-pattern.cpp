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

struct cDragonSkillColorParam : MtObject
{
    u8 mId;
    u16 mUnknown1;
    u8 mUnknown2;
};

struct rDragonSkillColorParam : rTbl2<cDragonSkillColorParam>
{
};

rDragonSkillColorParam DragonSkillColorParam @0x00;