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
    // T014b V (role); I (name): PC 0xe03c80 (craft progress UI, packet getter 0x86c670 =
    // conn+0x320, handler 0x7d0b60): after the support pawns (+20 list) it prints the name of each
    // element +4 of this list (+40 count, +52 data) via 0xb79e30 (pawn id -> name), (...)
    MtTypedArray<CDataCommonU32> LegendPawnIdList;   // Season 3, PC 0x75e8e0; server: CraftMasterLegendPawnInfoList as CDataCraftPawnInfo (lead, contradicted by the PC reader)
    u32 RecipeID;
    u32 Exp;
    s32 NpcActionID;
    u32 ItemID;         // I: position
    u32 ToppingID;      // I: position
    // T014b open (passed, not read), kept unk: PC 0xe03c80 passes element +76 as the last argument
    // of 0xdfe5c0, which does not use it (Hex-Rays); no other of the 27 getter 0x86c670 callers
    // reads word +76
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
    // T014b open (no reader), kept unk: element +4: not copied by 0x87f610 (copies +16, +20, +24,
    // skill list); none of the 22 callers of the packet getter 0x86a2c0 (nor the undefined caller
    // 0x53243f) reads element +4 or +8 except +8 in 0xb397e0
    u32 unk_u32_0;
    // T014b V (role); I (name): PC 0xb397e0 sums element +12 * create count (cCraftPawnCtrl +108)
    // only when +8 == 5 (...)
    u8 WalletType;
    // T014b V (role); I (name): PC 0xb37d10 returns element +12 for kind 3; 0xe02a20 multiplies it
    // by the create count and compares with the owned amount of wallet 5; 0xb397e0 sums +12 *
    // create count over the craft slots (fee per craft)
    u32 Price;
    // T014b V: PC 0x87f610 (handler 0x7d0bf0, packet kept at conn+0x32C, getter 0x86a2c0) copies
    // element +16 to the pawn entry +4 (PawnId slot: 0x881310 fills it from CDataPawnList.PawnId)
    // (...)
    u32 PawnId;
    // T014b V: PC 0x87f610 copies element +20 (MtString) to the pawn entry +12 (name slot, 0x881310
    // fills it from CDataPawnList name); 0xb39960 / 0xb39a60 return it as the pawn name
    MtString PawnName;
    // T014b V (role); I (name): PC 0xb39c40 switch on pawn kind: 1 own pawns -> pawn entry +52, 2
    // second list -> +52, 3 these pawns -> element +24. PS4 sCraftManager::getPawnRank 0x761ac0
    // returns the same pawn entry member (+64 on PS4) for its two lists (...)
    u32 CraftRank;
    MtTypedArray<CDataPawnCraftSkill> unk_SkillList;
};

// CDataCraftSettingUnkElement (struct name I): PC list reader 0x760db0, element 0x760ea0 {u32 x5,
// bool} (V); no PS4 counterpart (Season 3 tail of 30.13.2). server: CDataRefiningMaterialInfo (lead).
struct CDataCraftSettingUnkElement {
    // T014b V: PC 0xb3d310 finds the element whose +4 equals the item id it passes to the
    // item-param lookup 0xb98c80; 0xb3aca0 / 0xb3ad60 match +4 with the id of the item found by UID
    // (0xb3a9a0)
    u32 ItemId;
    // T014b V (role): PC 0xb3aca0: result = +8 * itemParam vfunc+80 (u16), capped at +12 (rate of
    // the first quantity); name open
    u32 unk_u32_1;
    // T014b V (role): PC 0xb3aca0: cap of +8 * itemParam vfunc+80 (maximum of the first quantity);
    // name open
    u32 unk_u32_2;
    // T014b V (role): PC 0xb3ad60: result = +16 * itemParam vfunc+80, capped at +20 (rate of the
    // second quantity); name open
    u32 unk_u32_3;
    // T014b V (role): PC 0xb3ad60: cap of the second quantity; name open
    u32 unk_u32_4;
    // T014b V (role): PC 0xb3d310 (caller 0xdff970): when the item is at the table's level cap (+14
    // of 0x48be30 entry) it is accepted only if listed here and +24 != 0 (allows the item past its
    // cap); name open
    bool unk_bool;
};

// CDataMDataCraftMaterial (Season 3): PC list reader 0x76dee0 {u32, u32, u32, bool} (V); PS4
// 0x19e72a0 {u32 m_unItemID, m_unNum, m_unSortNo}: Season 3 adds the bool (the PS4 material fails
// 3/3 54.0.2 captures, T013 14). server: IsSp (lead).
struct CDataMDataCraftMaterial {
    u32 ItemID;
    u32 Num;
    u32 SortNo;
    // T014b open (not read), kept unk: PC CRAFT_RECIPE_GET_CRAFT_RECIPE_RES handler 0x7d0eb0 ->
    // 0xb41130 -> 0xb3ff00: the material list (recipe +40) is sorted by +12 SortNo (comparator
    // 0xb414c0) and only +4 ItemId and +8 Num are copied; +16 is not read
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
