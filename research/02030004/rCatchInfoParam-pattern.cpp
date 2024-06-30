#define f32 float
struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct rTbl2<T> : rTbl2Base
{
    u32 mDataNum;
    T mpData[mDataNum];
};

struct cCatchInfoParam : MtObject
{
    u32 mCatchType;
    u32 mCatchActionTblNo;
    bool mIsConst;
    bool mRevAdjust;
    bool mConstScaleOff;
    u32 mConstJointNo;
    f32 mLoopTimer;
    s32 mLeverGachaPoint;
    bool mIsCheckSlaveDist;
    f32 mCheckSlaveDist;
};

struct rCatchInfoParam : rTbl2<cCatchInfoParam>
{
};
rCatchInfoParam rcatchinfoparam_at_0x00 @0x00;