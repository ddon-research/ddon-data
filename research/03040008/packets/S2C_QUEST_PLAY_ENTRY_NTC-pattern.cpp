// 11.39.16 S2C_QUEST_PLAY_ENTRY_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 22 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f3530 reads one u32 inline (no header), finds that party member, sets its entry
// byte and calls a GUI vfunc (index, 1); settled V by behaviour as PS4
// OnPacket_S2C_PLAY_ENTRY_NOTICE 0x2eeab0 {u16 m_usError, u32 m_unCharacterID}.
// Walk: 1/1 fit, slack 3.
// Body: u32 CharacterId (4 bytes).
// packet-id: 11.39.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_PLAY_ENTRY_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_PLAY_ENTRY_NTC packet @ 0x00;
