struct MtObject
{
};

struct cResource
{
    char magicString[];
    u32 magicVersion;
};

struct rSoundBossBgm_cSoundBossBgm : MtObject
{
    u32 mEnemyId;
    u32 mBgmNo;
    u64 mSrqrId;
};

struct rSoundBossBgm : cResource
{
    u32 mArrayDataNum;
    rSoundBossBgm_cSoundBossBgm mpArrayData[mArrayDataNum];
};

rSoundBossBgm rsoundbossbgm_at_0x00 @0x00;