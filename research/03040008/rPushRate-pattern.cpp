struct cPushRate
{
    float mRate[6];
};

struct rTbl2<cPushRate>
{
    u32 version;
    u32 mDataNum;
    cPushRate mpData[mDataNum];
};

struct rPushRate : rTbl2<cPushRate>
{
};

rPushRate rpushrate_at_0x00 @0x00;