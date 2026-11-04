// 11.88.16 S2C_QUEST_11_88_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.88.16.
// 006 T005 § 32. PC handler 0x7f15e0 is `return 1;`: it reads nothing (V). No name string, no lead
// structure: the raw name stays (meaning open). PS4 counterpart: not settled.
// Walk: 20/20 fit, slack 7.
// Body: none.
// packet-id: 11.88.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_QUEST_11_88_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_11_88_16_NTC packet @ 0x00;
