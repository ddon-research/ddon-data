// Item CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11b-old-patterns.md
// section 13 and the shared-structure table. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type; the member order also
// matches the PS4 recompilation (PacketData/Item.h). Marks: V = read in IDA, I = inferred.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataGameItemStorage: PS4 CDataGameItemStorage {u8 m_ucStorageType}; read inline by PC 0x7688e0.
struct CDataGameItemStorage {
    u8 StorageType;
};

// CDataGameItemStorageInfo: PC list reader 0x7688e0 (mid-function) {u8, u16, u16} (P11b 13, V);
// PS4 CDataGameItemStorageInfo {CDataGameItemStorage, u16 m_usUsedSlotNum, u16 m_usMaxSlotNum}.
struct CDataGameItemStorageInfo {
    CDataGameItemStorage GameItemStorage;
    u16 UsedSlotNum;
    u16 MaxSlotNum;
};
