// Group 23 AREA CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11a-old-patterns.md
// section 15 and the shared-structure table; P11b-old-patterns.md extends it (23.11.2 reads the
// same two Season 3 lists). "PC 0x..." is the reader VA in the PC 03040008 database (image base
// 0x400000); "PS4" names the PS4 02020005 DWARF type. Marks: V = read in IDA, I = inferred.
// `unk_*` = Season 3 field without a PS4 counterpart; its name is open. Server C# names are leads
// only and appear only as "server: <name>".
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataReleaseAreaInfoSet: PC list reader 0x776890 {u32, list CDataCommonU32 (0x75e8e0)} (V);
// PS4 CDataReleaseAreaInfoSet {u32 m_unAreaID, MtTypedArray<CDataCommonU32> m_ReleaseList}.
struct CDataReleaseAreaInfoSet {
    u32 AreaID;
    MtTypedArray<CDataCommonU32> ReleaseList;
};

// Season 3 list element {u32, u32, s64}: PC list reader 0x7696e0 (V), no PS4 type. Users: 23.8.2
// list 2, 23.11.2 list 2 (P11b). Server lead: MonsterGatheringSpots.
struct CDataAreaUnkU32U32S64 {
    u32 unk_u32_0;
    u32 unk_u32_1;
    s64 unk_s64;
};

// Season 3 list element {u32, bool, s64}: PC list reader 0x76d440 (V), no PS4 type. Users: 23.8.2
// list 3, 23.11.2 list 3 (P11b). Server lead: PeriodicallyReleasedSpots.
struct CDataAreaUnkU32BoolS64 {
    u32 unk_u32;
    bool unk_bool;
    s64 unk_s64;
};
