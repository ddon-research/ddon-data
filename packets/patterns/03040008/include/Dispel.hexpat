// Dispel CData of client 03040008 (PC, Season 3) shared by the packet patterns of group 51 DISPEL.
//
// Source: specs/006-packet-pattern-coverage/research/T013-small-groups.md sections 1, 10 and 16
// (T013b). Users: 51.2.2. The 51.0.2 pattern keeps its own CDataDispel* item types (unchanged).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataDispelCategoryInfo (Season 3): PC list reader 0x763390 {u32, MtString} (V); PS4 0x19eaf30
// {u8 m_ucCategory, MtString m_wstrCategoryName}: Season 3 widens Category to u32 (the PS4 element
// fails 1/1, T013 10). Category values 152-156 = the 51.0.1 Category. server: CDataDispelItemCategoryInfo
// (lead, u32 Category).
struct CDataDispelCategoryInfo {
    u32 Category;
    MtString CategoryName;
};
