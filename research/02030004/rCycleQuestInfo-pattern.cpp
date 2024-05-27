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

struct rCycleQuestInfo_cCycleQuestSituationInfo : MtObject
{
    u32 mSituationNo;
    u32 mSituationNameIdx;
    u32 mSituationStateIdx;
    u32 mSituationDetailIdx;
};

struct rCycleQuestInfo_cCycleQuestInfo : MtObject
{
    u32 mCycleNo;
    u32 mCycleSubNo;
    u32 mContentNameIdx;
    u32 mContentInfoIdx;
    u32 mGatherInfoIdx;
    MtTypedArray<rCycleQuestInfo_cCycleQuestSituationInfo> mSituationInfo;
    u32 mGatherNpcId;
    u32 mGatherStageNo;
    u32 mGatherStartPos;
};

struct rCycleQuestInfo : cResource
{
    MtTypedArray<rCycleQuestInfo_cCycleQuestInfo> mCycleQuestInfo;
};

rCycleQuestInfo rcyclequestinfo_at_0x00 @0x00;