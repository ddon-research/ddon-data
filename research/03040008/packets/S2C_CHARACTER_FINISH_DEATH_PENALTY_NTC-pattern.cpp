// 2.32.16 S2C_CHARACTER_FINISH_DEATH_PENALTY_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 11.
// Code name: FINISH_DEATH_PENALTY_NTC (V by behaviour).
// PC handler 0x7c8d90: no body; clears object condition 0x3006, timer 0 (V). PS4
// OnPacket_S2C_FINISH_DEATH_PENALTY_NOTICE 0x32a950: no body, cures 0x3006 (V).
// The PS4 u16 framing also fits (the window cannot tell): the framing rests on the PC handler.
// Walk: 1/1 fit, slack 7.
// Body: empty.
// packet-id: 2.32.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CHARACTER_FINISH_DEATH_PENALTY_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_FINISH_DEATH_PENALTY_NTC packet @ 0x00;
