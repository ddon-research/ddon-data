// 13.16.1 C2S_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 13.16.1.
// PC writer 0x82c70d: WritePacket(0x0d, 16, 1), Write_u32 (V). Name: CLI/server (G (lead)).
// PS4 counterpart: none matched (spec 006 T004 § 10).
// Walk: 1/1 fit, slack 3.
// Body: u32.
// packet-id: 13.16.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 unk_u32;        // T005 open: 2 in 1/1; server: Unk0 (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_REQ packet @ 0x00;
