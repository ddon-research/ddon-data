// Craft CData of client 03040008 (PC, Season 3) shared by the packet patterns of groups 30 CRAFT
// and 54 CRAFT_RECIPE.
//
// Source: specs/006-packet-pattern-coverage/research/T013-small-groups.md sections 1, 2, 4, 14 and
// 16 (T013b). Names are PS4 02020005 DWARF members (m_/type prefix dropped, V) unless marked (I) or
// `unk_*`. Users: 30.0.2, 30.13.2, 30.15.2, 54.0.2.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Pawn.hexpat"

// CDataCraftPawnInfo: PC list reader 0x760870 {u32, MtString} (V); PS4 Read_CDataCraftPawnInfo_
// 0x1a0d5f0 {u32 m_unPawnID, MtString m_wstrName}: same widths and order (V).
struct CDataCraftPawnInfo {
    u32 PawnID;
    MtString Name;
};

// CDataCraftProgress (Season 3): PC list reader 0x760b60 (loc_, read linearly), element 0x760c20:
// u32, MtString, list CDataCraftPawnInfo, list 0x75e8e0 {u32}, u32 +56, u32 +60, s32 +64, u32 +68,
// u32 +72, u16 +76, u32 +80, bool +84, u32 +88 (V, T013 2). PS4 Read_CDataCraftProgress__0
// 0x1a0d500 {m_CraftMainPawnInfo, m_CraftSupportPawnInfoList, u32 m_unRecipeID, m_unExp,
// s32 m_nNpcActionID, u32 m_unItemID, m_unToppingID, m_unRemainTime, b8 m_bExpBonus,
// u32 m_unCreateCount}. Season 3 adds the u32 list and the u16; the names after NpcActionID are I
// by order (which side of the u16 each PS4 u32 belongs is inferred). Code-only: the progress list
// is empty in every capture (10/10).
struct CDataCraftProgress {
    CDataCraftPawnInfo CraftMainPawnInfo;
    MtTypedArray<CDataCraftPawnInfo> CraftSupportPawnInfoList;
    MtTypedArray<CDataCommonU32> unk_u32_list;   // Season 3, PC 0x75e8e0; server: CraftMasterLegendPawnInfoList as CDataCraftPawnInfo (lead, contradicted by the PC reader)
    u32 RecipeID;
    u32 Exp;
    s32 NpcActionID;
    u32 ItemID;         // I: position
    u32 ToppingID;      // I: position
    u16 unk_u16;        // Season 3, no PS4 member; server: AdditionalStatusId (lead)
    u32 RemainTime;     // I: position
    bool ExpBonus;
    u32 CreateCount;
};

// CDataCraftPawnList: PC list reader 0x760960 {u32 x4} (V); PS4 Read_CDataCraftPawnList_ 0x1a0d260
// {u32 m_unPawnID, m_unCraftExp, m_unCraftPoint, m_unCraftRankLimit} (V).
struct CDataCraftPawnList {
    u32 PawnID;
    u32 CraftExp;
    u32 CraftPoint;
    u32 CraftRankLimit;
};

// CDataCraftTimeSaveCost: PC list reader 0x7611f0 {u8, u8, u32, u32} (V); PS4 0x19e8e80 {u8 m_ucID,
// u8 m_ucType, u32 m_unPrice, u32 m_unSec} (V).
struct CDataCraftTimeSaveCost {
    u8 ID;
    u8 Type;
    u32 Price;
    u32 Sec;
};

// CDataCraftSkillRate: PC list reader 0x7610f0 {u8, u8, u8} (V); PS4 0x19e8bb0 {u8 m_ucPawnType,
// u8 m_ucSkillType, u8 m_ucRate} (V).
struct CDataCraftSkillRate {
    u8 PawnType;
    u8 SkillType;
    u8 Rate;
};

// CDataCraftSettingUnkPawn (struct name I: pawn records by capture, T013 4): PC list reader 0x77abd0,
// element 0x77ace0 {u32, u8, u32, u32, MtString, u32, list 0x771c80} (V); no PS4 counterpart
// (Season 3 tail of 30.13.2). Captures: (309, 5, 1, 10000006, "Qualio", 100, 10 skills).
// server: CDataRegisteredLegendPawnInfo (lead).
struct CDataCraftSettingUnkPawn {
    u32 unk_u32_0;
    u8 unk_u8;
    u32 unk_u32_1;
    u32 unk_u32_2;
    MtString unk_Name;
    u32 unk_u32_3;
    MtTypedArray<CDataPawnCraftSkill> unk_SkillList;
};

// CDataCraftSettingUnkElement (struct name I): PC list reader 0x760db0, element 0x760ea0 {u32 x5,
// bool} (V); no PS4 counterpart (Season 3 tail of 30.13.2). server: CDataRefiningMaterialInfo (lead).
struct CDataCraftSettingUnkElement {
    u32 unk_u32_0;
    u32 unk_u32_1;
    u32 unk_u32_2;
    u32 unk_u32_3;
    u32 unk_u32_4;
    bool unk_bool;
};

// CDataMDataCraftMaterial (Season 3): PC list reader 0x76dee0 {u32, u32, u32, bool} (V); PS4
// 0x19e72a0 {u32 m_unItemID, m_unNum, m_unSortNo}: Season 3 adds the bool (the PS4 material fails
// 3/3 54.0.2 captures, T013 14). server: IsSp (lead).
struct CDataMDataCraftMaterial {
    u32 ItemID;
    u32 Num;
    u32 SortNo;
    bool unk_bool;      // Season 3, 0 in all 354 captured materials
};

// CDataMDataCraftRecipe: PC list reader 0x76e000 (loc_, read linearly), element 0x76e130 (V); PS4
// 0x19e7880 {u32 m_unRecipeID, m_unItemID, m_unTime, m_unNum, m_unCost, m_unExp, m_unNeedRank,
// s32 m_nNpcAct, b8 m_bIsHide, m_CraftMaterialList}: same widths and order, Season 3 material (V).
struct CDataMDataCraftRecipe {
    u32 RecipeID;
    u32 ItemID;
    u32 Time;
    u32 Num;
    u32 Cost;
    u32 Exp;
    u32 NeedRank;
    s32 NpcAct;
    bool IsHide;
    MtTypedArray<CDataMDataCraftMaterial> CraftMaterialList;
};
