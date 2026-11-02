// 11.103.16 S2C_QUEST_11_103_16_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 37 (section 44 for the shared types in include/Quest.hexpat).
// Code name PLAY_STOP_TIMER_NOTICE (V): PC handler 0x7f3fa0 reads nothing, builds a packet
// object (11/103/16) and pushes cQuestSvNotStopTimer (dti__1525); PS4's only user
// OnPacket_S2C_PLAY_STOP_TIMER_NOTICE 0x2ef890 reads u16 m_usError only (PS4 framing).
// Walk: 1/1 fit, slack 7 (a 16-byte raw fits any body of 0-7 bytes: the emptiness rests on the
// handler).
// Body: none.
// packet-id: 11.103.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_11_103_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_11_103_16_NTC packet @ 0x00;
