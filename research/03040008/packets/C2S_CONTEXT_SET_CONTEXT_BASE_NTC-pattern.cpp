// 35.8.16 C2S_CONTEXT_SET_CONTEXT_BASE_NTC (client 03040008).
// Body: CDataContextSetBase. P4 2.3, P5 7 (PC writer 0x824ba0, called from 0x87c3e0 on the
// non-additional branch). Client name by caller code match: C2S_SET_CONTEXT_BASE_NOTICE. The
// server has no PacketId for 35.8.16, so no raw file carries a name: this file name follows
// 35.9.16's. No capture: not validated on data.
// packet-id: 35.8.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct C2S_CONTEXT_SET_CONTEXT_BASE_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataContextSetBase m_Base;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONTEXT_SET_CONTEXT_BASE_NTC packet @ 0x00;
