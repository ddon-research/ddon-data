// 37.7.1 C2S_MAIL_SYSTEM_MAIL_GET_LIST_DATA_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 14.
// PC writer 0x82f680: u32, u32 (V); PS4 0x19c9160: u32 m_unOffset, u32 m_unNum (V).
// Walk: 42/42 fit, slack 15.
// Body: u32 Offset, u32 Num (8 bytes).
// packet-id: 37.7.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_MAIL_SYSTEM_MAIL_GET_LIST_DATA_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 Offset;
    u32 Num;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_MAIL_SYSTEM_MAIL_GET_LIST_DATA_REQ packet @ 0x00;
