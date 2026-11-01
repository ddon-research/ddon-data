// 1.1.1 C2S_SERVER_GET_GAME_SETTING_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 11.
// PC writer 0x83c160: WritePacket(p, 1, 1, 1, -1), no body (V).
// Walk: 42/42 fit, slack 7.
// Body: none. Header only: the PC writer writes no body (V); a 16-byte raw fits any body of 0-7
// bytes, so the emptiness rests on the writer (R1 F3).
// packet-id: 1.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_SERVER_GET_GAME_SETTING_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_SERVER_GET_GAME_SETTING_REQ packet @ 0x00;
