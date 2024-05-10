struct cNpcCustomSkill
{
    u32 mThinkId;
    u16 mCustomSkill1;
    u16 mCustomSkill2;
    u16 mCustomSkill3;
    u16 mCustomSkill4;
    u16 mCustomSkillLv1;
    u16 mCustomSkillLv2;
    u16 mCustomSkillLv3;
    u16 mCustomSkillLv4;
    u16 mNormalSkillBit;
};

struct rTbl2<cNpcCustomSkill>
{

    u32 mDataNum;
    cNpcCustomSkill mpData[mDataNum];
};

struct rNpcCustomSkill : rTbl2<cNpcCustomSkill>
{
};
rNpcCustomSkill rnpccustomskill_at_0x04 @0x04;