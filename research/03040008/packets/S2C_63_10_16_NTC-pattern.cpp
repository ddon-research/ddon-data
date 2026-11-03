// 63.10.16 S2C_63_10_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 63.10.16.
// PC handler 0x7d1e60 (no OnPacket_ string), reader 0x8066b0: Read_u32, Read_MtString, Read_u8 (V); the
// handler then announces a fixed message (dword_1bd4204), not the packet values. Packet name: the
// CLI/server name (purpose open).
// PS4 counterpart: none (Season 3 group).
// Walk: 12/12 fit, slack 0.
// Body: u32, MtString, u8.
// packet-id: 63.10.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_63_10_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 unk_u32;        // T005 open: 1, 6, 9, 10; server: Unk0 (lead)
    MtString unk_str;   // T005 open: empty in 12/12; server: Unk1String (lead)
    u8 unk_u8;          // T005 open: 1, 2; server: Unk2 (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_63_10_16_NTC packet @ 0x00;
