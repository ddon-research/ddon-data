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
    // T014b open (stored, no reader), kept unk: receive: 0x850010 stores it with sub_47bc80 into
    // the context +84; no getter of that +84 found (0x4745c0 reads +84 of another object as a
    // float) (...)
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
    // T014b I (consumer): basis 1: enemy-context array cContext +3144 (setter 0x479fd0, getter
    // 0x475520, block copy 0x4754e0/0x479fa0); read in enemy code, e.g. 0xcd5c80 uses element 1 as
    // a bitfield (bit 0 state, bits 1..4 and 5..8 4-bit timers) (...)
    u32 unk_u32[4];               // Season 3, new (PC writer 0x77d0e0; server: Unk0). Enemy-context
                                  // array cContext+0xC48, applied only to cContextInstEm
                                  // (0x850010 / 0x479fd0); same array as CtrlAction 0x3C (T001c 1, V)
};

// CDataContextEnemyStatus (name I, T001c 1): the second structure of 35.12.16, PC reader 0x760480
// into the 200-byte object of ctor 0x783270. No PS4 counterpart. Field names by shared setter with
// SetAdditional (T001c 1): the apply 0x850b30 calls the same setters as the SetAdditional apply
// 0x850010 (setter identity V, names from the PS4 DWARF CDataContextSetAdditional). Wire order V.
// 159 B plus the two Ocd lists (2n each).
struct CDataContextEnemyStatus {
    u64 m_ullHp[10];                  // setter 0x47a770
    u64 m_ullEnemyBitCtrlCollision;   // 0x479df0
    u64 m_ullEnemyBitCtrlParts;       // 0x479d90
    u64 m_ullEnemyBitCtrlWorkRate;    // 0x47a2f0
    u64 m_ullEnemyBitCtrlScale;       // 0x479ff0
    u64 m_ullEnemyBitCtrlMontage;     // 0x479e50
    u32 ocdActiveCount;
    CDataOcdActive m_OcdActiveList[ocdActiveCount];       // PC 0x76fb30
    u32 ocdImmuneLvCount;
    CDataOcdImmuneLv m_OcdImmuneLvList[ocdImmuneLvCount]; // PC 0x76fc20 {u8, u8}
    u32 m_unEnemyBitCtrlSyncBit;      // 0x479eb0
    u32 m_unStateLive;                // 0x47bf90
    u16 m_usUseRegionBit;             // 0x47c110
    u16 m_usCommonWork;               // 0x479980
    u16 m_usCustomWork;               // 0x479a10
    u8 m_ucEnemyCtrlRegionSelectNo;   // 0x479f50
    // T014b I (consumer): same array as CDataContextSetAdditional.unk_u32 (setter 0x479fd0 via the
    // apply 0x850b30); open: role without a name; no captures
    u32 unk_u32[4];                   // PC 0x757e60: fixed u32[4], no count on the wire. Season 3,
                                      // unnamed: same enemy-context array as SetAdditional
                                      // unk_u32[4] (setter 0x479fd0, cContextInstEm only)
};

// SetBase + SetAdditional: 35.9.16 (C2S), 35.13.16 (S2C).
struct ContextSetInfo {
    CDataContextSetBase m_Base;
    CDataContextSetAdditional m_Additional;
};

// CDataEquipElementParam position of the EquipData element (PC 0x765a90); server names
// SlotNo, CrestId, Add are leads.
struct EquipElementParam {
    // T014b V (consumer; lead agrees): basis 1: 0x4fa0d0 accepts 1..4 and fills cCrestParam[u8-1];
    // matches PS4 m_ucSlotNo
    u8 SlotNo;
    // T014b V (consumer): basis 1: stored as the crest item number and resolved with the item-param
    // lookup 0xb98c80 (the lookup addItemNotice uses for CDataItemList ItemId); PS4 counterpart
    // cCraftParam.mCraftElementItemNo[4]/mpElementParam[4] (...)
    u32 ItemId;
    // T014b I (consumer; lead agrees): basis 1: cCrestParam +12, passed by 0x4f9be0 to the crest
    // param callback 0x4ddaf0, whose handlers (e.g. 0x4ddb80) add it to the crest param value; no
    // PS4 member; server lead Add
    u16 Add;
};

