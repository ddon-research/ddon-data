// 11.32.16 S2C_QUEST_SET_PRIORITY_QUEST_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 18 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f5570, reader 0x818ba0: no header, u32, list CDataPriorityQuest (V). PS4
// OnPacket_S2C_SET_PRIORITY_QUEST_NOTICE 0x2ed9e0 {u16 m_usError, CPriorityQuestSetting} (V).
// Walk: 5/5 fit, slack 3-15; PS4 framing 0/5.
// Body: u32 CharacterId, MtTypedArray<CDataPriorityQuest> PriorityQuestList (8 + var bytes).
// packet-id: 11.32.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_SET_PRIORITY_QUEST_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterId;
    MtTypedArray<CDataPriorityQuest> PriorityQuestList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_SET_PRIORITY_QUEST_NTC packet @ 0x00;
