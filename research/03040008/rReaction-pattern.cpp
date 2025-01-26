struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cReaction_cCondition : MtObject
{
    u32 mCondition;
    u64 mParam0;
    u64 mParam1;
    u32 mCkAndOR;
    bool mReverse;
};

struct cReaction_cTrigger : MtObject
{
    u32 mTrigger;
    u32 mParam;
    u32 mParam1;
    u32 mCount;
};

struct cReaction_cAction : MtObject
{
    u32 mPercent;
    u32 mActNoLand;
    u32 mActNoAir;
    u32 mActNoDown;
};

struct cReaction : MtObject
{
    cReaction_cTrigger mReactTrigger;
    cReaction_cCondition mReactCondition[4];
    // u32 mActPrio;
    bool mAllCondition;
    cReaction_cAction mReactAction[4];
    u32 mForceReaction;
    u32 mOptionFlg;
};

struct rTbl2<cReaction> : rTbl2Base
{
    u32 mDataNum;
    cReaction mpData[mDataNum];
};

struct rReaction : rTbl2<cReaction>
{
};

rReaction rreaction_at_0x00 @0x00;