// 35.7.2 S2C_CONTEXT_GET_SET_CONTEXT_RES (client 03040008).
// Body: s32 Error [, s32 Result]. P4 2.3 (PC handler 0x7cfb10, reader 0x805340).
// packet-id: 35.7.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_GET_SET_CONTEXT_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // RES convention (spec 005 R2 F3): Error inline, Result only when Error == 0.
    s32 Error;
    if (Error == 0) {
        s32 Result;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONTEXT_GET_SET_CONTEXT_RES packet @ 0x00;
