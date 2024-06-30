#define f32 float

struct MtObject
{
};

struct cUIResource
{
};

struct MtArray
{
    u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
    T arr[mLength];
};

struct cResource
{
    // char magicString[];
    u32 magicVersion;
};

struct rTbl2Base : cResource
{
};

struct rTbl2<T> : rTbl2Base
{
    u32 mDataNum;
    T mpData[mDataNum];
};
struct cSpotEnemyData : cUIResource
{
    u32 mEnemyGroupId;
    u32 mEnemyNamedId;
    u16 mLevel;
    u16 Unknown;
    u8 mRank;
};

struct cSpotItemData : cUIResource
{
    u32 mItemId;
    u16 Unknown;
    bool mIsFeature;
    bool mIsCannotPawnTake;
};

struct cAreaMasterSpotDetailData : cUIResource
{
    u32 mSpotId;
    MtTypedArray<cSpotItemData> mItemArray;
    MtTypedArray<cSpotEnemyData> mEnemyArray;
};

struct rAreaMasterSpotDetailData : rTbl2<cAreaMasterSpotDetailData>
{
};
rAreaMasterSpotDetailData rareamasterspotdetaildata_at_0x00 @0x00;