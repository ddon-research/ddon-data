// 0.0.2 L2C_PING_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 1.
// PC reader 0x889a30 via handler 0x887740 (key 0x20000) (V): s32 Error; Result and the body only when Error == 0 (T002
// section 0.2).
// PS4 OnPacket_L2C_PING_RES 0x37c6c0, slot 3; DWARF CPacket_L2C_PING_RES {u16 m_usError,
// s32 m_nResult} (V).
// Walk: 75/75 fit, slack 15; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result].
// packet-id: 0.0.2
// packet-select: L2C_PING_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct L2C_PING_RES : CPacket {
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

L2C_PING_RES packet @ 0x00;
