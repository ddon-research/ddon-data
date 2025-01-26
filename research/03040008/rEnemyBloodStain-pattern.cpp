#define f32 float

enum nEnemy_ENEMY_BLOOD_STAIN_TYPE : s32
{
    ENEMY_BLOOD_STAIN_TYPE_HP = 0x0,
    ENEMY_BLOOD_STAIN_TYPE_REGION = 0x1,
    ENEMY_BLOOD_STAIN_TYPE_NONE = 0x2,
    ENEMY_BLOOD_STAIN_TYPE_NUM = 0x3,
};

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct cEnemyBloodStain : MtObject
{
    nEnemy_ENEMY_BLOOD_STAIN_TYPE mBloodStainType;
    f32 mHpRateLv1;
    f32 mHpRateLv2;
    f32 mHpRateLv3;
    s32 mRegionNoLv1;
    s32 mRegionNoLv2;
    s32 mRegionNoLv3;
};
struct rTbl2<cEnemyBloodStain> : rTbl2Base
{
    u32 mDataNum;
    cEnemyBloodStain mpData[mDataNum];
};

struct rEnemyBloodStain : rTbl2<cEnemyBloodStain>
{
};

rEnemyBloodStain renemybloodstain_at_0x00 @0x00;