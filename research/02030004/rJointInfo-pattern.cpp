#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct MtVector3
{
    float x;
    float y;
    float z;
};

struct cJointInfo : MtObject
{
    u16 mJntNo;
    u16 mAttr;
    f32 mRadius;
    MtVector3 mOfsPos;
    u16 mJointInfoID;
};
struct rTbl2<cJointInfo> : rTbl2Base
{
    u32 mDataNum;
    cJointInfo mpData[mDataNum];
};

struct rJointInfo : rTbl2<cJointInfo>
{
};
rJointInfo rjointinfo_at_0x00 @0x00;