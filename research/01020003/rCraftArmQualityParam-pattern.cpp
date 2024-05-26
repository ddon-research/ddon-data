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

struct cCraftArmQualityParamData : MtObject
{
    u32 mItemRank;
    u32 mEquip;
    u32 mDefense;
    u32 mMagicDefense;
    u32 mDurability;
    u8 mLv;
};
struct rCraftArmQualityParam : rTbl2<cCraftArmQualityParamData>
{
};

rCraftArmQualityParam rcraftarmqualityparam_at_0x00 @0x00;