// 34.0.1 C2S_ENTRY_BOARD_ENTRY_BOARD_LIST_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 34.0.1.
// PC writer 0x827580: WritePacket(0x22, 0, 1), list writer 0x77dff0: Write_u32 count, Write_u64 per
// element (V; corrects 008 T001's plain `{4 8}`: the u32 is the count). Name: CLI/server (G (lead)).
// PS4 counterpart: none matched (spec 006 T013 § 5).
// Walk: 1/1 fit, slack 11.
// Body: list CDataCommonU64.
// packet-id: 34.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_ENTRY_BOARD_ENTRY_BOARD_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T005 V (writer 0x77dff0); name I (value: 34.0.2 returns the id as BoardId, 1/1; lead agrees:
    // server BoardIdList)
    MtTypedArray<CDataCommonU64> BoardIdList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ENTRY_BOARD_ENTRY_BOARD_LIST_REQ packet @ 0x00;
