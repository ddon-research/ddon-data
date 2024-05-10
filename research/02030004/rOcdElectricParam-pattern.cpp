struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cOcdElectricParam : MtObject
{
    s32 mJointNo;
};

struct rTbl2<cOcdElectricParam> : rTbl2Base
{
    u32 mDataNum;
    cOcdElectricParam mpData[mDataNum];
};

struct rOcdElectricParam : rTbl2<cOcdElectricParam>
{
};

rOcdElectricParam rocdelectricparam_at_0x00 @0x00;