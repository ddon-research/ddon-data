// 0.2.1 C2S_CONNECTION_LOGOUT_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 4.
// PC writer 0x8244c0: WritePacket(p, 0, 2, 1, -1), no body (V). PS4 Send_C2S_LOGOUT_REQ
// 0x19afdf0 writes the header only (V).
// The login server's C2L_LOGOUT_REQ shares the id 0.2.1: `// packet-select:` below.
// Walk: 42/42 fit, slack 7.
// Body: none. Header only: the PC writer writes no body (V); a 16-byte raw fits any body of 0-7
// bytes, so the emptiness rests on the writer (R1 F3).
// packet-id: 0.2.1
// packet-select: C2S_CONNECTION_LOGOUT_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CONNECTION_LOGOUT_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONNECTION_LOGOUT_REQ packet @ 0x00;
