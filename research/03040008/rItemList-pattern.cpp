#pragma pattern_limit 731072

struct MtObject
{
};

struct cResource
{
    char magicString[];
    u32 magicVersion;
};

enum rItemList_ITEM_CATEGORY : u8
{
    CATEGORY_NONE = 0x0,
    CATEGORY_USE_ITEM = 0x1,
    CATEGORY_MATERIAL_ITEM = 0x2,
    CATEGORY_ARMS = 0x3,
    CATEGORY_KEY_ITEM = 0x4,
    CATEGORY_JOB_ITEM = 0x5,
    CATEGORY_FURNITURE = 0x6,
    CATEGORY_CRAFT_RECIPE = 0x7
};

enum rItemList_rParam_PARAM_KIND : s16
{
    KIND_NONE = 0x0,
    HP_RECOVER = 0x1,
    ST_RECOVER = 0x2,
    POISON_CLEAR = 0x3,
    SlOW_CLEAR = 0x4,
    SLEEP_CLEAR = 0x5,
    STAN_CLEAR = 0x6,
    WATER_CLEAR = 0x7,
    OIL_CLEAR = 0x8,
    SEAL_CLEAR = 0x9,
    SOFTBODY_CLEAR = 0xA,
    STONE_CLEAR = 0xB,
    GOLD_CLEAR = 0xC,
    SPREAD_CLEAR = 0xD,
    FREEZE_CLEAR = 0xE,
    FALLFIRE_CLEAR = 0xF,
    FALLICE_CLEAR = 0x10,
    FALLTHUNDER_CLEAR = 0x11,
    FALLSAINT_CLEAR = 0x12,
    FALLBLIND_CLEAR = 0x13,
    FALLATTACK_CLEAR = 0x14,
    FALLDEF_CLEAR = 0x15,
    FALLMAGIC_CLEAR = 0x16,
    FALLMAGICDEF_CLEAR = 0x17,
    ATTACK_UP = 0x18,
    DEFENCE_UP = 0x19,
    MAGICATTACK_UP = 0x1A,
    MAGICDEFENSE_UP = 0x1B,
    POWERREV_UP = 0x1C,
    DURABILITY_UP = 0x1D,
    SPIRIT_UP = 0x1E,
    HP_UP = 0x1F,
    ENDURANCE_UP = 0x20,
    BLIND_CLEAR = 0x21,
    REVIVAL_ONE = 0x22,
    REVIVAL_THREE = 0x23,
    LANTERN_ON = 0x24,
    GOLD_CHANGE = 0x6E,
    RIM_CHANGE = 0x6F,
    DOGMA_CHANGE = 0x70,
    MEDAL_POISON = 0x71,
    MEDAL_SLEEP = 0x72,
    MEDAL_STAN = 0x73,
    MEDAL_FALLFIRE = 0x74,
    MEDAL_FALLICE = 0x75,
    MEDAL_FALLTHUNDER = 0x76,
    MEDAL_FALLSAINT = 0x77,
    MEDAL_FALLBLIND = 0x78,
    MEDAL_SEAL = 0x79,
    MEDAL_STONE = 0x7A,
    MEDAL_GOLD = 0x7B,
    CURRENCY = 0x7C,
    THUNDER_CLEAR = 0x7D,
    EROSION_CLEAR = 0x7E,
    EROSION_GUARD_UP = 0x7F,
    JOB_POINT = 0x80,
    AREA_POINT = 0x81,
    SKILL_LEARN = 0x82,
    ABILITY_LEARN = 0x83,
    PAWN_USE = 0x84,
};

enum rItemList_rItemParam_EQUIP_SUB_CATEGORY : s32
{
    EQUIP_SUB_CATEGORY_NONE = 0x0,
    EQUIP_SUB_CATEGORY_TOP = 0x1,
    EQUIP_SUB_CATEGORY_JEWELRY_COMMON = 0x1,
    EQUIP_SUB_CATEGORY_JEWELRY_RING = 0x2,
    EQUIP_SUB_CATEGORY_JEWELRY_BRACELET = 0x3,
    EQUIP_SUB_CATEGORY_JEWELRY_PIERCE = 0x4
};

enum rItemList_MATERIAL_CATEGORY : s32
{
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
    MATERIAL_CATEGORY_SPECIALTY_GOODS = 0x1E
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
    USE_CATEGORY_DOOR_KEY = 0x8
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
    rItemList_rParam_PARAM_KIND mKindType; // cast to u16
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

bitfield GradeRankFlag
{
mGrade:
    2;
mRank:
    4;
Reserved:
    10;
};

bitfield IsUseJobAttackStatusFlag
{
mAttackStatus:
    1;
mIsUseJob:
    4;
Reserved:
    3;
};

struct Consumable
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;
    u32 mNameId;
    u8 detailCategoryMaybe;

    u16 mIconNo;
    u8 mIconColNo;
    u32 mSortNo;
    u32 mNameSortNo;

    u16 mPrice;
    GradeRankFlag mGradeRankFlag;
    u8 mStackMax;
    u8 mAttackStatus;

    u8 mParamNum;
    rItemList_rParam mpItemParamList[mParamNum];
};

struct Material
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;
    u32 mNameId;
    u8 detailCategoryMaybe;

    u16 mIconNo;
    u8 mIconColNo;
    u32 mSortNo;
    u32 mNameSortNo;

    u16 mPrice;
    GradeRankFlag mGradeRankFlag;
    u8 mStackMax;
    // u8 mAttackStatus;

    u8 mParamNum;
    rItemList_rParam mpItemParamList[mParamNum];
};

