// 65.3.1 C2S_EQUIP_ENHANCED_GET_PACKS_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 65.3.1.
// PC writer 0x827e40: WritePacket(0x41, 3, 1), Write_u8 (V). Name: CLI/server (G (lead)).
// PS4 counterpart: none (Season 3 group).
// Walk: 2/2 fit, slack 6.
// Body: u8.
// packet-id: 65.3.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_EQUIP_ENHANCED_GET_PACKS_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 EnhanceType;     // T005 G (lead): server EnhanceType; 3 in 2/2
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_EQUIP_ENHANCED_GET_PACKS_REQ packet @ 0x00;
