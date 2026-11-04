// 10.7.1 C2S_ITEM_MOVE_ITEM_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.5.
// PC writer 0x82d270 (10, 7, 1): u8, list 0x780090 (CDataMoveItemUIDFromTo) (V). PS4
// CPacket_C2S_MOVE_ITEM_REQ::WritePacket 0x1a37b30: u8 in_SourceGameStorageType, m_ItemUIDList
// (same, V). Walk: 6/6 fit, slack 0.
// Body: u8 SourceGameStorageType, list CDataMoveItemUIDFromTo (variable).
// packet-id: 10.7.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct C2S_ITEM_MOVE_ITEM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 SourceGameStorageType;
    MtTypedArray<CDataMoveItemUIDFromTo> ItemUIDList;      // PC 0x780090
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ITEM_MOVE_ITEM_REQ packet @ 0x00;
