// 2.15.16 C2S_CHARACTER_CHARACTER_DEAD_NTC (client 03040008).
// Body: empty. P4 4 (PC call site 0x820b53 (not a defined function: empty body inferred from captures and PS4)).
// packet-id: 2.15.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CHARACTER_CHARACTER_DEAD_NTC : CPacket {
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_CHARACTER_DEAD_NTC packet @ 0x00;
