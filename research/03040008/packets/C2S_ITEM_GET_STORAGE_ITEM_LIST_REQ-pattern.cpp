// 10.3.1 C2S_ITEM_GET_STORAGE_ITEM_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.3.
// PC writer 0x82d0d0 (10, 3, 1): list 0x77e050 {u8} (V). PS4
// CPacket_C2S_GET_STORAGE_ITEM_LIST_REQ::WritePacket 0x1a37da0: MtTypedArray<CDataCommonU8>
// m_StorageList (V). Walk: 136/136 fit, slack 2-10, up to 9 storage types.
// Body: list CDataCommonU8 (4 + n bytes).
// packet-id: 10.3.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_ITEM_GET_STORAGE_ITEM_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataCommonU8> StorageList;               // PC 0x77e050
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ITEM_GET_STORAGE_ITEM_LIST_REQ packet @ 0x00;
