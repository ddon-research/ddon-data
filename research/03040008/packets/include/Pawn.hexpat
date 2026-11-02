// Pawn CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11b-old-patterns.md
// section 14 and the shared-structure table. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type. CDataPawnListData and
// CDataPawnCraftSkill also match the PS4 recompilation (PacketData/Pawn.h); CDataRegisterdPawnList
// has no class there. Marks: V = read in IDA, I = inferred.
// Since spec 006 T007b also the group 8 PAWN and 53 PARTNER_PAWN types of
// specs/006-packet-pattern-coverage/research/T007-pawn-partner.md sections 1 and 6 (field names: the
// PS4 DWARF member, m_ and type prefix dropped, V; Season 3 fields with no PS4 member are `unk_*`,
// server C# names as "server: <name> (lead)").
// Includes Packet.hexpat and Login.hexpat (CDataEquipItemInfo; Login includes Character, Context
// and GP); none of them includes this file (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Login.hexpat"

// CDataPawnCraftSkill: PC list reader 0x771c80 {u8, u32} (V); PS4 CDataPawnCraftSkill
// {u8 m_ucType, u32 m_unLevel}.
struct CDataPawnCraftSkill {
    u8 Type;
    u32 Level;
};

// CDataPawnListData: PC reader 0x772750 {u8, u32, u32, list CDataPawnCraftSkill, u32, u64} (V);
// PS4 CDataPawnListData, same order (m_ullLatestReturnDate u64).
struct CDataPawnListData {
    u8 Job;
    u32 Level;
    u32 CraftRank;
    MtTypedArray<CDataPawnCraftSkill> PawnCraftSkillList;
    u32 CommentSize;
    u64 LatestReturnDate;
};

// CDataRegisterdPawnList: PC list reader 0x776610, element 0x7766d0 {s32, MtString, u8, u32, u64,
// CDataPawnListData} (V); PS4 Read_CDataRegisterdPawnList_ identical (P11b 14).
struct CDataRegisterdPawnList {
    s32 PawnId;
    MtString Name;
    u8 Sex;
    u32 RentalCost;
    u64 Updated;
    CDataPawnListData PawnListData;
};

// ---- spec 006 T007b (T007 sections 1, 6) ----

// CDataPartnerPawnData: PC reader 0x7710a0 {u32, u32, u8} (V); PS4 CDataPartnerPawnData {u32
// m_unPawnId, u32 m_unLikability, u8 m_ucPersonality} (V). Users: 8.2.2, 53.8.2 (same PC reader).
struct CDataPartnerPawnData {
    u32 PawnId;
    u32 Likability;
    u8 Personality;
};

// CDataPawnList: PC list reader 0x7725c0, element 0x772680 {s32, u32, MtString, u8, u8, u8,
// CDataPawnListData 0x772750, u32, u32, u32} (V); PS4 Read_CDataPawnList__0 0x1a2ca80 {s32 m_nPawnId,
// u32 m_unSlotNo, m_wstrName, u8 m_ucSex, u8 m_ucPawnState, u8 m_ucShareRange, m_PawnListData} (V).
// The three trailing u32 are Season 3 (V by code; the PS4 element fails 119/119 captures, T007 1.2).
// User: 8.2.2.
struct CDataPawnList {
    s32 PawnId;
    u32 SlotNo;
    MtString Name;
    u8 Sex;
    u8 PawnState;
    u8 ShareRange;
    CDataPawnListData PawnListData;
    // T014b V (consumer); I (role): handler 0x7eab80 -> 0x7eaac0 calls sGame_0 0xbcdac0(PawnId +4,
    // element +72) for every element: a 16-slot PawnId -> value table (+196); the getter 0xbccbd0
    // is read by 0x9a1940, which switches a mode when the value is >= 2
    u32 unk_u32_0;              // Season 3, no PS4 member; server: Unk0 (lead)
    // T014b open (V store; no reader found), kept unk: 0x881da0 copies element +76 to the pawn
    // entry +100 (conn +18436 list); no reader of that member was found
    u32 unk_u32_1;              // Season 3, no PS4 member; server: TrainingExp (lead)
    // T014b open (V store; no reader found), kept unk: 0x881da0 copies element +80 to the pawn
    // entry +104 (conn +18436 list); no reader of that member was found
    u32 unk_u32_2;              // Season 3, no PS4 member; server: Unk2 (lead)
};

