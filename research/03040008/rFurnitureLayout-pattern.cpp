#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cFurnitureLayout : MtObject
{
    u32 mID;
    bool mIsRemovable;
    u32 mGroupId;
    u32 mGmdIdx;
    u8 mSortNo;
};

struct rTbl2<cFurnitureLayout> : rTbl2Base
{
    u32 mDataNum;
    cFurnitureLayout mpData[mDataNum];
};

struct rFurnitureLayout : rTbl2<cFurnitureLayout>
{
};

rFurnitureLayout rfurniturelayout_at_0x00 @0x00;