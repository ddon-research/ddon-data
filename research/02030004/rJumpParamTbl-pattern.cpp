#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cJumpParam : MtObject
{
    f32 mSpeedY;
    f32 mSpeedZ;
    f32 mGravity;
    f32 mDampingZ;
    f32 mAddMoveSpeedXZ;
    bool mIsAwakening;
    f32 mAwakeJumpAdd;
};

struct rTbl2<cJumpParam> : rTbl2Base
{
    u32 mDataNum;
    cJumpParam mpData[mDataNum];
};

struct rJumpParamTbl : rTbl2<cJumpParam>
{
};
rJumpParamTbl rjumpparamtbl_at_0x00 @0x00;