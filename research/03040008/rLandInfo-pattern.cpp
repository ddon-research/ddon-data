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

struct rLandInfo_cLandInfo_cLandAreaInfo : MtObject
{

    u32 mAreaId;
};

struct rLandInfo_cLandInfo : MtObject
{
    u32 mLandId;
    bool mIsDispNews;
    u8 mGameMode;
    MtTypedArray<rLandInfo_cLandInfo_cLandAreaInfo> mAreaArray;
};

struct rLandInfo : cResource
{
    MtTypedArray<rLandInfo_cLandInfo> mLandInfo;
};

rLandInfo rlandinfo_at_0x00 @0x00;