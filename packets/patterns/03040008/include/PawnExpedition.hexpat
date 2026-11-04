// Group 58 PAWN_EXPEDITION CData of client 03040008 (PC, Season 3), shared by the pawn expedition
// packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// sections 4 and 6. "PC 0x..." is the reader or writer VA in the PC 03040008 database (image base
// 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the fields carry (m_ and
// type prefix dropped). Marks: V = read in IDA, I = inferred.
// Group 58 reuses CDataCommonU32/CDataCommonU8 (Packet.hexpat) and CDataGatheringItemElement/
// CDataGatheringItemGetRequest (Instance.hexpat): patterns include those files themselves.
// Includes Packet.hexpat only; nothing includes this file (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataAreaSpotSet: PC list reader 0x7594b0 element and reader 0x7595a0 {u32, u32} (V); PS4
// CDataAreaSpotSet {u32 m_unAreaId, u32 m_unSpotId} (V). Users: 58.0.2, 58.5.2.
struct CDataAreaSpotSet {
    u32 AreaId;
    u32 SpotId;
};

// CDataPawnExpeditionClanSallySpotInfo: PC list reader 0x771d70 element {u32, u32, u32} (V); PS4
// {u32 m_unAreaID, u32 m_unSpotID, u32 m_unSallyNum} (V). Never non-empty in the captures:
// code-only. User: 58.0.2.
struct CDataPawnExpeditionClanSallySpotInfo {
    u32 AreaID;
    u32 SpotID;
    u32 SallyNum;
};

// CDataBattleResultInfo: element of PC list reader 0x759f80 (not a function in the database; read
// linearly: u32 count, then Read_u32 x3 per element) (V); PS4 CBattleResultInfo {u32 m_unEnemyId,
// u32 m_unEnemyNum, u32 m_unEnemyLevel} (V). PS4 reads one; Season 3 reads a list. User: 58.5.2.
struct CDataBattleResultInfo {
    u32 EnemyId;
    u32 EnemyNum;
    u32 EnemyLevel;
};
