#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};
struct cEmWorkRateTable : MtObject
{
    f32 mWorkRate;
    u32 mWorkRateStatus;
};
struct rTbl2<cEmWorkRateTable> : rTbl2Base
{
    u32 mDataNum;
    cEmWorkRateTable mpData[mDataNum];
};
struct rEmWorkRateTable : rTbl2<cEmWorkRateTable>
{
};
rEmWorkRateTable remworkratetable_at_0x00 @0x00;