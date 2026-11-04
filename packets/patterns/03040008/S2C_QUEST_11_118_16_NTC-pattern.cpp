// 11.118.16 S2C_QUEST_11_118_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.118.16.
// 006 T005 § 39. PC handler 0x7f2e50 reads one u8 into a local and returns: the client ignores it (V). No
// name string, no lead structure: the raw name stays. PS4 counterpart: not settled (7 PS4 notices read u16
// + u8).
// Walk: 41/41 fit, slack 6; the u8 is 0 in 41/41.
// Body: u8.
// packet-id: 11.118.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_QUEST_11_118_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T003 V (read and discarded by the handler); name open, kept unk; no lead
    u8 unk_u8;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_11_118_16_NTC packet @ 0x00;
