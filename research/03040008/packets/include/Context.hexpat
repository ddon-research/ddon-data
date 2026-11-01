// Group 35 CONTEXT structures of client 03040008 (PC, Season 3).
//
// Source (transcribed, not re-derived): P4 specs/005-netmsg-patterns/research/P4-context-binary-character.md
// section 2.2 (PC readers/writers, V) with the PS4 02020005 field names of the DWARF types in
// binaries/PS4_02020005/DDOORBIS.elf.h (CDataContextBase, CDataContextPlayerInfo,
// CDataContextSetAdditional, ...). "PC 0x..." is the reader or writer VA in the PC 03040008
// database (image base 0x400000). `unk_*` = Season 3 field without a PS4 counterpart; its name is
// open. Server C# names are leads only and appear here only as "server: <name>".
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CNetPos: f64 X, f32 Y, f64 Z (20 B).
struct CNetPos {
    double x;
    float y;
    double z;
};

// CVector3: 3 x f32.
struct CVector3 {
    float x;
    float y;
    float z;
};

// CDataContextSetBase: PC reader 0x760400, writer 0x77e7e0 (28 B).
struct CDataContextSetBase {
    u32 m_unID;
    u64 m_unUniqueID;     // PS4 u32
    s32 m_nStageNo;
    s32 m_nEncountArea;
    s32 m_nMasterIndex;
    u32 unk_u32;          // Season 3, new (server: Unk0)
};

// CDataMasterInfo: PC reader in 0x76ec20, writer in 0x77ff60.
struct CDataMasterInfo {
    u64 m_unUniqueID;     // PS4 u32
    s8 m_cMasterIndex;
};

// u32 count + CDataMasterInfo[count]: 35.10.1, 35.10.16, 35.14.16, 35.15.16.
struct MasterInfoList {
    u32 count;
    CDataMasterInfo entries[count];
};

struct CDataOcdActive {
    u8 m_ucOcdUID;
    u8 m_ucOcdActiveLv;
};

struct CDataOcdImmuneLv {
    u8 m_ucIndex;
    u8 m_ucImmuneLv;
};

// CDataContextSetAdditional: PC writer 0x77e2b0, reader 0x75ff30. PS4 declaration order; 567 B
// plus the two Ocd lists (4 + 2n each).
struct CDataContextSetAdditional {
    s32 m_nMasterIndex;
    bool m_bMasterChangeFlag;
    CNetPos m_Pos;
    float m_fMoveSpeed;
    float m_fMoveAngle;
    float m_fAngleY;
    u32 m_unActNo;
    u8 m_ucActReqPrio;
    u16 m_usActAtkAdjustUniqueID;
    u64 m_unActFreeWork;          // PS4 u32
    u64 m_ullHp[10];
    u16 m_usUseRegionBit;
    u64 m_ullHpWhite;
    u16 m_usCommonWork;
    u16 m_usCustomWork;
    u32 ocdActiveCount;
    CDataOcdActive m_OcdActiveList[ocdActiveCount];
    u32 ocdImmuneLvCount;
    CDataOcdImmuneLv m_OcdImmuneLvList[ocdImmuneLvCount];
    float m_fEnchantRate;
    float m_fAilmentDamage;
    CNetPos m_CliffPos;
    CVector3 m_CliffNormal;
    CNetPos m_CliffStartPos;
    CNetPos m_CliffStartOldPos;
    u64 m_unClimbEnemyID;         // PS4 u32
    s32 m_nJointNo;
    CVector3 m_JointOffset;
    u16 m_usNodeIndex;
    u16 m_usGeomIndex;
    u64 m_unTargetUID;            // PS4 u32
    CNetPos m_TargetPos;
    s32 m_nEncountAreaBuff[3];
    u32 m_unEnemyStatusGroupNoNum;
    u32 m_unEnemyStatusGroupNo[16];
    u32 m_unEnemyStatusSubGroupNo[16];
    u64 m_ullEnemyBitCtrlCollision;
    u8 m_ucEnemyCtrlRegionSelectNo;
    u64 m_ullEnemyBitCtrlParts;
    u64 m_ullEnemyBitCtrlWorkRate;
    u64 m_ullEnemyBitCtrlScale;
    u64 m_ullEnemyBitCtrlMontage;
    u32 m_unEnemyBitCtrlSyncBit;
    bool m_bIsEnemyWaitting;
    bool m_bIsEnemyStartWait;
    u64 m_ullAttackParamUIDForDmVec;
    CNetPos m_WallClimbPos;
    CVector3 m_WallClimbNormal;
    CNetPos m_WallClimbLandPos;
    u32 m_unStateLive;
    u8 m_ucCatchType;
    u8 m_ucCatchJointNo;
    u64 m_unCatchTargetUID;       // PS4 u32
    u32 m_unQuestID;
    u32 unk_u32[4];               // Season 3, new (PC writer 0x77d0e0; server: Unk0)
};

