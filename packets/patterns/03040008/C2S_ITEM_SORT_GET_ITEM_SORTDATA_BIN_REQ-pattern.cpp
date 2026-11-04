// 50.0.1 C2S_ITEM_SORT_GET_ITEM_SORTDATA_BIN_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 4.1.
// PC writer 0x82d550 (50, 0, 1): list 0x77df90 {u32} (V). PS4
// CPacket_C2S_GET_ITEM_SORTDATA_BIN_REQ::WritePacket 0x1a32690: MtTypedArray<CDataCommonU32>
// m_SortList (V). Walk: 46/46 fit, slack 7-15, up to 7 entries.
// Body: list CDataCommonU32 (4 + 4n bytes).
// packet-id: 50.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_ITEM_SORT_GET_ITEM_SORTDATA_BIN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataCommonU32> SortList;                 // PC 0x77df90
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ITEM_SORT_GET_ITEM_SORTDATA_BIN_REQ packet @ 0x00;
