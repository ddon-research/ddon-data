// 11.95.16 S2C_QUEST_11_95_16_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 35 (section 44 for the shared types in include/Quest.hexpat).
// Code name FORT_DEFENSE_NOTICE (V): PC handler 0x7f0480, reader 0x815860 (no header): list
// 0x766c00 of 0x761970, list 0x773ba0 of 0x773c60 (V); pushes cQuestSvNotCycle01Phase
// (dti__1492), whose only PS4 user is OnPacket_S2C_FORT_DEFENSE_NOTICE 0x2edea0. Season 3: a
// second u64 in the notice data and a {u32, u32} list in the detail. Walk: 48/48 fit, slack
// 1-11; PS4 body 0/48.
// Body: MtTypedArray<CDataFortDefenseNoticeData> FortDefenseNoticeDataList,
// MtTypedArray<CDataQuestContentsSituationInfoDetail> SituationInfoDetailList.
// packet-id: 11.95.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma pattern_limit 3200000
#pragma array_limit 3200000
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_11_95_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataFortDefenseNoticeData> FortDefenseNoticeDataList;
    MtTypedArray<CDataQuestContentsSituationInfoDetail> SituationInfoDetailList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_11_95_16_NTC packet @ 0x00;
