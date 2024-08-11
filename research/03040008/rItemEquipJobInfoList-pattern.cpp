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

bitfield JobFlag {
    ANY: 1;
    FIGHTER: 1;
    SEEKER: 1;
    HUNTER: 1;
    PRIEST: 1;
    SHIELD_SAGE: 1;
    SORCERER: 1;
    WARRIOR: 1;
    ELEMENT_ARCHER: 1;
    ALCHEMIST: 1;
    SPIRIT_LANCER: 1;
    HIGH_SCEPTER: 1;
    RESERVED: 20;
};

struct rTbl2<T> : rTbl2Base
{
    u32 mDataNum;
    T mpData[mDataNum];
};

struct cItemEquipJobInfo : MtObject
{
    JobFlag Unknown;
};
struct rItemEquipJobInfoList : rTbl2<cItemEquipJobInfo>
{
};


rItemEquipJobInfoList ritemequipjobinfolist_at_0x00 @ 0x00;