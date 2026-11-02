// Group 13 INSTANCE CData of client 03040008 (PC, Season 3), shared by the instance packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/T004-instance.md
// sections 1, 2, 5, 6, 7, 11 and 20. "PC 0x..." is the reader or writer VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the
// fields carry (m_ and type prefix dropped) unless marked. Marks: V = read in IDA, I = inferred.
// A Season 3 field with no PS4 member is `unk_*`; server C# (Arrowgene) names are leads only and
// appear as "server: <name> (lead)".
// Includes Packet.hexpat and Character.hexpat (CDataWalletPoint, same PC reader 0x77c5a0, V);
// neither includes this file (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"

// CDataStageLayoutId: PC reader 0x77a330 and the inline triplets of every writer and NTC reader
// {u32, u8, u32} (V); PS4 CStageLayoutID {u32 m_unStageID, u8 m_ucLayerNo, u32 m_unGroupID} (V).
// 9 bytes (T004 1).
struct CDataStageLayoutId {
    u32 StageId;
    u8 LayerNo;
    u32 GroupId;
};

// CDataStageLayoutEnemyPresetEnemyInfoClient: PC reader 0x77a1b0 {u32 x3, u16 x3, u8 x7, bool x6}
// (V); PS4 the same with 5 bools (V). Season 3 adds a sixth bool after IsBloodEnemy (V width;
// captures: 13.0.2 with 5 bools fits 654/667, T004 2). 31 bytes. PS4 order RepopNum (+27) then
// RepopCount (+28) (V; the server swaps them, T004 21).
struct CDataStageLayoutEnemyPresetEnemyInfoClient {
    u32 EnemyId;
    u32 NamedEnemyParamsId;
    u32 RaidBossId;
    u16 Scale;
    u16 Lv;
    u16 HmPresetNo;
    u8 StartThinkTblNo;
    u8 RepopNum;
    u8 RepopCount;
    u8 EnemyTargetTypesId;
    u8 MontageFixNo;
    u8 SetType;
    u8 InfectionType;
    bool IsBossGauge;
    bool IsBossBGM;
    bool IsManualSet;
    bool IsAreaBoss;
    bool IsBloodEnemy;
    bool unk_bool;              // Season 3, no PS4 member (PC 0x77a1b0, V width); server: IsHighOrbEnemy (lead)
};

// CDataLayoutEnemyData: PC list reader 0x76ca20 element {Read_u8, then 0x77a1b0} (V); PS4
// CDataLayoutEnemyData {u8 m_ucPositionIndex, CDataStageLayoutEnemyPresetEnemyInfoClient m_EnemyInfo}.
struct CDataLayoutEnemyData {
    u8 PositionIndex;
    CDataStageLayoutEnemyPresetEnemyInfoClient EnemyInfo;
};

// CDataDropItemSetInfo: PC list reader 0x764400 element {u8, u8, f64, f32, f64} (V); PS4
// {u8 m_ucID, u8 m_ucMdlType, f64 m_dX, f32 m_fY, f64 m_dZ} (V). 22 bytes.
struct CDataDropItemSetInfo {
    u8 Id;
    u8 MdlType;
    double X;
    float Y;
    double Z;
};

// CDataNamedEnemyParamClient: PC reader 0x76f550 (list 0x76f450) {u32, u16 x22, u8} (V); PS4
// {u32 m_unId, u16 m_usRate* x22, u8 m_ucNameTypeId} in this order (V). 49 bytes. Never non-empty in
// the captures: code-only (T004 2, 22).
struct CDataNamedEnemyParamClient {
    u32 Id;
    u16 RateHp;
    u16 RateHpPart;
    u16 RatePhyAttackBase;
    u16 RatePhyAttackEq;
    u16 RatePhyDefenceBase;
    u16 RatePhyDefenceEq;
    u16 RateMagAttackBase;
    u16 RateMagAttackEq;
    u16 RateMagDefenceBase;
    u16 RateMagDefenceEq;
    u16 RateStr;
    u16 RateGuardAtk;
    u16 RateGuardDefBase;
    u16 RateGuardDefEq;
    u16 RateShrinkDef;
    u16 RateBlowDef;
    u16 RateDownDef;
    u16 RateShakeDef;
    u16 RateShrinkDefPart;
    u16 RateBlowDefPart;
    u16 RateOcdDef;
    u16 RateOcdAtk;
    u8 NameTypeId;
};

// CDataLayoutItemData: PC list reader 0x76cb40 element {u8, bool x4} (V); PS4 {u8 m_ucPosID,
// b8 m_bIsEmpty, b8 m_bIsGathered, b8 m_bIsAppearEnemy, b8 m_bIsTreasurePoint} (V). 5 bytes.
struct CDataLayoutItemData {
    u8 PosId;
    bool IsEmpty;
    bool IsGathered;
    bool IsAppearEnemy;
    bool IsTreasurePoint;
};

// CDataGatheringItemElement: PC list reader 0x769100 element (alloc 0x18) {u32 x4, bool} (V); PS4
// {u32 m_ulID, u32 m_ulItemId, u32 m_ulNum} (12 bytes, V). Season 3 adds a u32 and a bool (V widths;
// captures: the 12-byte element fits only the empty lists, 13.10.2 44/88, T004 6, 8). 17 bytes.
// Users: 13.6.2, 13.10.2.
struct CDataGatheringItemElement {
    u32 Id;
    u32 ItemId;
    u32 Num;
    u32 unk_u32;                // Season 3, no PS4 member; server: Quality (lead)
    bool unk_bool;              // Season 3, no PS4 member; server: IsHidden (lead)
};

// CDataGatheringItemGetRequest: PC list reader 0x769240 element and writer 0x77f9d0 element
// {u32, u32} (V); PS4 {u32 m_ulID, u32 m_ulNum} (V). Users: 13.8.1/2, 13.11.1/2.
struct CDataGatheringItemGetRequest {
    u32 Id;
    u32 Num;
};

// Season 3 element of the GatheringItemListRes_unk_0 second list (struct name neutral; server:
// CDataItemAmount, lead): PC list reader 0x7731b0 element
// {u32, u16} (V widths); no PS4 type. Type name I (T004 20); same shape as Quest CDataRewardItem but
// read by another reader (0x7771b0 there).
struct GatheringItemListRes_unk_1 {
    u32 unk_u32;                // server: ItemId (lead)
    u16 unk_u16;                // server: Num (lead)
};

// Season 3 GatheringItemListRes_unk_0 (struct name neutral; server: CDataGatheringItemRestriction,
// lead): PC list reader 0x773060 element
// (alloc 0x34) {u32, list 0x77c5a0 (CDataWalletPoint), list 0x7731b0} (V widths); no PS4 type. The
// 13.6.2 restriction list is never non-empty in the captures: the element is code-only (T004 6, 22).
struct GatheringItemListRes_unk_0 {
    u32 unk_u32;                                       // server: RestrictionId (lead)
    MtTypedArray<CDataWalletPoint> unk_WalletPointList;  // server: Unk1 (lead)
    MtTypedArray<GatheringItemListRes_unk_1> unk_ItemList;          // server: RequiredItems (lead)
};

// CDataOmData (COmData): PC reader 0x76fe10, list reader 0x76fd10 {Read_u64, Read_u32} (V); PS4
// {u32 m_ulKey, u32 m_ulValue} (V). Season 3 widens Key to u64 in every OM packet (V; captures: the
// u32 key fits 13.20.2 0/559, T004 11). Capture keys carry the high bit (0x80000000_001415b3).
struct CDataOmData {
    u64 Key;
    u32 Value;
};
