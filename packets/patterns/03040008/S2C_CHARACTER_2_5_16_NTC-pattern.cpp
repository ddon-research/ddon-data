// 2.5.16 S2C_CHARACTER_2_5_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 2.5.16.
// PC handler 0x7c7770 (no OnPacket_ string): Read_u8, passed to sItemManager 0xb9f450 (V). Packet name:
// the CLI/server name (purpose open).
// PS4 counterpart: none matched (spec 006 T009 § 3).
// Walk: 2/2 fit, slack 6.
// Body: u8.
// packet-id: 2.5.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CHARACTER_2_5_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T005 open (role V: first argument of sItemManager 0xb9f450), kept unk: 10 in 2/2; server: Unk0 (lead)
    u8 unk_u8;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_2_5_16_NTC packet @ 0x00;
