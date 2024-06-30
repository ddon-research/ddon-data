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

struct cDragonSkillParam : MtObject
{
    u8 mId;
    u32 mUnknown;
    u32 mMsgIndex;
};

struct rDragonSkillParam : rTbl2<cDragonSkillParam>
{
};

rDragonSkillParam DragonSkillParam @0x00;