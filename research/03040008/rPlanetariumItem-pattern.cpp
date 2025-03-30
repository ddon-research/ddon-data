struct MtObject
{
};

struct cResource
{
    u32 version;
};

struct MtArray
{
    u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
    T arr[mLength];
};

struct cPlanetariumItem : MtObject
{
    u32 mItemId;
    u32 mNpcNo;
    u32 mCategory;
    u32 mMotNo;
};

struct rPlanetariumItem : cResource
{
    MtTypedArray<cPlanetariumItem> Array;
};

rPlanetariumItem rplanetariumitem_at_0x00 @0x00;