// 10.9.1 C2S_ITEM_GET_ITEM_STORAGE_INFO_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.6.
// PC writer 0x82ce40 (10, 9, 1): list 0x77f970 {u8} (V). PS4
// CPacket_C2S_GET_ITEM_STORAGE_INFO_REQ::WritePacket 0x1a324e0:
// MtTypedArray<CDataGameItemStorage> m_GameItemStorageList (V). Walk: 4/4 fit, slack 2.
// Body: list CDataGameItemStorage (4 + n bytes).
// packet-id: 10.9.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct C2S_ITEM_GET_ITEM_STORAGE_INFO_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataGameItemStorage> GameItemStorageList;   // PC 0x77f970
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ITEM_GET_ITEM_STORAGE_INFO_REQ packet @ 0x00;
