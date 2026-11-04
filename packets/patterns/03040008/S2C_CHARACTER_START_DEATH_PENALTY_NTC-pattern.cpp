// 2.31.16 S2C_CHARACTER_START_DEATH_PENALTY_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 11.
// Code name: START_DEATH_PENALTY_NTC (V by behaviour).
// PC handler 0x7c9d50: u32, no error header; sets object condition 0x3006, timer = 30 * u32 (V).
// PS4 OnPacket_S2C_START_DEATH_PENALTY_NOTICE 0x32a780: u32 m_unRemainTime, sets 0x3006 (V).
// The PS4 u16 framing also fits (the window cannot tell): the framing rests on the PC handler.
// Walk: 2/2 fit, slack 3 (RemainTime 900).
// Body: u32 RemainTime (4 bytes).
// packet-id: 2.31.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CHARACTER_START_DEATH_PENALTY_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 RemainTime;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_START_DEATH_PENALTY_NTC packet @ 0x00;
