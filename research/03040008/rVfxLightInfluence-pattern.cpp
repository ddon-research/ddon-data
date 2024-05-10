struct cVfxLightInfluence
{
    float mLightIntensity;
    float mCustom1;
    float mCustom2;
    float mCustom3;
    float mCustom4;
    float mCustom6;
    float mEnv1;
    float mEnv2;
};

struct rTbl2<cVfxLightInfluence>
{
    u32 mDataNum;
    cVfxLightInfluence mpData[mDataNum];
};

struct rVfxLightInfluence : rTbl2<cVfxLightInfluence>
{
};
rVfxLightInfluence rvfxlightinfluence_at_0x04 @0x04;