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

struct cEndContentsSortieData : MtObject
{
    u32 QuestId;
    u32 StageNo1;
    u32 StageNo2;
    u32 StageNo3;
    u32 Unknown2;
    u32 Unknown3;
    u32 Flag;
    bool Unknown4;
};

struct rEndContentsSortieInfo : rTbl2<cEndContentsSortieData>
{
};

rEndContentsSortieInfo rendcontentssortieinfo_at_0x00 @0x00;