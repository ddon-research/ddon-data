// 0.2.2 S2C_CONNECTION_LOGOUT_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 4.
// PC reader 0x804ae0 via handler 0x7ce5c0: RES header only (V). PS4 OnPacket_S2C_LOGOUT_RES
// 0x2dd050 u16, s32; DWARF agrees (V).
// The login server's L2C_LOGOUT_RES shares the id 0.2.2: `// packet-select:` below.
// Walk: 42/42 fit, slack 15; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result].
// packet-id: 0.2.2
// packet-select: S2C_CONNECTION_LOGOUT_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CONNECTION_LOGOUT_RES : CPacket {
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

S2C_CONNECTION_LOGOUT_RES packet @ 0x00;
