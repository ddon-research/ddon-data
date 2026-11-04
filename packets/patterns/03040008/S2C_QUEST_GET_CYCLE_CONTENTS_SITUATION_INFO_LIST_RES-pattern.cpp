// 11.38.2 S2C_QUEST_GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 20 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f0f60, reader 0x815f80: RES header, u32, list {u32, u32} (V). PS4 0x2ee590 {u32
// m_unCycleContentsScheduleId, MtTypedArray<CDataQuestContentsSituationInfo>} (V).
// Walk: 2/2 fit, slack 7.
// Body: s32 Error [, s32 Result, u32 CycleContentsScheduleId,
// MtTypedArray<CDataQuestContentsSituationInfo> SituationInfoList] (16 + 8n bytes).
// packet-id: 11.38.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 CycleContentsScheduleId;
        MtTypedArray<CDataQuestContentsSituationInfo> SituationInfoList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_RES packet @ 0x00;
