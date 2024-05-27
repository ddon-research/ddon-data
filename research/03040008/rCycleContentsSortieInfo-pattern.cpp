#define f32 float

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

struct rTbl2<T> : rTbl2Base
{
    u32 mDataNum;
    T mpData[mDataNum];
};

struct cCycleContentsSortieData : MtObject
{
    u32 CycleContentsSortieID;
    u32 NpcID;
    u32 StageNo2;
    u32 StageNo3;
    u32 StageNo4;
    bool unknown;
};

struct rCycleContentsSortieInfo : rTbl2<cCycleContentsSortieData>
{
};

rCycleContentsSortieInfo rcyclecontentssortieinfo_at_0x00 @0x00;