struct KeyItem
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;
    u32 mNameId;
    u8 detailCategoryMaybe;

    u16 mIconNo;
    u8 mIconColNo;
    u32 mSortNo;
    u32 mNameSortNo;

    u8 mStackMax;
};

struct JobItem
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;
    u32 mNameId;
    u8 detailCategoryMaybe;

    u16 mIconNo;
    u8 mIconColNo;
    u32 mSortNo;
    u32 mNameSortNo;

    u16 mPrice;
    GradeRankFlag mGradeRankFlag;
    u8 mStackMax;
    // u8 mAttackStatus;
    u8 mIsUseLv;
    IsUseJobAttackStatusFlag mIsUseJobAttackStatusFlag;

    u8 mParamNum;
    rItemList_rParam mpItemParamList[mParamNum];
};

struct SpecialItem
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;
    u32 mNameId;
    u8 detailCategoryMaybe;

    u16 mIconNo;
    u8 mIconColNo;
    u32 mSortNo;
    u32 mNameSortNo;

    u8 mRank;
};

struct Weapon
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;
    // u32 mNameId;
    // u8 detailCategoryMaybe;

    // u16 mIconNo;
    // u8 mIconColNo;
    u32 mSortNo;
    u32 mNameSortNo;

    u16 mPrice;
    GradeRankFlag mGradeRankFlag;

    u16 mAttack;
    u16 mMagicAttack;
    u16 mWeight;

    u8 Unknown1;
    u16 Unknown2;

    u8 mEquipParamS8Num;
    rItemList_rEquipParamS8 mpEquipParamS8List[mEquipParamS8Num];
};

struct UpgradableWeapon
{
    u32 mItemId;
    u8 Unknown2;
    u8 Unknown3MaybeColorId;

    u32 mNameId;
    u16 Unknown5;
    u16 Unknown6;
    u16 Unknown7;
    u8 Unknown8;
    u8 Unknown9;
    u8 Unknown10;

    u8 Unknown11;
    u8 Unknown12;
    u8 Unknown13;
};

struct Armor
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;
    // u32 mNameId;
    // u8 detailCategoryMaybe;

    // u16 mIconNo;
    // u8 mIconColNo;
    u32 mSortNo;
    u32 mNameSortNo;

    u16 mPrice;
    GradeRankFlag mGradeRankFlag;

    u16 mAttack;
    u16 mMagicAttack;
    u16 mDefense;
    u16 mMagicDefense;
    u16 mWeight;

    u8 Unknown1;
    u16 Unknown2;

    u8 mEquipParamS8Num;
    rItemList_rEquipParamS8 mpEquipParamS8List[mEquipParamS8Num];
};

struct UpgradableArmor
{
    u32 mItemId;
    u8 Unknown2;
    u8 Unknown3MaybeColorId;

    u32 mNameId;
    u16 Unknown5;
    u16 Unknown6;
    u16 Unknown7;
    u8 Unknown8;
    u8 mIsUseLv;
    u8 Unknown10;
};

struct Jewelry
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;

    u32 mSortNo;
    u32 mNameSortNo;

    u16 mPrice;
    GradeRankFlag mGradeRankFlag;

    u32 mNameId;
    u16 mIconNo;

    u8 mIsUseLv;
    u8 Unknown1;
    u16 mAttack;
    u16 mMagicAttack;
    u16 mDefense;
    u16 mMagicDefense;
    u16 mWeight;
    u8 Unknown2;
    u8 mIconColNo;
    u8 mEleSlot; // crest

    u8 mEquipParamS8Num;
    rItemList_rEquipParamS8 mpEquipParamS8List[mEquipParamS8Num];
};

struct NPCEquipment
{
    u32 mItemId;
    u16 mFlag;
    rItemList_ITEM_CATEGORY mCategory;

    u32 Unknown1;
    u8 Unknown2;
    u8 Unknown3MaybeColorId;

    u32 mNameId;
    GradeRankFlag mGradeRankFlag;
    // u8 weaponCategoryMaybe;
};

struct rItemList : cResource
{
    u32 buffer1;
    u32 buffer2;

    u32 Unknown1;
    u32 mArrayConsumablesNum;
    u32 mArrayMaterialsNum;
    u32 mArrayKeyItemsNum;
    u32 mArrayJobItemsNum;
    u32 mArraySpecialItemsNum;
    u32 mArrayWeaponsNum;
    u32 mArrayUpgradableWeaponNum;
    u32 mArrayArmorsNum;
    u32 mArrayUpgradableArmorNum;
    u32 mArrayJewelriesNum;
    u32 mArrayNpcEquipmentsNum;

    u32 UnknownList1[Unknown1];
    Consumable ConsumableItemList[mArrayConsumablesNum];
    Material MaterialItemList[mArrayMaterialsNum];
    KeyItem KeyItemList[mArrayKeyItemsNum];
    JobItem JobItemList[mArrayJobItemsNum];
    SpecialItem SpecialItemList[mArraySpecialItemsNum];
    Weapon WeaponItemList[mArrayWeaponsNum];
    UpgradableWeapon UpgradableWeaponItemList[mArrayUpgradableWeaponNum];
    Armor ArmorItemList[mArrayArmorsNum];
    UpgradableArmor UpgradableArmorItemList[mArrayUpgradableArmorNum];
    Jewelry JewelryItemList[mArrayJewelriesNum];
    NPCEquipment NpcEquipmentItemList[mArrayNpcEquipmentsNum];
};

rItemList ritemlist_at_0x00 @0x00;