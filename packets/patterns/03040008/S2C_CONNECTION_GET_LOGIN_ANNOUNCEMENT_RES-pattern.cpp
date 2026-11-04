// 0.3.2 S2C_CONNECTION_GET_LOGIN_ANNOUNCEMENT_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 5.
// PC reader 0x8049d0 via handler 0x7ce240: RES header, Read_MtString (+24) (V). PS4
// OnPacket_S2C_GET_LOGIN_ANNOUNCEMENT_RES 0x2dd200 u16, s32, MtString; DWARF {..., MtString
// m_wstrMessage} (V).
// Walk: 41/41 fit, slack 14; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, MtString Message].
// packet-id: 0.3.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CONNECTION_GET_LOGIN_ANNOUNCEMENT_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtString Message;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONNECTION_GET_LOGIN_ANNOUNCEMENT_RES packet @ 0x00;