// SetBase + SetAdditional: 35.9.16 (C2S), 35.13.16 (S2C).
struct ContextSetInfo {
    CDataContextSetBase m_Base;
    CDataContextSetAdditional m_Additional;
};

// CDataEquipElementParam position of the EquipData element (PC 0x765a90); server names
// SlotNo, CrestId, Add are leads.
struct EquipElementParam {
    u8 unk_u8;
    u32 unk_u32;
    u16 unk_u16;
};

// CDataAddStatusParam position (PC 0x765ba0); server names EnhanceType, Unk0, EnhanceId, Unk1.
struct AddStatusParam {
    u8 unk_u8_0;
    u8 unk_u8_1;
    u16 unk_u16_0;
    u16 unk_u16_1;
};

// CDataContextEquipData: PC 0x75f480. PS4 has one list, CrestData {u16 m_usItemID}; PC has two.
struct CDataContextEquipData {
    u16 m_usItemID;
    u8 m_ucColorNo;
    u32 m_unQualityParam;        // server: PlusValue
    u32 elementCount;
    EquipElementParam unk_ElementList[elementCount];   // Season 3
    u32 addStatusCount;
    AddStatusParam unk_AddStatusList[addStatusCount];  // Season 3
};

// PC 0x75f5d0.
struct CDataContextEquipJobItemData {
    u16 m_usItemID;
    u8 m_ucSlotNo;
};

// PC 0x75f800.
struct CDataContextNormalSkillData {
    u8 m_ucSkillNo;
};

// PC 0x75f140.
struct CDataContextAcquirementData {
    u8 m_ucSlotNo;
    u32 m_unAcquirementNo;
    u8 m_ucAcquirementLv;
};

// New trailing list of CDataContextBase (PC 0x75f7e0 -> 0x7605e0); server: EmblemStatList of
// CDataEquipStatParam {EffectID, EffectValue}, no PS4 counterpart.
struct EquipStatParam {
    u8 unk_u8;
    u16 unk_u16;
};

// CDataContextBase: PC reader 0x75f250.
struct CDataContextBase {
    s32 m_nMemberIndex;
    u32 m_unPawnId;
    s32 m_nStageNo;
    s32 m_nStartPosNo;
    CNetPos m_Pos;
    float m_fAngleY;
    u8 m_ucSex;
    u8 m_ucColor;
    MtString m_wstrFirstName;
    MtString m_wstrLastName;
    u32 equipPerformanceCount;
    CDataContextEquipData m_ContextEquipPerformanceList[equipPerformanceCount];
    u32 equipVisualCount;
    CDataContextEquipData m_ContextEquipVisualList[equipVisualCount];
    u32 equipJobItemCount;
    CDataContextEquipJobItemData m_ContextEquipJobItemList[equipJobItemCount];
    bool m_bHideEquipHead;
    bool m_bHideEquipLantern;
    u8 m_ucHmType;
    u8 m_ucPawnType;
    u32 m_unCharacterId;
    bool m_bSetWaitFlag;
    u32 normalSkillCount;
    CDataContextNormalSkillData m_ContextNormalSkillList[normalSkillCount];
    u32 skillCount;
    CDataContextAcquirementData m_ContextSkillList[skillCount];
    u32 abilityCount;
    CDataContextAcquirementData m_ContextAbilityList[abilityCount];
    u32 m_unAbilityCostSum;
    u32 m_unAbilityCostMax;
    u32 equipStatCount;
    EquipStatParam unk_EquipStatList[equipStatCount];  // Season 3
};

