// 11.1.1 C2S_QUEST_GET_SET_QUEST_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 3 (section 44 for the shared types in include/Quest.hexpat).
// PC writer 0x8389b0 (11, 1, 1): u32 (V); PS4 Send_* 0x19b79f0: u32 m_unDistributeID (V).
// Walk: 179/179 fit, slack 3.
// Body: u32 DistributeId (4 bytes).
// packet-id: 11.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct C2S_QUEST_GET_SET_QUEST_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 DistributeId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_QUEST_GET_SET_QUEST_LIST_REQ packet @ 0x00;
