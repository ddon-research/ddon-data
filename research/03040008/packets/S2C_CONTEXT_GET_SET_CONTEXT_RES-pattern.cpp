// 35.7.2 S2C_CONTEXT_GET_SET_CONTEXT_RES (client 03040008).
// Body: s32 Error [, s32 Result]. P4 2.3 (PC handler 0x7cfb10, reader 0x805340).
// packet-id: 35.7.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_GET_SET_CONTEXT_RES : CPacket {
    ResHeader res;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONTEXT_GET_SET_CONTEXT_RES packet @ 0x00;
