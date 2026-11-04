// 3.0.1 C2L_GET_ERROR_MESSAGE_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 8.
// PC writer 0x88a600: WritePacket(p, 3, 0, 1, -1), no body (V).
// PS4 cNetLoginServer::getErrorMessageList 0x380160, status slot 9 (V). The list arrives in
// 3.0.16 NTCs before the 3.0.2 RES.
// Walk: 41/41 fit, slack 7.
// Body: none. Header only: the PC writer writes no body (V); a 16-byte raw fits any body of 0-7
// bytes, so the emptiness rests on the writer (R1 F3).
// packet-id: 3.0.1
// packet-select: C2L_GET_ERROR_MESSAGE_LIST_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2L_GET_ERROR_MESSAGE_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2L_GET_ERROR_MESSAGE_LIST_REQ packet @ 0x00;
