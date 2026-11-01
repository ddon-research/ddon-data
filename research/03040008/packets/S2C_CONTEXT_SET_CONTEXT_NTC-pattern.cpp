// 35.13.16 S2C_CONTEXT_SET_CONTEXT_NTC (client 03040008).
// Body: CDataContextSetBase, CDataContextSetAdditional. P4 2.3 (PC handler 0x7cffe0, reader
// 0x805460).
// packet-id: 35.13.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_SET_CONTEXT_NTC : CPacket {
    ContextSetInfo m_SetInfo;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONTEXT_SET_CONTEXT_NTC packet @ 0x00;
