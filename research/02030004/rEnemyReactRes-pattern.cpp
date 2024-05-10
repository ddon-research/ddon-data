#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cEnemyReactRes : MtObject
{
    u32 mCountStart;
    u32 mCountEnd;
    f32 mPercent;
    s32 mParam0;
    s32 mParam1;
};

struct rEnemyReactResEx : rTbl2Base
{

    u32 mOverallConditionsType;
    f32 mOverallConditions0;
    f32 mOverallConditions1;

    bool mOverallConditionsReverse;

    bool mOverallConditionsBitMode;

    u32 mWhereType0;
    s32 mWhereNo0;

    u32 mWhereType1;
    s32 mWhereNo1;

    u32 mWhereType2;
    s32 mWhereNo2;

    u32 mWhereType3;
    s32 mWhereNo3;

    u32 mWhereType4;
    s32 mWhereNo4;

    u32 mWhereType5;
    s32 mWhereNo5;

    u32 mWhereType6;
    s32 mWhereNo6;

    u32 mWhereType7;
    s32 mWhereNo7;

    bool mWhereNoRev;
    u32 mPlayTypeGuard;
    u32 mPlayTypeNamed;
    u32 mPlayTypeAnger;
    u32 mPlayTypeNanteki;
    u32 mPlayTypeYojinoboriAttack;

    bool mPlayTypeHP;
    f32 mPlayTypeHPParam[2];

    bool mPlayTypeHPParamReverse;
    u32 mPlayTypeUseSeq;
    u32 mPlayTypeUseSeqWorkNo;
    u32 mPlayTypeSeqNo;
    u32 mPlayTypeSeqWorkNo;

    bool mCountType[12];

    bool mResetTypeBlow;
    u32 mResetTypeBlowCount;
    bool mResetTypeShrink;
    u32 mResetTypeShrinkCount;

    bool mResetTypeDown;
    u32 mResetTypeDownCount;
    u32 mResetType;

    f32 mFResetParam;
    u32 mUResetParam;
    bool mResultThinkTable;
    s32 mResultThinkTableNo;
    bool mResultThinkTableActionGet;
    bool mResultAction;
    u32 mResultActionNo;
    u64 mOverallConditionsBit;

    u32 mDataNum;
    cEnemyReactRes mpData[mDataNum];
};

rEnemyReactResEx renemyreactresex_at_0x00 @0x00;