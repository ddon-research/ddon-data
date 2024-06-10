#pragma pattern_limit 231072

struct cResource
{
    // char magicString[4];
    // u32 magicVersion;
};

struct rLanguageResIDConverter_stResList
{
    u32 dtiId;
    u32 hashBase;
    u32 hashLng;
};

struct rLanguageResIDConverter_stHeader
{
    u32 version;
    u32 num;
    u16 topOfs[256];
    u16 nodeNum[256];
};

struct rLanguageResIDConverter : cResource
{
    rLanguageResIDConverter_stHeader mpHeader;
    rLanguageResIDConverter_stResList dat[mpHeader.num];
};

enum rLanguageResIDConverter_ : s32
{
    HEADER_SIZE_0 = 0x408,
};

enum rLanguageResIDConverter__ : s32
{
    DATA_VERSION_11 = 0x1,
    TBL_BIT_NUM = 0x8,
    TBL_NUM = 0x100,
    TBL_MASK = 0xFF,
};
rLanguageResIDConverter rlanguageresidconverter_at_0x00 @0x00;