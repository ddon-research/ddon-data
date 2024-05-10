struct cCharParamEnemy_cJumpAttackSpeed
{
    bool mIsValid;
    float mSpeedZ;
    float mSpeedY;
    float mGravity;
};

struct cCharParamEnemy_cGuardCounter
{
    u8 mTimes;
    u8 mPercent;
};

struct cCharParam96
{
    u16 mVersion;
};

struct cCharParamEnemy
{
    float mAttackBasePhys;
    float mAttackBaseMagic;
    float mAttackWepPhys;
    float mAttackWepMagic;
    float mDefenceBasePhys;
    float mDefenceBaseMagic;
    float mDefenceWepPhys;
    float mDefenceWepMagic;
    float mPower;
    float mWeight;
    float mGuardAttackBase;
    float mGuardDefenceBase;
    float mGuardDefenceWep;
    u32 mWeaponTypeSe;
    u32 mEnemyBodySizeSe;
    u32 mPushGroup;
    u32 mScrAdjustType;
    u32 mScrAdjustSize;
    float mShakeCureRateRage;
    cCharParamEnemy_cJumpAttackSpeed mJumpAttackSpeed[4];
    float mFallDamageCheckHeight;
    u32 mUseMotionBlendNum;
    bool mUseMotionHistory;
    u32 mUseMotionHistoryNum;
    float mReturnTerritoryContTime;
    u8 mBeardownEffective;
    cCharParamEnemy_cGuardCounter mGuardCounter[10];
    u32 mGuardReactionCheckType;
    float mEnemyScaleBase;
    float mEnemyScaleThinkTable;
    bool mIsShakedActionEnemy;
    u32 mHangdType;
    float mcThinkMgrScaleParam;
    float mEnemyLinkRadiusA;
    bool mEnemyLinkRadiusBOn;
    float mEnemyLinkRadiusB;
    u32 mEvaluationPLJobsNum;
    float mEvaluationPLJobs[mEvaluationPLJobsNum];
    u32 mEvaluationPLSexNum;
    float mEvaluationPLSex[mEvaluationPLSexNum];
    bool mDownPerformanceOff;
    bool mIsDispDownGuage;
    bool mIsNoneAdbantageBGM;
};

struct cCharParamEnemyFly : cCharParamEnemy
{
    float mHoverSpeed;
    u32 mHoverAltitudeNum;
    float mHoverAltitude[mHoverAltitudeNum];
    s32 mHoverLevelMax;
    s32 mHoverLevelRange;

    float mFlySpeed;
    float mFlyAltitude;
};

struct rCharParamEnemy
{
    bool mFlgEnemyFly;
    if (mFlgEnemyFly)
    {
        cCharParamEnemyFly mpCharParamEnemy;
    }
    else
    {

        cCharParamEnemy mpCharParamEnemy;
    }
};

rCharParamEnemy rcharparamenemy_at_0x08 @0x08;