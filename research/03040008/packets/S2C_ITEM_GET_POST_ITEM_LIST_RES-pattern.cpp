// 10.6.2 S2C_ITEM_GET_POST_ITEM_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.4 (1.1 for the type).
// PC handler 0x7dd270, reader 0x80c5b0: identical to 10.3.2's (RES header, list 0x76abe0) (V).
// PS4 OnPacket_S2C_GET_POST_ITEM_LIST_RES 0x2e9850: m_ItemList (V; the PS4 element fails 3/3).
// Walk: 3/3 fit, slack 11-14, up to 190 items; the element lists are always empty here.
// Body: s32 Error [, s32 Result, list CDataItemList] (variable).
// packet-id: 10.6.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct S2C_ITEM_GET_POST_ITEM_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataItemList> ItemList;                  // PC 0x76abe0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_GET_POST_ITEM_LIST_RES packet @ 0x00;
