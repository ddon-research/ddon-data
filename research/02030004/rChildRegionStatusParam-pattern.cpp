#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct MtVector3
{
    float x;
    float y;
    float z;
};

struct cChildRegionStatusParam : MtObject
{
    u32 mNo;
    u32 mParentNo[2];
    f32 mAttackTolerance[4];
    f32 mMagicTolerance[7];
    f32 mShrinkAdj;
    f32 mBlowAdj;
    f32 mDownAdj;
    f32 mOcdAdj;
    f32 mShakeAdjPhys[4];
    f32 mShakeAdjMagic[7];
    f32 mShakeAdjShake;
    f32 mHitStopAdj;
    f32 mHitSlowAdj;
    f32 unknown[33];
    u32 mHitStopDefenceAttr;
    u32 mSurface;
    bool mIsClimbBonus;
    bool mIsDownWeakRegion;

    u32 mCorePointType;
    s32 mCorePointID;
    s32 mCoreJointNo;

    MtVector3 mCoreJointOffset;

    s32 mCoreEpvIndex;
    s32 mCoreEpvElementNo;

    u32 mAttackReactionType[4];
    bool mIsElementWeakRegion[6];
};

struct rChildRegionStatusParam : rTbl2Base
{
    u32 mDataNum;
    cChildRegionStatusParam mpData[mDataNum];
};

rChildRegionStatusParam rchildregionstatusparam_at_0x00 @0x00;