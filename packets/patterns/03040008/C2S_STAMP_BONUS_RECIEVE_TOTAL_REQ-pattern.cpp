// 45.4.1 C2S_STAMP_BONUS_RECIEVE_TOTAL_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 45.4.1.
// 006 T009 § 20. PC writer 0x83f5a0 (not a function in the database; called from 0x87869b in 0x878650):
// WritePacket(0x2d, 4, 1, -1), then send: no body (V).
// Walk: 1/1 fit, slack 7.
// Body: none.
// packet-id: 45.4.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_STAMP_BONUS_RECIEVE_TOTAL_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_STAMP_BONUS_RECIEVE_TOTAL_REQ packet @ 0x00;