// PC 0x75f6c0.
struct CDataContextJobData {
    u8 m_ucJob;
    u16 m_usLv;
    u64 m_ullExp;
    u64 m_ullJobPoint;
};

// PC 0x75e8e0.
struct CDataCommonU32 {
    u32 m_unValue;
};

// CDataContextPlayerInfo: PC reader 0x75f930, PS4 order; CatchTargetUID widened, two u32 appended.
struct CDataContextPlayerInfo {
    u8 m_ucJob;
    float m_fHP;
    float m_fMaxHP;
    float m_fWhiteHP;
    float m_fStamina;
    float m_fMaxStamina;
    float m_fWeight;
    u16 m_usLv;
    u64 m_ullExp;
    u32 m_unAtk;
    u32 m_unDef;
    u32 m_unMAtk;
    u32 m_unMDef;
    u32 m_unStrength;
    u32 m_unDownPower;
    u32 m_unShakePower;
    u32 m_unStanPower;
    u32 m_unConstitution;
    u32 m_unGuts;
    u64 m_ullJobPoint;
    u32 m_unGainHp;
    u32 m_unGainStamina;
    u32 m_unGainAttack;
    u32 m_unGainDefense;
    u32 m_unGainMagicAttack;
    u32 m_unGainMagicDefense;
    u32 m_unActNo;
    u8 m_ucRevivePoint;
    u8 m_ucCustomSkillGroup;
    u32 jobCount;
    CDataContextJobData m_JobList[jobCount];
    u32 chargeEffectCount;
    CDataCommonU32 m_ChargeEffectList[chargeEffectCount];
    u32 ocdActiveCount;
    CDataOcdActive m_OcdActiveList[ocdActiveCount];   // PC 0x76fb30
    CNetPos m_CliffPos;
    CVector3 m_CliffNormal;
    CNetPos m_CliffStartPos;
    CNetPos m_CliffStartOldPos;
    u8 m_ucCatchType;
    u8 m_ucCatchJointNo;
    u64 m_unCatchTargetUID;       // PS4 u32
    u16 m_usCustomWork;
    u32 unk_u32_0;                // Season 3, new
    u32 unk_u32_1;                // Season 3, new
};

// PC 0x772860.
struct CDataPawnReaction {
    u8 m_ucReactionType;
    u32 m_unMotionNo;
};

// PC 0x772950; server: SpSkillList.
struct SpSkill {
    u8 unk_u8_0;
    u8 unk_u8_1;
};

// CDataContextPawnInfo: PC 0x75f8d0. PS4 has only the reaction list.
struct CDataContextPawnInfo {
    u32 pawnReactionCount;
    CDataPawnReaction m_PawnReactionList[pawnReactionCount];
    u8 unk_u8[64];                // Season 3 (server: TrainingStatus)
    u32 spSkillCount;
    SpSkill unk_SpSkillList[spSkillCount];  // Season 3
};

