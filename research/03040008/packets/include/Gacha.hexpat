// Gacha CData structures of client 03040008 (PC, Season 3) shared by the group 39 GACHA patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T012-achievement-equip-skill.md sections 1, 16 and 19. "PC 0x..." is the reader VA in the PC
// 03040008 database (image base 0x400000); "PS4" names the PS4 02020005 reader and DWARF type, whose
// member names the fields carry (m_ and type prefix dropped) unless marked. The recompilation's
// PacketData/Gacha.h declares the same members. Marks: V = read in IDA, I = inferred.
// Distinct from the box gacha types of the 57.0.2 pattern (CDataBoxGacha*).
// Includes Packet.hexpat only. Users: 39.0.2, 39.1.2.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataGachaItemInfo: PC list reader 0x7685e0 {u32 x4, f64} (V); PS4 0x19ef190 {u32 m_unItemId,
// m_unItemNum, m_unRank, m_unEffect, f64 m_dProbability}: same (V).
struct CDataGachaItemInfo {
    u32 ItemId;
    u32 ItemNum;
    u32 Rank;
    u32 Effect;
    double Probability;
};

// CDataGachaSettlementInfo: PC list reader 0x768720, element 0x768830 {u32 x9} (V width); PS4
// 0x19efae0/0x19effe0 has the first eight members. Season 3 adds a trailing u32 (0 in all 520
// captured settlements; no code use traced): the PS4 settlement fails 26/26 39.0.2 captures.
struct CDataGachaSettlementInfo {
    u32 DrawGroupId;
    u32 Id;
    u32 Price;
    u32 BasePrice;
    u32 PurchaseNum;
    u32 PurchaseMaxNum;
    u32 SpecialPriceNum;
    u32 SpecialPriceMaxNum;
    // T014b V (flow); I (name): PC 0xd9fef0 (gacha UI, packet getter 0x86c250, conn sub +0x460)
    // passes settlement +36 as arg 5 of 0xda2f00, which stores it in the price slot (+128/+140)
    // (...)
    u32 ChargeId;                                   // Season 3
};

// CDataGachaDrawInfo: PC list reader 0x768310 {u32, bool, list 0x7685e0} (V); PS4 0x19efcf0 {u32
// m_unNum, b8 m_bIsBonus, list CDataGachaItemInfo}: same (V).
struct CDataGachaDrawInfo {
    u32 Num;
    bool IsBonus;
    MtTypedArray<CDataGachaItemInfo> GachaItemInfo;
};

// CDataGachaDrawGroupInfo: PC list reader 0x7681e0 {list 0x768720, list 0x768310} (V); PS4 0x19ef860
// {m_GachaSettlementList, m_GachaDrawList}: same, with the Season 3 settlement.
struct CDataGachaDrawGroupInfo {
    MtTypedArray<CDataGachaSettlementInfo> GachaSettlementList;
    MtTypedArray<CDataGachaDrawInfo> GachaDrawList;
};

// CDataGachaInfo: PC list reader 0x768430 (loc), element 0x7684f0 (V); PS4 0x19ef760 {u32 m_unId,
// s64 m_llBegin, s64 m_llEnd, MtString m_wstrName, m_wstrDescription, m_wstrDetail, u8
// m_ucWeightDispType, MtString m_wstrWeightDispTitle, m_wstrWeightDispText, m_wstrListAddr,
// m_wstrImageAddr, m_DrawGroups}: same, with the Season 3 settlement (V).
struct CDataGachaInfo {
    u32 Id;
    s64 Begin;
    s64 End;
    MtString Name;
    MtString Description;
    MtString Detail;
    u8 WeightDispType;
    MtString WeightDispTitle;
    MtString WeightDispText;
    MtString ListAddr;
    MtString ImageAddr;
    MtTypedArray<CDataGachaDrawGroupInfo> DrawGroups;
};
