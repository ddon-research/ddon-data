// Pawn CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11b-old-patterns.md
// section 14 and the shared-structure table. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type. CDataPawnListData and
// CDataPawnCraftSkill also match the PS4 recompilation (PacketData/Pawn.h); CDataRegisterdPawnList
// has no class there. Marks: V = read in IDA, I = inferred.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

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
