#pragma pattern_limit 731072

struct MtObject
{
};

struct cResource
{
    char magicString[];
    u32 magicVersion;
};

enum rItemList_MATERIAL_CATEGORY : s32
{
    MATERIAL_CATEGORY_START = 0x0,
    MATERIAL_CATEGORY_NONE = 0x0,
    MATERIAL_CATEGORY_METAL = 0x1,
    MATERIAL_CATEGORY_STONE = 0x2,
    MATERIAL_CATEGORY_SAND = 0x3,
    MATERIAL_CATEGORY_CLOTH = 0x4,
    MATERIAL_CATEGORY_THREAD = 0x5,
    MATERIAL_CATEGORY_WOOL = 0x6,
    MATERIAL_CATEGORY_BARK = 0x7,
    MATERIAL_CATEGORY_BONE = 0x8,
    MATERIAL_CATEGORY_FANG = 0x9,
    MATERIAL_CATEGORY_HORN = 0xA,
    MATERIAL_CATEGORY_SHELL = 0xB,
    MATERIAL_CATEGORY_WING = 0xC,
    MATERIAL_CATEGORY_JEWEL = 0xD,
    MATERIAL_CATEGORY_GRASS = 0xE,
    MATERIAL_CATEGORY_FLOWER = 0xF,
    MATERIAL_CATEGORY_NUTS = 0x10,
    MATERIAL_CATEGORY_MUSHROOM = 0x11,
    MATERIAL_CATEGORY_WOODCHIP = 0x12,
    MATERIAL_CATEGORY_LIQUID = 0x13,
    MATERIAL_CATEGORY_BANDEROLE = 0x14,
    MATERIAL_CATEGORY_ALCHE = 0x15,
    MATERIAL_CATEGORY_MEAT = 0x16,
    MATERIAL_CATEGORY_OTHER = 0x17,
    MATERIAL_CATEGORY_ELEMENT_WEP = 0x18,
    MATERIAL_CATEGORY_ELEMENT_ARMOR = 0x19,
    MATERIAL_CATEGORY_SPECIAL_WEP = 0x1A,
    MATERIAL_CATEGORY_SPECIAL_ARMOR = 0x1B,
    MATERIAL_CATEGORY_COLOR = 0x1C,
    MATERIAL_CATEGORY_APPRAISAL = 0x1D,
    MATERIAL_CATEGORY_SPECIALTY_GOODS = 0x1E,
    MATERIAL_CATEGORY_NUM = 0x1F,
};

enum rItemList_USE_CATEGORY : s32
{
    USE_CATEGORY_DUMMY = 0x0,
    USE_CATEGORY_NONE = 0x1,
    USE_CATEGORY_THROW = 0x2,
    USE_CATEGORY_MINE = 0x3,
    USE_CATEGORY_LUMBER = 0x4,
    USE_CATEGORY_KEY = 0x5,
    USE_CATEGORY_JOBITEM = 0x6,
    USE_CATEGORY_UNUSE = 0x7,
    USE_CATEGORY_DOOR_KEY = 0x8,
    USE_CATEGORY_NUM = 0x9,
};

struct rItemList_rItemParam_SUB_CATEGORY_EquipCategory
{
    u8 mEquipCategory;
    u8 _padding;
    u16 mEquipSubCategory;
};

union rItemList_rItemParam_SUB_CATEGORY
{
    rItemList_rItemParam_SUB_CATEGORY_EquipCategory mEquipCategory;
    rItemList_USE_CATEGORY mUseCategory;
    rItemList_MATERIAL_CATEGORY mMaterialCategory;
    u32 mCategory;
};

struct rItemList_rParam_PARAM_GenericParam
{
    u16 mParam1;
    u16 mParam2;
    u16 mParam3;
};

struct rItemList_rParam_AP_GET
{
    u16 mAreaId;
    u16 mPoint;
    u16 _padding;
};

struct rItemList_rParam_JP_GET
{
    u16 mJobId;
    u16 mPoint;
    u16 _padding;
};

struct rItemList_rParam_ABILITY_ASSIGNMENT
{
    u16 mAbilityNo;
    u16 mLv;
    u16 _padding;
};

struct rItemList_rParam_SKILL_LEARNING
{
    u16 mJobId;
    u16 mSkillNo;
    u16 _padding;
};

struct rItemList_rParam_ABILITY_LEARNING
{
    u16 mAbilityNo;
    u16 padding1;
    u16 padding2;
};

union rItemList_rParam_PARAM
{
    rItemList_rParam_PARAM_GenericParam _anon_0;
    rItemList_rParam_AP_GET mAp;
    rItemList_rParam_JP_GET mJp;
    rItemList_rParam_ABILITY_ASSIGNMENT mAbilityAssignment;
    rItemList_rParam_SKILL_LEARNING mSkillLearning;
    rItemList_rParam_ABILITY_LEARNING mAbilityLearning;
};

