// 11.91.16 S2C_QUEST_QUEST_COMPLETE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 34 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f4310, reader 0x818100: u32, 7 x u8 (no header, V); pushes
// cQuestSvNotQuestComplete. PS4 ReadPacket 0x19d67c0 (V; recompilation S2C.cpp:9520 agrees).
// Walk: 4/4 fit, slack 12.
// Body: u32 QuestScheduleId, u8 x7 (11 bytes).
// packet-id: 11.91.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_QUEST_COMPLETE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 QuestScheduleId;
    u8 RandomRewardNum;
    u8 ChargeRewardNum;
    u8 ProgressBonusNum;
    u8 IsRepeatReward;
    u8 IsUndiscoverReward;
    u8 IsHelpReward;
    u8 IsPartyBonus;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_QUEST_COMPLETE_NTC packet @ 0x00;
