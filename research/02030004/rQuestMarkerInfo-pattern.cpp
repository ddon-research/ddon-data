#define f32 float

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
    T mInfoList[mLength];
};

struct rQuestMarkerInfo_cInfo : MtObject
{
    MtVector3 mPos;
    u32 mGroupNo;
    u32 mUniqueId;
};

struct rQuestMarkerInfo : cResource
{
    u32 mStageNo;
    MtTypedArray<rQuestMarkerInfo_cInfo> mInfoList;
};

rQuestMarkerInfo rquestmarkerinfo_at_0x00 @0x00;