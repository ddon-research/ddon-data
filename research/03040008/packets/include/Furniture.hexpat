// Furniture CData of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source: specs/006-packet-pattern-coverage/research/T010-gp-clan.md sections 1.2 and 25. Moved
// here in T010b from the 52.1.2 pattern (its only earlier user) so that the clan patterns share it.
// Users: 52.1.2 S2C_MY_ROOM_FURNITURE_LIST_GET_RES, 31.31.2 through Clan.hexpat.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataFurnitureLayout: PC list reader 0x766f90 {u32, u32, u8} (V). Read by the PC
// MY_ROOM_FURNITURE_LIST_GET_RES reader 0x80fa00 where PS4 CPacket_S2C_FURNITURE_LIST_GET_RES::
// ReadPacket 0x19df920 reads Read_CDataFurnitureLayout_ 0x19e8890 {u32 m_unItemID, u32 m_unOmID,
// u8 m_ucLayoutID}; names V by that identity (T010 1.2).
struct CDataFurnitureLayout {
    u32 ItemID;
    u32 OmID;
    u8 LayoutID;
};