// Season 3 list element of CDataContextEquipData (PC 0x765ba0), no PS4 counterpart; struct name neutral
// (TC1). server: CDataAddStatusParam {EnhanceType, Unk0, EnhanceId, Unk1} (lead).
struct CDataContextEquipData_unk_0 {
    // T014b V (consumer; lead agrees): basis 1: setter 0x5f8030 switches on it: 1 -> ctrl +4, 2 ->
    // ctrl +6/+8/+10 by unk_u8_1, 3 -> ctrl +12; getters 0x5f7f40/0x5f7f80 and status calc 0x4dce10
    // loop the same three types; values 1..3; server lead EnhanceType
    u8 EnhanceType;
    // T014b V (consumer): basis 1: setter 0x5f8030 uses it only for type 2, as a 1-based slot (a3-1
    // <= 2 -> ctrl +6+2*(a3-1)); values 1..3; name from the role (no string); server lead Unk0
    u8 EnhanceSlotNo;
    // T014b V (consumer; lead agrees): basis 1: stored as the enhance id of its type/slot; 0x4dde40
    // rejects 0 and ids above the rEnhancedParamList count and applies entry id-1 (EnhancedDataList
    // {ParamId, ParamValue}) through table 0x1b0fcb8 (...)
    u16 EnhanceId;
    // T014b I (consumer): basis 1: setter 0x5f8030 keeps it only for type 1 (ctrl +14) and for type
    // 2 slot 1 (ctrl +16); no reader of ctrl +14/+16 found (word-access scan for cItemEquipParam
    // +106/+108 after [x+28h] and ctrl +14/+16 after +5Ch) (...)
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
    CDataContextEquipData_unk_0 unk_List[addStatusCount];  // Season 3; server: AddStatusParamList (lead)
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

// New trailing list of CDataContextBase (PC 0x75f7e0 -> 0x7605e0), no PS4 counterpart; struct name
// neutral (TC1). server: EmblemStatList of CDataEquipStatParam {EffectID, EffectValue} (lead).
struct CDataContextBase_unk_0 {
    // T014b I (consumer + enum range): basis 1/3: selects the stat handler in table 0x1b0fcb8 (kind
    // < 0x4B) in status calc 0x4dd630, the same table and kind space as rEnhancedParamList ParamId
    // (0x4dde40) and the rItemList equip-param kinds (PS4 DWARF enum (...)
    u8 EquipParamKind;
    // T014b V (consumer): basis 1: the value argument of the kind handler (0x4dd630: handler(this,
    // arg, u16)); values 0..5000; the context list is applied only to the category-10/sub-5 equip
    // item (0x4f9620); server lead EffectValue (EmblemStatList)
    u16 EquipParamValue;
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
    CDataContextBase_unk_0 unk_List[equipStatCount];  // Season 3; server: EmblemStatList (lead)
};

// PC 0x75f6c0.
struct CDataContextJobData {
    u8 m_ucJob;
    u16 m_usLv;
    u64 m_ullExp;
    u64 m_ullJobPoint;
};

// CDataCommonU32 (PC 0x75e8e0) is defined in Packet.hexpat.

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
    // T014b V (property name): basis 1: stored into cContext +14992, which PC createProperty
    // 0x471a50 names mRoomNo; 0xbb12b0 compares the own mRoomNo with the own CharId (property
    // CharId +8676 in 0x471180, getter 0x4770b0) (...)
    u32 RoomNo;                // Season 3, new
    // T014b V (property name): basis 1: OR-ed into cContext +14996, which PC createProperty
    // 0x471a50 names mPlayerStatusFlag; captures 0
    u32 PlayerStatusFlag;                // Season 3, new
};

// PC 0x772860.
struct CDataPawnReaction {
    u8 m_ucReactionType;
    u32 m_unMotionNo;
};

// Season 3 list element of CDataContextPawnInfo (PC 0x772950), no PS4 counterpart; struct name
// neutral (TC1). server: SpSkillList of CDataSpSkill (lead).
struct CDataContextPawnInfo_unk_0 {
    // T014b I (binary hint; lead agrees): basis 3: same element reader 0x772950 and consumer
    // 0x6042c0 as the PAWN_SP_SKILL group (69.0.2 reader 0x813510, string
    // OnPacket_PAWN_SP_SKILL_GET_ACTIVE_SKILL_RES; 69.6.16 handler 0x7ec870 builds the same
    // 3+3-byte record) (...)
    u8 SpSkillId;
    // T014b I (binary hint; lead agrees): basis 3: second byte of the same pawn special-skill pair
    // (record b[i]); values 1..3; server lead SpSkillLv
    u8 SpSkillLv;
};

// CDataContextPawnInfo: PC 0x75f8d0. PS4 has only the reaction list.
struct CDataContextPawnInfo {
    u32 pawnReactionCount;
    CDataPawnReaction m_PawnReactionList[pawnReactionCount];
    // T014b I (binary hint; lead agrees): basis 3: the 64 bytes go as one block (0x5fd640 object)
    // into the pawn context (...)
    u8 TrainingStatus[64];                // Season 3 (server: TrainingStatus)
    u32 spSkillCount;
    CDataContextPawnInfo_unk_0 unk_List[spSkillCount];  // Season 3; server: SpSkillList (lead)
};

// CDataContextResist: PC 0x75fcc0, 30 x u8 (= PS4). Field names: the PS4 members without m_uc (TC1).
struct CDataContextResist {
    u8 FireResist;
    u8 IceResist;
    u8 ThunderResist;
    u8 HolyResist;
    u8 DarkResist;
    u8 SpreadResist;
    u8 FreezeResist;
    u8 ShockResist;
    u8 AbsorbResist;
    u8 DarkElmResist;
    u8 PoisonResist;
    u8 SlowResist;
    u8 SleepResist;
    u8 StunResist;
    u8 WetResist;
    u8 OilResist;
    u8 SealResist;
    u8 CurseResist;
    u8 SoftResist;
    u8 StoneResist;
    u8 GoldResist;
    u8 FireReduceResist;
    u8 IceReduceResist;
    u8 ThunderReduceResist;
    u8 HolyReduceResist;
    u8 DarkReduceResist;
    u8 AtkDownResist;
    u8 DefDownResist;
    u8 MAtkDownResist;
    u8 MDefDownResist;
};

