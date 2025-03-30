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

struct cJukeBoxItem : MtObject
{
    u32 mItemId;
    u32 mBgmNo;
};

struct rJukeBoxItem : cResource
{
    MtTypedArray<cJukeBoxItem> Array;
};

rJukeBoxItem rjukeboxitem_at_0x00 @0x00;