struct MtVector3
{
    float x;
    float y;
    float z;
};

struct MtObject
{
};

struct cResource
{
    char magicString[];
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

struct rStageAdjoinList_cAdjoinInfo_cIndex : MtObject
{
    u16 mIndex;
};

struct rStageAdjoinList_cAdjoinInfo : MtObject
{
    MtTypedArray<rStageAdjoinList_cAdjoinInfo_cIndex> mIndex;
    u16 mDestinationStageNo;
    u16 mNextStageNo;
    u8 mPriority;
};

struct rStageAdjoinList_cJumpPosition : MtObject
{
    MtVector3 mPos;
    u32 mQuestId;
    u32 mFlagId;
};

struct rStageAdjoinList : cResource
{
    u16 mStageNo;
    MtTypedArray<rStageAdjoinList_cAdjoinInfo> mAdjoinInfo;
    MtTypedArray<rStageAdjoinList_cJumpPosition> mJumpPosition;
};

rStageAdjoinList rstageadjoinlist_at_0x00 @0x00;