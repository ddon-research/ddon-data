#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cRegionBreakInfo : MtObject
{
    s32 mLockOffJointID;
    s32 mLockOnJointID;
    s32 mSoundJointNo;
};

struct rRegionBreakInfo : rTbl2Base
{
    u32 mDataNum;
    cRegionBreakInfo mpData[mDataNum];
};

struct cParentRegionStatusParam : MtObject
{
    u32 mNo;
    u32 mRegionCategory;
    bool mIsReGenerate;
    u32 mRegenerateProprirty;
    u32 mHPForEdit[5];
    f32 mShPMax;
    f32 mShPSpeed;
    f32 mShPResetTimerMax;
    f32 mBlPMax;
    f32 mBlPSpeed;
    f32 mBlResetTimerMax;
    f32 mDownPMax;
    f32 mDownPSpeed;
    f32 mDownPResetTimerMax;
    f32 mShakePMax;
    f32 mShakePSpeed;
    f32 mShakeResetTimerMax;
    f32 mRageShrinkMax;
    bool mIsDamageToMain;
    u32 mBreakReactionNo;
    rRegionBreakInfo mpBreakInfo;
};

struct rParentRegionStatusParam : rTbl2Base
{
    u32 mDataNum;
    cParentRegionStatusParam mpData[mDataNum];
};

rParentRegionStatusParam rparentregionstatusparam_at_0x00 @0x00;