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

struct cActivateDragonSkill : MtObject
{
    u8 mId;
    u8 mUnknown1;
    u8 mUnknown2;
    u8 mUnknown3;
    u8 mUnknown4;
};

struct rActivateDragonSkill : rTbl2<cActivateDragonSkill>
{
};

rActivateDragonSkill ActivateDragonSkill @0x00;