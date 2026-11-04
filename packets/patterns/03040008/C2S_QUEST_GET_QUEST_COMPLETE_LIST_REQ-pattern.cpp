// 11.31.1 C2S_QUEST_GET_QUEST_COMPLETE_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 12 (section 44 for the shared types in include/Quest.hexpat).
// PC writer 0x838220 (11, 31, 1) and PS4 Send_* 0x19b89d0 agree (V): u8 QuestType (PS4 member u8 m_ucQuestType).
// Walk: 86/86 fit, slack 6.
// Body: u8 QuestType (1 bytes).
// packet-id: 11.31.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct C2S_QUEST_GET_QUEST_COMPLETE_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 QuestType;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_QUEST_GET_QUEST_COMPLETE_LIST_REQ packet @ 0x00;
