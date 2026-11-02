// 34.2.2 S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 6 (1 and 16 for the types).
// PC handler 0x7d2bd0 -> reader 0x806c50: header, u64, element 0x765420 (one CDataEntryItem) (V).
// PS4 0x3220d0 {u64 m_ullBoardID, CEntryItem m_EntryItem} (read inline): match V; the PS4 body fails 1/1.
// Walk: 1/1 fit.
// Body: s32 Error [, s32 Result, u64 BoardID, CDataEntryItem EntryItem].
// packet-id: 34.2.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "EntryBoard.hexpat"

struct S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u64 BoardID;
        CDataEntryItem EntryItem;   // PC 0x765420
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES packet @ 0x00;