// CDataEditInfo: PC reader 0x764550, 122 B, identical to PS4. Field names: the PS4 members without
// m_uc/m_us (TC1).
struct CDataEditInfo {
    u8 Sex;
    u8 Voice;
    u16 VoicePitch;
    u8 Personality;
    u8 SpeechFreq;
    u8 BodyType;
    u8 Hair;
    u8 Beard;
    u8 Makeup;
    u8 Scar;
    u8 EyePresetNo;
    u8 NosePresetNo;
    u8 MouthPresetNo;
    u8 EyebrowTexNo;
    u8 ColorSkin;
    u8 ColorHair;
    u8 ColorBeard;
    u8 ColorEyebrow;
    u8 ColorREye;
    u8 ColorLEye;
    u8 ColorMakeup;
    u16 Sokutobu;
    u16 Hitai;
    u16 MimiJyouge;
    u16 Kannkaku;
    u16 MabisasiJyouge;
    u16 HanakuchiJyouge;
    u16 AgoSakiHaba;
    u16 AgoZengo;
    u16 AgoSakiJyouge;
    u16 HitomiOokisa;
    u16 MeOokisa;
    u16 MeKaiten;
    u16 MayuKaiten;
    u16 MimiOokisa;
    u16 MimiMuki;
    u16 ElfMimi;
    u16 MikenTakasa;
    u16 MikenHaba;
    u16 HohoboneRyou;
    u16 HohoboneJyouge;
    u16 Hohoniku;
    u16 ErahoneJyouge;
    u16 ErahoneHaba;
    u16 HanaJyouge;
    u16 HanaHaba;
    u16 HanaTakasa;
    u16 HanaKakudo;
    u16 KuchiHaba;
    u16 KuchiAtsusa;
    u16 EyebrowUVOffsetX;
    u16 EyebrowUVOffsetY;
    u16 Wrinkle;
    u16 WrinkleAlbedoBlendRate;
    u16 WrinkleDetailNormalPower;
    u16 MuscleAlbedoBlendRate;
    u16 MuscleDetailNormalPower;
    u16 Height;
    u16 HeadSize;
    u16 NeckOffset;
    u16 NeckScale;
    u16 UpperBodyScaleX;
    u16 BellySize;
    u16 TeatScale;
    u16 TekubiSize;
    u16 KoshiOffset;
    u16 KoshiSize;
    u16 AnkleOffset;
    u16 Fat;
    u16 Muscle;
    u16 MotionFilter;
};

// Context body variants of the packets without captures (T001c 2; no captures, unvalidated; no
// pattern uses them yet). Order V from the PC readers, names from the PS4 DWARF types:
// - CDataLobbyContextPlayer: 35.0.2 RES (PC reader 0x804fb0 -> 0x76d6a0) and 35.0.16; no Resist.
// - CDataPartyContextPlayer: 35.1.2 RES / 35.1.16 NTC (0x8051b0 / 0x805140 -> 0x771280).
// - CDataAllContextPlayer: 35.2.2 RES / 35.2.16 NTC (0x804e80 / 0x804e10 -> 0x758d10, a copy of
//   0x771280). Party and All add CDataContextResist between PlayerInfo and EditInfo; spec 005 P4
//   2.3's "35.1.16/35.2.16 equal 35.0.16" is contradicted (T001c 2, C).
// - CDataPartyContextPawn: 35.3.2 / 35.4.2 RES, 35.4.16 NTC (0x8050b0 / 0x8052b0 / 0x805240 ->
//   0x771200).
// The packets wrap them as: RES `s32 Error; if (Error == 0) { s32 Result; u32 CharacterID (pawn:
// PawnID); <context> }`; NTC `u32 CharacterID (pawn: PawnID); <context>`.
struct CDataLobbyContextPlayer {
    CDataContextBase m_Base;
    CDataContextPlayerInfo m_PlayerInfo;
    CDataEditInfo m_EditInfo;
};

struct CDataPartyContextPlayer {
    CDataContextBase m_Base;
    CDataContextPlayerInfo m_PlayerInfo;
    CDataContextResist m_ResistInfo;
    CDataEditInfo m_EditInfo;
};

struct CDataAllContextPlayer {
    CDataContextBase m_Base;
    CDataContextPlayerInfo m_PlayerInfo;
    CDataContextResist m_ResistInfo;
    CDataEditInfo m_EditInfo;
};

struct CDataPartyContextPawn {
    CDataContextBase m_Base;
    CDataContextPlayerInfo m_PlayerInfo;
    CDataContextPawnInfo m_PawnInfo;
    CDataContextResist m_ResistInfo;
    CDataEditInfo m_EditInfo;
};
