// 53.9.16 S2C_PARTNER_PAWN_LIKABILITY_UP_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 3.4.
// PC handler 0x7e6d50 (53, 9, 16): inline Read_u32, then an announce and a chat message of message
// index 0x1CC (V; the u32 is not used). PS4 OnPacket_S2C_PAWN_LIKABILITY_UP_NTC 0x3363a0: u16
// m_usError, u32 m_unPawnId, announce of index 0x1CE (V by behaviour: code name PAWN_LIKABILITY_UP_NTC;
// the index difference is open). No error header: the PC handler reads none (V; the PS4 framing also
// fits, so the framing rests on the PC code). Walk: 23/23 fit, slack 3.
// Body: u32 PawnId (4 bytes).
// packet-id: 53.9.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_PARTNER_PAWN_LIKABILITY_UP_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 PawnId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTNER_PAWN_LIKABILITY_UP_NTC packet @ 0x00;
