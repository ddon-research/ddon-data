struct cNpcIsUseJobParamEx
{
    u16 mStageNo;
    u16 mGroupNo;
    u8 mUnitNo;
    u32 mQuestId;
};

struct rTbl2<cNpcIsUseJobParamEx>
{
    u32 mDataNum;
    cNpcIsUseJobParamEx mpData[mDataNum];
};

struct rNpcIsUseJobParamEx : rTbl2<cNpcIsUseJobParamEx>
{
};

rNpcIsUseJobParamEx rnpcisusejobparamex_at_0x04 @0x04;