// CDataRentedPawnList: PC list reader 0x776ce0, element 0x776da0 {s32, u32, MtString, u8 x4,
// CDataPawnListData, u8} (V); PS4 0x1a2b780, same members (V). No Season 3 change. User: 8.8.2.
struct CDataRentedPawnList {
    s32 PawnId;
    u32 SlotNo;
    MtString Name;
    u8 Sex;
    u8 PawnState;
    u8 CraftCount;
    u8 AdventureCount;
    CDataPawnListData PawnListData;
    u8 PawnType;
};

// CDataLostPawnList: PC list reader 0x76d980, element 0x76da40 {s32, u32, MtString, u8 x3, u32,
// CDataPawnListData} (V); PS4 0x1a2ae70, same members (V). No Season 3 change. Never non-empty in
// the captures: code-only. User: 8.20.2.
struct CDataLostPawnList {
    s32 PawnId;
    u32 SlotNo;
    MtString Name;
    u8 Sex;
    u8 PawnState;
    u8 ShareRange;
    u32 ReviveCost;
    CDataPawnListData PawnListData;
};

// CDataPawnFeedback: PC reader 0x771fd0, list 0x771ed0 {u8, u8, u8} (V); PS4 CPawnFeedback {u8
// m_ucType, u8 m_ucValue, u8 m_ucCommentNo} (V).
struct CDataPawnFeedback {
    u8 Type;
    u8 Value;
    u8 CommentNo;
};

// CDataPawnHistory: PC list reader 0x772020, element 0x7720e0 {u32, CDataCommunityCharacterBaseInfo
// 0x75ecf0, u64, u64, u8, u8, u32, CDataPawnFeedback} (V); PS4 0x1a2a530, same members (V).
// Users: 8.28.2, 8.34.16.
struct CDataPawnHistory {
    u32 PawnID;
    CDataCommunityCharacterBaseInfo DebtorBaseInfo;
    u64 ReturnDate;
    u64 AdventureTime;
    u8 AdventureCount;
    u8 CraftCount;
    u32 KillEnemyNum;
    CDataPawnFeedback PawnFeedback;
};

// CDataAchievementIdentifier: read inline by PC 0x7596f0 {u32, u32} (V); PS4 {u32 m_unUid,
// u32 m_unIndex} (V).
struct CDataAchievementIdentifier {
    u32 Uid;
    u32 Index;
};

// CDataArisenProfile: PC reader 0x7596f0 {u8, u32, u32, u16, u32} (V); PS4 {u8 m_ucBackgroundID,
// CAchievementIdentifier m_Title, u16 m_usMotionID, u32 m_unMotionFrameNo} (V).
struct CDataArisenProfile {
    u8 BackgroundID;
    CDataAchievementIdentifier Title;
    u16 MotionID;
    u32 MotionFrameNo;
};

// CDataPawnProfile: PC reader 0x7727d0 {CDataCommunityCharacterBaseInfo, CDataArisenProfile,
// MtString, u32} (V); PS4 {m_OwnerBaseInfo, CArisenProfile m_ProfileInfo, m_wstrComment,
// u32 m_unRentalCost} (V). User: 8.33.16.
struct CDataPawnProfile {
    CDataCommunityCharacterBaseInfo OwnerBaseInfo;
    CDataArisenProfile ProfileInfo;
    MtString Comment;
    u32 RentalCost;
};

// CDataPawnTotalScore: PC reader 0x772a40 {u32, u32, u32, list 0x771ed0} (V); PS4 {u32
// m_unRentalCount, u32 m_unBattleCount, u32 m_unCraftCount, m_AveragePawnFeedbackList} (V).
// User: 8.35.16.
struct CDataPawnTotalScore {
    u32 RentalCount;
    u32 BattleCount;
    u32 CraftCount;
    MtTypedArray<CDataPawnFeedback> AveragePawnFeedbackList;
};

// CDataOrbCategoryStatus: PC list reader 0x76fe50 {u8, u8} (V); PS4 {u8 m_ucCategoryID,
// u8 m_ucReleaseNum} (V).
struct CDataOrbCategoryStatus {
    u8 CategoryID;
    u8 ReleaseNum;
};

// CDataOrbPageStatus: PC list reader 0x7702d0 {u8, list 0x76fe50} (V); PS4 {u8 m_ucPageNo,
// OrbCategoryStatusVec m_CategoryStatusList} (V). User: 8.36.16.
struct CDataOrbPageStatus {
    u8 PageNo;
    MtTypedArray<CDataOrbCategoryStatus> CategoryStatusList;
};

