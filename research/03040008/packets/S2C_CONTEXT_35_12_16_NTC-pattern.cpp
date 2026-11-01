// 35.12.16 S2C_CONTEXT_35_12_16_NTC (client 03040008).
// Body: CDataContextSetBase, then the 200-byte structure read by PC 0x760480. P4 2.3, P5 7
// (handler 0x7d0060, reader 0x8054d0; name unresolved). Decoded up to the second list; the
// element of the list read by 0x76fc20 and the count of 0x757e60 were not read (P4 5), so the
// rest stays bytes (TODO) and `decoded` is false. No capture: not validated on data.
// packet-id: 35.12.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_35_12_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataContextSetBase m_Base;
    u64 unk_u64_a[10];
    u64 unk_u64_b[5];
    u32 ocdCount;
    CDataOcdActive unk_OcdList[ocdCount];  // PC 0x76fb30
    // TODO: list read by PC 0x76fc20 (element not decompiled), then u32, u32, u16, u16, u16,
    // u8, u32 x n (PC 0x757e60, count source not read).
    bool decoded = false [[export]];
    u8 unparsed[std::mem::size() - $];
    bool fits = false [[export]];
};

S2C_CONTEXT_35_12_16_NTC packet @ 0x00;
