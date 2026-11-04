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
    // T014b V (consumer); I (name): PC 0xd40fd0 finds the element whose +4 equals
    // CDataSpotInfo.SpotID (spot list element +4) and takes +8; PC 0xbfe8e0 builds +4*1000 + +8
    // (0x5df870, both > 0) and registers it in sSetManager (0xbf8250, type 1) (...)
    u32 SpotId;
    // T014b I (consumer): PC 0xd40fd0 stores it per spot (UI object +60); PC 0xbfe8e0 uses it as
    // the low part of SpotId*1000 + x for sSetManager 0xbf8250 type 1; no PS4 counterpart, no name
    u32 unk_u32_1;
    // T014b open (value only), kept unk: no consumer found (0xbfe8e0, 0xd40fd0) reads element +16;
    // epoch seconds by value
    s64 unk_s64;
};

// Season 3 list element {u32, bool, s64}: PC list reader 0x76d440 (V), no PS4 type. Users: 23.8.2
// list 3, 23.11.2 list 3 (P11b). Server lead: PeriodicallyReleasedSpots.
struct CDataAreaUnkU32BoolS64 {
    // T014b V (consumer); I (name): PC 0xd40fd0 compares +4 with the spot id (CDataSpotInfo.SpotID)
    // and 0x9784f0 with a set unit id (+0x1b8), returning +8; values 1068..1080
    u32 SpotId;
    // T014b I (consumer): PC 0x9784f0 returns +8 for the spot; callers 0x98e990, 0x9927e0, 0xf185f0
    // branch on it; 0xd40fd0 stores it per spot; no code name
    bool unk_bool;
    // T014b open (value only), kept unk: no consumer found reads element +16; epoch seconds by
    // value
    s64 unk_s64;
};

// CDataSpotEnemyInfo: PC sublist reader loc_779c00 {u32, u8} (P11b 11, V); PS4 CDataSpotEnemyInfo
// {u32 m_unEnemyID, u8 m_ucEnemyLv}.
struct CDataSpotEnemyInfo {
    u32 EnemyID;
    u8 EnemyLv;
};

// CDataSpotItemInfo: PC sublist reader 0x779e50 {u32, u8} (P11b 11, V); PS4 CDataSpotItemInfo
// {u32 m_unItemId, u8 m_ucPawnTakeRate}.
struct CDataSpotItemInfo {
    u32 ItemId;
    u8 PawnTakeRate;
};

// CDataSpotInfo: PC list reader 0x779cf0, element 0x779db0 (P11b 11, V); PS4 CDataSpotInfo, same
// order (PS4 OnPacket_S2C_GET_SPOT_INFO_LIST_RES 0x303540; PS4 recompilation
// PacketData/AreaMaster.h). User: 23.11.2.
struct CDataSpotInfo {
    u32 SpotID;
    u32 TextIndex;
    u32 StageID;
    bool IsRelease;
    bool IsNew;
    MtTypedArray<CDataSpotEnemyInfo> SpotEnemyInfoList;
    MtTypedArray<CDataSpotItemInfo> SpotItemInfoList;
    u32 QuickPartyPopularity;
};

// CDataRewardItemInfo: PC list reader 0x7773b0 {u32, u32, u8} (P11b 10, V); PS4
// CDataRewardItemInfo {u32 m_unIndex, u32 m_ulItemId, u8 m_ucNum}. User: 23.3.2.
struct CDataRewardItemInfo {
    u32 Index;
    u32 ItemId;
    u8 Num;
};

// CDataSelectItemInfo: PC list writer 0x780ea0 {u32, u8} (P11b 9, V); PS4 CDataSelectItemInfo
// (CPacket_C2S_GET_AREA_SUPPLY_REQ::WritePacket 0x1a34990; no class in the PS4 recompilation).
// User: 23.4.1.
struct CDataSelectItemInfo {
    u32 Index;
    u8 Num;
};
