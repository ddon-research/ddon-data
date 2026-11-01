// 35.11.16 S2C_CONTEXT_SET_CONTEXT_BASE_NTC (client 03040008).
// Body: CDataContextSetBase. P4 2.3 (PC handler 0x7cfee0, reader 0x760400).
// packet-id: 35.11.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_SET_CONTEXT_BASE_NTC : CPacket {
    CDataContextSetBase m_Base;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONTEXT_SET_CONTEXT_BASE_NTC packet @ 0x00;
