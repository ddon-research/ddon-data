// 11.20.2 S2C_QUEST_QUEST_ORDER_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 13 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f4650, reader 0x818310: RES header, list 0x775310 CDataQuestProcessState (V).
// PS4 0x2ec290 (V). No Season 3 change. Walk: 1/1 fit, slack 3.
// Body: s32 Error [, s32 Result, MtTypedArray<CDataQuestProcessState> QuestProcessStateList].
// packet-id: 11.20.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma pattern_limit 3200000
#pragma array_limit 3200000
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_QUEST_ORDER_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataQuestProcessState> QuestProcessStateList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_QUEST_ORDER_RES packet @ 0x00;
