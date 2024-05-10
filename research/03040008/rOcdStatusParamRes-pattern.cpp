struct cOcdStatusParamRes
{
    u32 mOcdUID;
    bool mIsEffective;
    float mEndurance;
    bool mIsTimeRecover;
    float mActiveTime;
    float mCureWaitTime;
    float mCureValue;
    float mFreeParam0;
    float mFreeParam1;
    // float mEnduranceCheatCheck;
    // float mActiveTimeCheatCheck;
    // float mCureValueCheatCheck;
    // float mFreeParam0CheatCheck;
    // float mFreeParam1CheatCheck;
};

struct rTbl2<cOcdStatusParamRes>
{
    u32 mDataNum;
    cOcdStatusParamRes mpData[mDataNum];
};

struct rOcdStatusParamRes : rTbl2<cOcdStatusParamRes>
{
};

rOcdStatusParamRes rocdstatusparamres_at_0x04 @0x04;