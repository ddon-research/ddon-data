#define f32 float

struct cAIResource
{
};

struct cResource
{
    char magicString[4];
    u32 magicVersion;
};

struct MtArray
{
    u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
    T arr[mLength];
};

struct MtVector3
{
    float x;
    float y;
    float z;
};

struct MtSphere
{
    MtVector3 pos;
    float r;
};

bitfield cGpCategoryFlag
{
flag:
    32;
};

struct cAISensorNodeRes : cAIResource
{
    MtSphere mSphere;
    MtVector3 mDir;
    f32 mEffectiveAngle;

    u32 mCategoryFlagNum;
    cGpCategoryFlag mCategoryFlag[mCategoryFlagNum];

    u32 mGroupFlag;
    u32 mUserFlag;
    u32 mStatusFlag;
    s32 mJntNo;
};

struct rAISensor : cResource
{
    MtTypedArray<cAISensorNodeRes> mNodes;
};

rAISensor raisensor_at_0x00 @0x00;