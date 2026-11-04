// 11.70.16 S2C_QUEST_DECIDE_DELIVERY_ITEM_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 30 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f0130, reader 0x8155c0: u32, u32, no header (V); pushes
// cQuestSvNotDecideDeliveryItem (dti__1497), whose only PS4 OnPacket is
// OnPacket_S2C_DECIDE_DELIVERY_ITEM_NOTICE 0x313140 {u16 m_usError, u32 m_unQuestScheduleId, u32
// m_unProcessNo} (V). Walk: 1/1 fit, slack 15.
// Body: u32 QuestScheduleId, u32 ProcessNo (8 bytes).
// packet-id: 11.70.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_DECIDE_DELIVERY_ITEM_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 QuestScheduleId;
    u32 ProcessNo;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_DECIDE_DELIVERY_ITEM_NTC packet @ 0x00;
