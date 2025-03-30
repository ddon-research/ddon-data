struct MtObject
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

struct cFlagData : MtObject
{
    u32 mQuestId;
    u32 mFlagNo;
};

struct rEventViewerSetInfo : cResource
{
    MtTypedArray<cFlagData> mFlagArray;
    MtTypedArray<cFlagData> mLayoutFlagArray;
};

rEventViewerSetInfo reventviewersetinfo_at_0x00 @0x00;