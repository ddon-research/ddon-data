
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

enum rCraftRecipe_NPC_ACTION : s32
{
    NPC_ACTION_NONE = 0x0,
    NPC_ACTION_STITHY = 0x1,
    NPC_ACTION_DESK = 0x2,
    NPC_ACTION_COOK = 0x3,
};

struct rCraftRecipe_cMaterialData : MtObject
{
    u32 mItemId;
    u32 mNum;
    bool mIsSp;
};

struct rCraftRecipe_cCraftRecipe : MtObject
{
    u32 mRecipeId;
    u32 mItemId;
    u32 mCreateTime;
    u8 mCreateNum;
    u32 mGold;
    u32 mExp;
    u32 mRank;
    rCraftRecipe_NPC_ACTION mNpcAction;
    MtTypedArray<rCraftRecipe_cMaterialData> mMaterialDataList;
};

struct rCraftRecipe : cResource
{
    u32 mArrayDataNum;
    rCraftRecipe_cCraftRecipe mpArrayData[mArrayDataNum];
};

rCraftRecipe rcraftrecipe_at_0x00 @0x00;