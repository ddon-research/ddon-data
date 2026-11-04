// 50.0.2 S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 4.1.
// PC handler 0x7ddb80 and reader 0x80ca00 (both read linearly): RES header, list 0x75e6e0
// (CDataItemSort) (V). PS4 OnPacket_S2C_GET_ITEM_SORTDATA_BIN_RES 0x333210:
// MtTypedArray<CDataItemSort> m_SortData (V). Walk: 46/46 fit, slack 11; the list is never
// non-empty (the data arrives in 50.0.16, same element reader).
// Body: s32 Error [, s32 Result, list CDataItemSort] (12 + 1025n bytes).
// packet-id: 50.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataItemSort> SortData;                  // PC 0x75e6e0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_RES packet @ 0x00;