// CDataContextResist: PC 0x75fcc0, 30 x u8 (= PS4).
struct CDataContextResist {
    u8 m_ucFireResist;
    u8 m_ucIceResist;
    u8 m_ucThunderResist;
    u8 m_ucHolyResist;
    u8 m_ucDarkResist;
    u8 m_ucSpreadResist;
    u8 m_ucFreezeResist;
    u8 m_ucShockResist;
    u8 m_ucAbsorbResist;
    u8 m_ucDarkElmResist;
    u8 m_ucPoisonResist;
    u8 m_ucSlowResist;
    u8 m_ucSleepResist;
    u8 m_ucStunResist;
    u8 m_ucWetResist;
    u8 m_ucOilResist;
    u8 m_ucSealResist;
    u8 m_ucCurseResist;
    u8 m_ucSoftResist;
    u8 m_ucStoneResist;
    u8 m_ucGoldResist;
    u8 m_ucFireReduceResist;
    u8 m_ucIceReduceResist;
    u8 m_ucThunderReduceResist;
    u8 m_ucHolyReduceResist;
    u8 m_ucDarkReduceResist;
    u8 m_ucAtkDownResist;
    u8 m_ucDefDownResist;
    u8 m_ucMAtkDownResist;
    u8 m_ucMDefDownResist;
};

// CDataEditInfo: PC reader 0x764550, 122 B, identical to PS4.
struct CDataEditInfo {
    u8 m_ucSex;
    u8 m_ucVoice;
    u16 m_usVoicePitch;
    u8 m_ucPersonality;
    u8 m_ucSpeechFreq;
    u8 m_ucBodyType;
    u8 m_ucHair;
    u8 m_ucBeard;
    u8 m_ucMakeup;
    u8 m_ucScar;
    u8 m_ucEyePresetNo;
    u8 m_ucNosePresetNo;
    u8 m_ucMouthPresetNo;
    u8 m_ucEyebrowTexNo;
    u8 m_ucColorSkin;
    u8 m_ucColorHair;
    u8 m_ucColorBeard;
    u8 m_ucColorEyebrow;
    u8 m_ucColorREye;
    u8 m_ucColorLEye;
    u8 m_ucColorMakeup;
    u16 m_usSokutobu;
    u16 m_usHitai;
    u16 m_usMimiJyouge;
    u16 m_usKannkaku;
    u16 m_usMabisasiJyouge;
    u16 m_usHanakuchiJyouge;
    u16 m_usAgoSakiHaba;
    u16 m_usAgoZengo;
    u16 m_usAgoSakiJyouge;
    u16 m_usHitomiOokisa;
    u16 m_usMeOokisa;
    u16 m_usMeKaiten;
    u16 m_usMayuKaiten;
    u16 m_usMimiOokisa;
    u16 m_usMimiMuki;
    u16 m_usElfMimi;
    u16 m_usMikenTakasa;
    u16 m_usMikenHaba;
    u16 m_usHohoboneRyou;
    u16 m_usHohoboneJyouge;
    u16 m_usHohoniku;
    u16 m_usErahoneJyouge;
    u16 m_usErahoneHaba;
    u16 m_usHanaJyouge;
    u16 m_usHanaHaba;
    u16 m_usHanaTakasa;
    u16 m_usHanaKakudo;
    u16 m_usKuchiHaba;
    u16 m_usKuchiAtsusa;
    u16 m_usEyebrowUVOffsetX;
    u16 m_usEyebrowUVOffsetY;
    u16 m_usWrinkle;
    u16 m_usWrinkleAlbedoBlendRate;
    u16 m_usWrinkleDetailNormalPower;
    u16 m_usMuscleAlbedoBlendRate;
    u16 m_usMuscleDetailNormalPower;
    u16 m_usHeight;
    u16 m_usHeadSize;
    u16 m_usNeckOffset;
    u16 m_usNeckScale;
    u16 m_usUpperBodyScaleX;
    u16 m_usBellySize;
    u16 m_usTeatScale;
    u16 m_usTekubiSize;
    u16 m_usKoshiOffset;
    u16 m_usKoshiSize;
    u16 m_usAnkleOffset;
    u16 m_usFat;
    u16 m_usMuscle;
    u16 m_usMotionFilter;
};
