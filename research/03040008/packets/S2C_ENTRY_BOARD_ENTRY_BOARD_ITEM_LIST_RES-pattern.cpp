// 34.1.2 S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 6 (1 and 16 for the types).
// PC handler 0x7d3880 -> reader 0x8072a0: header, u64, list 0x765360 (CDataEntryItem, Season 3) (V).
// PS4 OnPacket_S2C_ENTRY_BOARD_ITEM_LIST_RES 0x321f30 {u64 m_ullID, m_EntryItemList}: match V. The PS4
// element fails 1/3 (the two others hold empty lists).
// Walk: 3/3 fit; one capture holds 8 members.
// Body: s32 Error [, s32 Result, u64 ID, list CDataEntryItem].
// packet-id: 34.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "EntryBoard.hexpat"

struct S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u64 ID;
        MtTypedArray<CDataEntryItem> EntryItemList;   // PC 0x765360
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES packet @ 0x00;
