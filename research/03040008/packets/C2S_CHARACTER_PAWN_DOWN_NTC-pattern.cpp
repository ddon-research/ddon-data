// 2.19.16 C2S_CHARACTER_PAWN_DOWN_NTC (client 03040008).
// Body: u32 pawn id. P4 4 (PC writer 0x821bb0; PS4 m_unPawnId by the PS4 Send_ of the same name, I).
// packet-id: 2.19.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CHARACTER_PAWN_DOWN_NTC : CPacket {
    u32 PawnId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_PAWN_DOWN_NTC packet @ 0x00;
