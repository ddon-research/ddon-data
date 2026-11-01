// 13.44.16 C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC (client 03040008).
// Body: one u32. P4 4, P5 7 (PC writer 0x82c2b0; sent for a bad-status condition (c & 0xF000) == 0x1000
// of a non-player character). The client name is unresolved (P5 7); the raw-file name is the
// server's. The value looks like a status id (captures: 0x1004, I).
// packet-id: 13.44.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC : CPacket {
    u32 unk_u32;  // status id (inferred)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC packet @ 0x00;
