struct MtObject
{
};

struct cResource
{
    // char magicString[];
    u32 magicVersion;
};

struct rTbl2Base : cResource
{
};

struct cUIResource : MtObject
{
};

struct cWarpLocation : cUIResource
{
    u32 mId;
    u32 mSortNo;
    u32 mAreaId;
    u32 mSpotId;
    s32 mStageNo;
    u32 mPosNo;
    u16 mMapPosX;
    u16 mMapPosY;
    u8 mIconType;
};

struct rTbl2<cWarpLocation> : rTbl2Base
{
    u32 mDataNum;
    cWarpLocation mpData[mDataNum];
};

struct rWarpLocation : rTbl2<cWarpLocation>
{
};
rWarpLocation rwarplocation_at_0x00 @0x00;