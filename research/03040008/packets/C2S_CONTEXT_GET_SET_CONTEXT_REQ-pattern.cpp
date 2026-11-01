// 35.7.1 C2S_CONTEXT_GET_SET_CONTEXT_REQ (client 03040008).
// Body: CDataContextSetBase. P4 2.3 (PC writer 0x8249e0).
// packet-id: 35.7.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct C2S_CONTEXT_GET_SET_CONTEXT_REQ : CPacket {
    CDataContextSetBase m_Base;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONTEXT_GET_SET_CONTEXT_REQ packet @ 0x00;
