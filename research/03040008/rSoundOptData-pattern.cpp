enum rSoundRequest_SOUND_REQUEST_CATEGORY : u32
{
    SOUND_REQUEST_SE = 0x0,
    SOUND_REQUEST_ENV = 0x1,
    SOUND_REQUEST_VOICE = 0x2,
    SOUND_REQUEST_SYSTEM = 0x3
};

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cSoundOptData : MtObject
{
    rSoundRequest_SOUND_REQUEST_CATEGORY mCategory;
    u32 mItem;
    s32 mChannel[6];
};
struct rTbl2<cSoundOptData> : rTbl2Base
{
    u32 mDataNum;
    cSoundOptData mpData[mDataNum];
};

struct rSoundOptData : rTbl2<cSoundOptData>
{
};

rSoundOptData rsoundoptdata_at_0x00 @0x00;