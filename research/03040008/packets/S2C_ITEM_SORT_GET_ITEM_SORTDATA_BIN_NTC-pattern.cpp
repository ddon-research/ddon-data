// 50.0.16 S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 50.0.16.
// PC handler 0x7ddab0 (no OnPacket_ string; name G (lead)): nPacket::Read_CDataItemSort_ 0x75e6e0 (V),
// the reader of 50.0.2's list (Item.hexpat CDataItemSort {u8, u8[0x400]}).
// PS4 counterpart: see spec 006 T008 § 4 (50.0.2's PS4 type, same element).
// Walk: 48/48 fit, slack 2-14; 0, 1 or 5 entries (storage types 1, 2, 3, 6, 7), every bin all zero.
// Body: list CDataItemSort.
// packet-id: 50.0.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Context.hexpat"
#include "Item.hexpat"

struct S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T005 I (same structure: the same reader 0x75e6e0 as 50.0.2's SortData); name G (lead: server SortData)
    MtTypedArray<CDataItemSort> SortData;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC packet @ 0x00;
