// 8.12.2 S2C_PAWN_JOIN_PARTY_MYPAWN_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.4.
// PC handler 0x7ebd40, reader 0x812cc0: RES header only (V). PS4 OnPacket_S2C_JOIN_PARTY_MYPAWN_RES
// 0x2e5ff0: header only (V). Walk: 9/9 fit, slack 15.
// Body: s32 Error [, s32 Result].
// packet-id: 8.12.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_PAWN_JOIN_PARTY_MYPAWN_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_JOIN_PARTY_MYPAWN_RES packet @ 0x00;
