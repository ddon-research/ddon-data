// 37.9.1 C2S_MAIL_SYSTEM_MAIL_GET_TEXT_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 15.
// PC writer 0x82f8f0 (37, 9, 1): u64 (V); PS4 0x19c93f0: u64 m_ullId (V). Walk: 7/7 fit, slack 15.
// Body: u64 Id (8 bytes).
// packet-id: 37.9.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_MAIL_SYSTEM_MAIL_GET_TEXT_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u64 Id;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_MAIL_SYSTEM_MAIL_GET_TEXT_REQ packet @ 0x00;
