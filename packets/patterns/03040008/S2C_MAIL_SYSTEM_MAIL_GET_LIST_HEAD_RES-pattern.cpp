// 37.6.2 S2C_MAIL_SYSTEM_MAIL_GET_LIST_HEAD_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 14.
// PC handler 0x7e3fb0, reader 0x80f110: RES header, u32 (V); PS4 0x32c970: u32 m_unNum (V).
// Walk: 42/42 fit, slack 11.
// Body: s32 Error [, s32 Result, u32 Num].
// packet-id: 37.6.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_MAIL_SYSTEM_MAIL_GET_LIST_HEAD_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 Num;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_MAIL_SYSTEM_MAIL_GET_LIST_HEAD_RES packet @ 0x00;
