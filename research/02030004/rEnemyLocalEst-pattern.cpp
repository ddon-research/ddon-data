struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cEnemyLocalEstTable : MtObject
{
    u32 mIdx;
    u32 mBitNo;
    u32 mStatus;
    bool mCheckBit;
    bool mPlayAlways;
    u32 mControlType;
    u32 mControlIndex;
    u32 mBitContrlCommand;
    bool mSetUpOff;
};

struct rTbl2<cEnemyLocalEstTable> : rTbl2Base
{
    u32 mDataNum;
    cEnemyLocalEstTable mpData[mDataNum];
};

struct rEnemyLocalEst : rTbl2<cEnemyLocalEstTable>
{
};
rEnemyLocalEst renemylocalest_at_0x00 @0x00;