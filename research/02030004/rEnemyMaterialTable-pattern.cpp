struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cEnemyMaterialTable : MtObject
{
    u32 mIdx;
    u32 mMaterialType;
    s32 mMaterialNo;
    u32 mMaterialWeakPointNo;
    u32 mMaterialAnimationType;
    bool mDieIsNoCall;
};
struct rTbl2<cEnemyMaterialTable> : rTbl2Base
{
    u32 mDataNum;
    cEnemyMaterialTable mpData[mDataNum];
};

struct rEnemyMaterialTable : rTbl2<cEnemyMaterialTable>
{
};

rEnemyMaterialTable renemymaterialtable_at_0x00 @0x00;