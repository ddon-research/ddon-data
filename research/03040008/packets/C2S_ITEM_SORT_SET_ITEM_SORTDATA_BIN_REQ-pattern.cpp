// 50.1.1 C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 4.3.
// PC writer 0x841860 (50, 1, 1): u8, 0x780fe0 (1024 x Write_u8), bool (V). PS4
// CPacket_C2S_SET_ITEM_SORTDATA_BIN_REQ::WritePacket 0x1a325f0: CDataItemSort m_SortData only.
// Season 3 adds the trailing bool (V code; the PS4 body fits 59/59 inside the slack, so the bool
// is code-only; it reads 1 in 59/59). Walk: 59/59 fit, slack 5.
// Body: CDataItemSort SortData, bool unk_bool (1026 bytes).
// packet-id: 50.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataItemSort SortData;
    bool unk_bool;                                         // Season 3, new
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ packet @ 0x00;
