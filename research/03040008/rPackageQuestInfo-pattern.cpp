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

struct rPackageQuestInfo_cPackageQuestInfo : MtObject
{
    //see package_quest.gmd for quest names
    u32 mPackageNo;
    u32 mContentInfoIdx;  
    u32 mGatherNpcId;
    u32 mGatherInfoIdx;
    u32 mGatherStartPos;
};

struct rPackageQuestInfo : cResource
{
    MtTypedArray<rPackageQuestInfo_cPackageQuestInfo> mPackageQuestInfo;
};

rPackageQuestInfo rPackagequestinfo_at_0x00 @0x00;