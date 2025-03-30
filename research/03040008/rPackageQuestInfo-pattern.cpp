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

struct cPackageQuestClientInfo : MtObject
{
    u32 mNpcId;
    u32 mClientMessageIdx;
};

struct cPackageQuestInfo : MtObject
{
    // see package_quest.gmd for quest names
    u32 mPackageId;
    u32 ContentInfoIdx;
    cPackageQuestClientInfo mClientInfo;
    u32 mHistoryMessageIdx;
};

struct rPackageQuestInfo : cResource
{
    MtTypedArray<cPackageQuestInfo> mPackageQuestInfo;
};

rPackageQuestInfo rPackagequestinfo_at_0x00 @0x00;