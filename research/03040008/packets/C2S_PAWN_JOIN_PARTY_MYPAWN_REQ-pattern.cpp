// 8.12.1 C2S_PAWN_JOIN_PARTY_MYPAWN_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.4.
// PC writer 0x833c80 (8, 12, 1): u8 (V). PS4 Send_C2S_JOIN_PARTY_MYPAWN_REQ 0x19b5170: u8 in_SlotNo (V).
// Walk: 7/7 fit, slack 6.
// Body: u8 SlotNo (1 byte).
// packet-id: 8.12.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_PAWN_JOIN_PARTY_MYPAWN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 SlotNo;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PAWN_JOIN_PARTY_MYPAWN_REQ packet @ 0x00;
