// 63.11.16 S2C_63_11_16_NTC (client 03040008).
// Body: empty. P5 7: the PC client writes this packet (writer 0x826270, WritePacket(0x3F, 0x0B,
// 0x10), empty body), so its direction is C2S; the raw-file name (server Name) says S2C. The
// client name is unresolved.
// packet-id: 63.11.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_63_11_16_NTC : CPacket {
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_63_11_16_NTC packet @ 0x00;
