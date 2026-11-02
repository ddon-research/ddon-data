// 11.101.16 S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 36 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f5830, reader 0x75f030 (no header, V). PS4 0x2eeff0 {u16 m_usError,
// CTimeGainQuestPlayStartData = CDataContentsPlayStartData} without the three Season 3 bools
// and the u8 list (V). Walk: 1/1 fit, slack 2; PS4 body 0/1.
// Body: CDataContentsPlayStartData PlayStartData.
// packet-id: 11.101.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma pattern_limit 3200000
#pragma array_limit 3200000
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataContentsPlayStartData PlayStartData;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC packet @ 0x00;
