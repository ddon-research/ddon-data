struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cPartsCtrlTable : MtObject
{
    s32 mPartsKeyNo;
    u32 mPartsDisp[16];
};
struct rTbl2<cPartsCtrlTable> : rTbl2Base
{
    u32 mDataNum;
    cPartsCtrlTable mpData[mDataNum];
};

struct rPartsCtrlTable : rTbl2<cPartsCtrlTable>
{
};
