// 2.12.2 S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_GET_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 6.
// PC handler 0x7c7af0, reader 0x801ed0: RES header only (V); PS4 0x332270: header only (V).
// Walk: 45/45 fit, slack 15.
// Body: s32 Error [, s32 Result].
// packet-id: 2.12.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_GET_RES : CPacket {
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

S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_GET_RES packet @ 0x00;
