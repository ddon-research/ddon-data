// 2.14.16 C2S_CHARACTER_CHARACTER_DOWN_CANCEL_NTC (client 03040008).
// Body: empty. P4 4 (PC writer 0x820ba0; PS4 Send_C2S_CHARACTER_DOWN_CANCEL_NOTICE).
// packet-id: 2.14.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CHARACTER_CHARACTER_DOWN_CANCEL_NTC : CPacket {
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_CHARACTER_DOWN_CANCEL_NTC packet @ 0x00;
