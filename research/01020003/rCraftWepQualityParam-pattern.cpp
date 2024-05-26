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

struct cCraftWepQualityParamData : MtObject
{
    u32 mItemRank;
    u32 mWepCategory;
    u32 mAttack;
    u32 mMagicAttack;
    u32 mPowerRev;
    u32 mStanSav;
    u32 mChance;
    u32 mShieldStagger;
    u32 mShieldStamina;
    u32 mTShieldStorage;
    u8 mLv;
};
struct rCraftWepQualityParam : rTbl2<cCraftWepQualityParamData>
{
};

rCraftWepQualityParam rcraftwepqualityparam_at_0x00 @0x00;