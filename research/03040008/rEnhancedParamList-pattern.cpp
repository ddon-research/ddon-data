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

enum MtDTI : u32
{
    cEnhancedData = 130648964,
};

struct cEnhancedData : MtObject
{
    MtDTI DTIID;
    u8 flag1;
    u16 flag2;
};

struct cEnhancedParam : MtObject
{
    MtTypedArray<cEnhancedData> EnhancedDataArray;
};

struct rEnhancedParamList : cResource
{
    MtTypedArray<cEnhancedParam> EnhancedParamArray;
};

rEnhancedParamList renhancedparamlist_at_0x00 @0x00;