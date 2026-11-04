// Group 14 WARP CData of client 03040008 (PC, Season 3), shared by the warp packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/T008-warp-item.md
// sections 1.2 and 6. "PC 0x..." is the reader VA in the PC 03040008 database (image base
// 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the fields carry (m_ and
// type prefix dropped). Marks: V = read in IDA. None of these types changed in Season 3.
// Includes nothing but Packet.hexpat (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataWarpPoint: PC list reader 0x77c870 element {u32, u32} (V); PS4 {u32 m_ulID, u32
// m_ulRimPrice} (V).
struct CDataWarpPoint {
    u32 ID;
    u32 RimPrice;
};

// CDataFavoriteWarpPoint: PC list reader 0x766af0 (read linearly: three Read_u32 per element)
// {u32, u32, u32} (V); PS4 {u32 m_ulSlotNo, u32 m_ulWarpPointID, u32 m_unPrice} (V).
struct CDataFavoriteWarpPoint {
    u32 SlotNo;
    u32 WarpPointID;
    u32 Price;
};

// CDataAreaWarpPoint: PC list reader 0x7595e0 element {u32, u32, u32} (V); PS4 {u32 m_unAreaID,
// u32 m_unWarpPointID, u32 m_unPrice} (V).
struct CDataAreaWarpPoint {
    u32 AreaID;
    u32 WarpPointID;
    u32 Price;
};

// CDataJumpLocation: PC reader 0x76c9e0 {u32, u32} (V); PS4 CJumpLocation {u32 m_ulStageId, u32
// m_unStartPos} (V).
struct CDataJumpLocation {
    u32 StageId;
    u32 StartPos;
};
