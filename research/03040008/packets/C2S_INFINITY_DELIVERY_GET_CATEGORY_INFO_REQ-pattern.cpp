// 59.9.1 C2S_INFINITY_DELIVERY_GET_CATEGORY_INFO_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 59.9.1.
// PC writer 0x82a880 (sub_): WritePacket(0x3b, 9, 1), Write_u32 (V; 008 T001). Packet name G (lead),
// the request of the V-named 59.9.2. No server structure (lead: PacketId only). PS4 counterpart: none (Season 3 group).
// Walk: 1/1 fit, slack 3.
// Body: u32.
// packet-id: 59.9.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_INFINITY_DELIVERY_GET_CATEGORY_INFO_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 CategoryId;     // T004 I (value: 61 = the CategoryId of the preceding 59.8.2, 1/1)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INFINITY_DELIVERY_GET_CATEGORY_INFO_REQ packet @ 0x00;
