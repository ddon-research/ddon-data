// 63.0.16 S2C_63_0_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 63.0.16.
// PC handler 0x7d1ae0 (no OnPacket_ string): Read_u32, then 0xb60860 on the game object without the
// value (V). Packet name: the CLI/server name (purpose open).
// PS4 counterpart: none (Season 3 group).
// Walk: 1/1 fit, slack 3.
// Body: u32.
// packet-id: 63.0.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_63_0_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 unk_u32;        // T005 open (the handler does not use it): 1 in 1/1; server: Unk0 (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_63_0_16_NTC packet @ 0x00;
