#define f32 float

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cEnemyStatusChange : MtObject
{
    u32 mGroupNo;
    u32 mGroupSubNo;
    u32 mNextGroupSubNo;
    bool mNextGroupSubOneGo;
    u32 mSelectNo;
    u32 mType;

    u32 mRepeatSetting;
    u32 mChangeStatus;

    f32 mParam[2];
    f32 mSystemParam[3];
    f32 mSystemParamWait;
    u32 mBitContrlCommand;
    bool mTypeReverse;
};

struct rTbl2<cEnemyStatusChange> : rTbl2Base
{
    u32 mDataNum;
    cEnemyStatusChange mpData[mDataNum];
};

struct rEnemyStatusChange : rTbl2<cEnemyStatusChange>
{
};
rEnemyStatusChange renemystatuschange_at_0x00 @0x00;