struct rItemList_rParam : MtObject
{
    s16 mKindType; // cast to u16
    rItemList_rParam_PARAM mParam;
};

struct rItemList_rVsEnemyParam : MtObject
{
    u8 mKindType;
    u16 mParam;
};

struct rItemList_rEquipParamS8_PARAM_S8
{
    s8 mValueS8;
    // u8 mPaddingS8;
};

struct rItemList_rEquipParamS8_PARAM_U8
{
    u8 mValueU8;
    // u8 mPaddingU8;
};

struct rItemList_rEquipParamS8_PARAM_S16
{
    s16 mValueS16;
};

struct rItemList_rEquipParamS8_PARAM_U16
{
    u16 mValueU16;
};

union rItemList_rEquipParamS8_PARAM
{
    rItemList_rEquipParamS8_PARAM_S8 _anon_0;
    rItemList_rEquipParamS8_PARAM_U8 _anon_1;
    rItemList_rEquipParamS8_PARAM_S16 _anon_2;
    rItemList_rEquipParamS8_PARAM_U16 _anon_3;
};

struct rItemList_rEquipParamS8 : MtObject
{
    u8 mKindType;
    u8 mForm;
    if (mForm == 0)
    {
        rItemList_rEquipParamS8_PARAM_S8 mValue;
    }
    if (mForm == 1)
    {
        rItemList_rEquipParamS8_PARAM_U8 mValue;
    }
    if (mForm == 2)
    {
        rItemList_rEquipParamS8_PARAM_S16 mValue;
    }
    if (mForm == 3)
    {
        rItemList_rEquipParamS8_PARAM_U16 mValue;
    }
};

struct rItemList_rWeaponParam : MtObject
{
    u32 mModelTagId;
    u32 mPowerRev;
    u32 mChance;
    u32 mDefense;
    u32 mMagicDefense;
    u32 mDurability;

    u8 mWepCategory;

    u32 mAttack;
    u32 mMagicAttack;
    u32 mShieldStagger;
    u16 mWeight;
    u16 mMaxHpRev;
    u16 mMaxStRev;

    u8 mColorNo;
    u8 mSex;
    u8 mModelParts;
    u8 mEleSlot;
    u8 mPhysicalType;
    u8 mElementType;

    u8 mEquipParamS8Num;
    rItemList_rEquipParamS8 mpEquipParamS8List[mEquipParamS8Num];
};

struct rItemList_rProtectorParam : MtObject
{
    u32 mModelTagId;
    u32 mPowerRev;
    u32 mChance;
    u32 mDefense;
    u32 mMagicDefense;
    u32 mDurability;
    u32 mAttack;
    u32 mMagicAttack;

    u16 mWeight;
    u16 mMaxHpRev;
    u16 mMaxStRev;

    u8 mColorNo;
    u8 mSex;
    u8 mModelParts;
    u8 mEleSlot;

    u8 mEquipParamS8Num;
    rItemList_rEquipParamS8 mpEquipParamS8List[mEquipParamS8Num];
};

struct rItemList_rItemParam : MtObject
{
    u32 mItemId;
    u32 mNameId;
    rItemList_rItemParam_SUB_CATEGORY mCategory2;
    u32 mPrice;
    u32 mSortNo;
    u32 mNameSortNo;
    u32 mAttackStatus;
    u32 mIsUseJob;
    u16 mFlag;
    u16 mIconNo;
    u16 mIsUseLv;
    u8 mCategory;
    u8 mStackMax;
    u8 mRank;
    u8 mGrade;
    u8 mIconColNo;

    u32 mParamNum;
    rItemList_rParam mpItemParamList[mParamNum];

    u32 mVsEmNum;
    rItemList_rVsEnemyParam mpVsEmList[mVsEmNum];

    if (mCategory == 3)
    {
        if (u8(mCategory2.mEquipCategory.mEquipCategory - 1) > 1u)
        {
            if (mCategory2.mEquipCategory.mEquipCategory <= 0xC && u8(mCategory2.mEquipCategory.mEquipCategory - 1) >= 2u)
            {
                rItemList_rProtectorParam mpProtectorParam;
            }
        }
        else
        {
            rItemList_rWeaponParam mpWeaponParam;
        }
    }
};

struct rItemList : cResource
{
    u32 mArrayDataNum;
    u32 mArrayParamDataNum;
    u32 mArrayVsParamDataNum;
    u32 mArrayWeaponParamDataNum;
    u32 mArrayProtectParamDataNum;
    u32 mArrayEquipParamS8DataNum;

    rItemList_rItemParam mpItemList[mArrayDataNum];
};

rItemList ritemlist_at_0x00 @0x00;
