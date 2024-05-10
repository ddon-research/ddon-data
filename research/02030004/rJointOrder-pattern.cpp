struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};
struct cJointOrder : MtObject
{
    u32 mNum;
    u8 mpJointTable[mNum];
};
struct rTbl2<cJointOrder> : rTbl2Base
{
    u32 mDataNum;
    cJointOrder mpData[mDataNum];
};

struct rJointOrder : rTbl2<cJointOrder>
{
};
rJointOrder rjointorder_at_0x00 @0x00;