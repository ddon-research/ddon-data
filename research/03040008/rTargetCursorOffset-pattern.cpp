#define f32 float

struct MtObject
{
};

struct MtVector3
{
    float x;
    float y;
    float z;
};

struct rTbl2Base
{
    u32 version;
};

struct cTargetCursorOffset : MtObject
{
    u32 mId;
    s32 mJointNo;
    MtVector3 mOffsetFromJoint;
};
struct rTbl2<cTargetCursorOffset> : rTbl2Base
{
    u32 mDataNum;
    cTargetCursorOffset mpData[mDataNum];
};

struct rTargetCursorOffset : rTbl2<cTargetCursorOffset>
{
};

rTargetCursorOffset rtargetcursoroffset_at_0x00 @0x00;