// CDataJobOrbTreeStatus: PC list reader 0x76c270 {u8, bool, f32} (V); PS4 {u8 m_ucJobID,
// b8 m_bIsReleased, f32 m_fRate} (V). User: 8.36.16 (two lists).
struct CDataJobOrbTreeStatus {
    u8 JobID;
    bool IsReleased;
    float Rate;
};

// CDataCharacterJobData: PC list reader 0x75c660, element 0x75c770 {u8, u32, u32, u32, u16 x10,
// u8 x30} (V); PS4 CDataCharacterJobData, same widths and order (V). User: CDataPawnInfo.
struct CDataCharacterJobData {
    u8 Job;
    u32 Exp;
    u32 JobPoint;
    u32 Lv;
    u16 Atk;
    u16 Def;
    u16 MAtk;
    u16 MDef;
    u16 Strength;
    u16 DownPower;
    u16 ShakePower;
    u16 StunPower;
    u16 Constitution;
    u16 Guts;
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

// CDataCharacterEquipData: PC list reader 0x75c190, element 0x765fb0 {list CDataEquipItemInfo
// 0x766070} (V); PS4 {MtTypedArray<CDataEquipItemInfo> m_EquipList} (V). The element is the
// Season 3 CDataEquipItemInfo of Login.hexpat, not the PS4 one (V, T007 1.1).
struct CDataCharacterEquipData {
    MtTypedArray<CDataEquipItemInfo> EquipList;
};

// CDataEquipJobItem: PC list reader 0x766120 {u32, u8} (V); PS4 {u32 m_unJobItemID,
// u8 m_ucEquipSlotNo} (V).
struct CDataEquipJobItem {
    u32 JobItemID;
    u8 EquipSlotNo;
};

// CDataPawnCraftData: PC reader 0x771c10 {u32 x4, list 0x771c80} (V); PS4 CPawnCraftData {u32
// m_unCraftExp, m_unCraftRank, m_unCraftRankLimit, m_unCraftPoint, m_PawnCraftSkillList} (V).
struct CDataPawnCraftData {
    u32 CraftExp;
    u32 CraftRank;
    u32 CraftRankLimit;
    u32 CraftPoint;
    MtTypedArray<CDataPawnCraftSkill> PawnCraftSkillList;
};

// CDataOrbGainExtendParam: PC reader 0x7701c0, u16 x13 (V); PS4 COrbGainExtendParam, same members
// (V; m_usJewerlySlot spelling kept).
struct CDataOrbGainExtendParam {
    u16 HpMax;
    u16 StaminaMax;
    u16 Attack;
    u16 Defence;
    u16 MagicAttack;
    u16 MagicDefence;
    u16 AbilityCost;
    u16 JewerlySlot;
    u16 UseItemSlot;
    u16 MaterialItemSlot;
    u16 EquipItemSlot;
    u16 MainPawnSlot;
    u16 SupportPawnSlot;
};

// Season 3 member of CDataPawnInfo: PC reader 0x772e80, u32 x5 (V widths); no PS4 type. Names unk.
// server: CDataPawnTrainingProfile (lead)
struct CDataPawnInfo_unk_0 {
    // T014b open (no reader found), kept unk: CDataPawnInfo +500 (reader 0x772e80, only behind
    // CDataPawnInfo 0x772180 of 8.3.2/8.9.2/8.11.2); the MYPAWN packet is kept whole at the pawn
    // entry +88 (0x881d10, conn +18436 list) (...)
    u32 unk_u32_0;              // server: TrainingExp (lead)
    // T014b open (no reader found), kept unk: CDataPawnInfo +500 (reader 0x772e80, only behind
    // CDataPawnInfo 0x772180 of 8.3.2/8.9.2/8.11.2); the MYPAWN packet is kept whole at the pawn
    // entry +88 (0x881d10, conn +18436 list) (...)
    u32 unk_u32_1;              // server: DialogCount (lead)
    // T014b open (no reader found), kept unk: CDataPawnInfo +500 (reader 0x772e80, only behind
    // CDataPawnInfo 0x772180 of 8.3.2/8.9.2/8.11.2); the MYPAWN packet is kept whole at the pawn
    // entry +88 (0x881d10, conn +18436 list) (...)
    u32 unk_u32_2;              // server: DialogCountMax (lead)
    // T014b open (no reader found), kept unk: CDataPawnInfo +500 (reader 0x772e80, only behind
    // CDataPawnInfo 0x772180 of 8.3.2/8.9.2/8.11.2); the MYPAWN packet is kept whole at the pawn
    // entry +88 (0x881d10, conn +18436 list) (...)
    u32 unk_u32_3;              // server: AttackFrequencyAndDistance (lead)
    // T014b open (no reader found), kept unk: CDataPawnInfo +500 (reader 0x772e80, only behind
    // CDataPawnInfo 0x772180 of 8.3.2/8.9.2/8.11.2); the MYPAWN packet is kept whole at the pawn
    // entry +88 (0x881d10, conn +18436 list) (...)
    u32 unk_u32_4;              // server: TrainingLv (lead)
};

// CDataPawnInfo (Season 3): PC reader 0x772180 (V, T007 1.1); PS4 Read_CDataPawnInfo_ 0x1a2bfc0,
// CDataPawnInfo. Items 1-12 and 14-29 match the PS4 members in order (V), with the Season 3
// CDataEquipItemInfo inside the equip lists. Season 3 adds item 13 (list {u8, u16}, reader 0x766210,
// the reader of CDataEquipItemInfo's third list: CDataContextBase_unk_0 shape) and items 30-32 (u8[64] by
// 0x772aa0, u32 x5 by 0x772e80, list {u8, u8} by 0x772950). Two of them (u8[64], the {u8, u8} list)
// are also in Context's CDataContextPawnInfo (PC 0x75f8d0, V); the u32 x5 has only this reader
// behind it (0x772e80). The PS4 body fails 72/72 (8.3.2) and 2/2 (8.9.2) captures.
// Users: 8.3.2, 8.9.2.
struct CDataPawnInfo {
    u32 Version;
    MtString Name;
    CDataEditInfo EditInfo;                                   // PC 0x764550
    u8 State;
    u32 MaxHp;
    u32 MaxStamina;
    u8 Job;
    MtTypedArray<CDataCharacterJobData> CharacterJobDataList;
    MtTypedArray<CDataCharacterEquipData> CharacterEquipDataList;
    MtTypedArray<CDataCharacterEquipData> CharacterEquipViewDataList;
    MtTypedArray<CDataEquipJobItem> CharacterEquipJobItemList;
    u8 JewelrySlotNum;
    MtTypedArray<CDataContextBase_unk_0> unk_List_0;                  // Season 3, PC 0x766210 {u8, u16}; server: CharacterItemSlotInfoList (lead)
    CDataPawnCraftData CraftData;
    MtTypedArray<CDataPawnReaction> PawnReactionList;         // PC 0x772860
    bool HideEquipHead;
    bool HideEquipLantern;
    u8 AdventureCount;
    u8 CraftCount;
    u8 MaxAdventureCount;
    u8 MaxCraftCount;
    MtTypedArray<CDataContextNormalSkillData> ContextNormalSkillList;   // PC 0x75f800
    MtTypedArray<CDataContextAcquirementData> ContextSkillList;         // PC 0x75f140
    MtTypedArray<CDataContextAcquirementData> ContextAbilityList;       // PC 0x75f140
    u32 AbilityCostMax;
    CDataOrbGainExtendParam ExtendParam;
    u8 PawnType;
    u8 ShareRange;
    u32 Likability;
    // T014b I (binary hint: shared reader; lead agrees): the u8[64] at CDataPawnInfo +432 is read
    // by 0x772aa0, the reader that also fills PAWN_TRAINING_GET_TRAINING_STATUS_RES (handler
    // 0x7ed6d0); same naming as CDataContextPawnInfo.unk_u8 in part 2
    u8 TrainingStatus[64];                                            // Season 3, PC 0x772aa0; server: TrainingStatus (lead)
    CDataPawnInfo_unk_0 unk_u32x5;                            // Season 3, PC 0x772e80; server: TrainingProfile (lead)
    MtTypedArray<CDataContextPawnInfo_unk_0> unk_List_1;                         // Season 3, PC 0x772950; server: SpSkillList (lead)
};

// CDataPartnerPawnRewardParam: read inline by the PC element reader of list 0x7710f0 {u32, u32} (V);
// PS4 {u32 m_unParamTypeId, u32 m_unUID} (V).
struct CDataPartnerPawnRewardParam {
    u32 ParamTypeId;
    u32 UID;
};

// CDataPartnerPawnReward: PC list reader 0x7710f0 element {u8, u32, u32} (V); PS4 {u8 m_ucType,
// CPartnerPawnRewardParam m_Value} (V). Users: 53.4.2, 53.6.2.
struct CDataPartnerPawnReward {
    u8 Type;
    CDataPartnerPawnRewardParam Value;
};
