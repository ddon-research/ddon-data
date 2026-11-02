// 11.90.16 S2C_QUEST_PROGRESS_WORK_SAVE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 33 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f4910, reader 0x818530: u32, u16, u16, u16, list CDataQuestProgressWork (no
// header, V); pushes cQuestSvNotQuestProgressWorkSave. PS4 ReadPacket 0x19d6700 (V).
// Walk: 11/11 fit, slack 5; PS4 framing 0/11.
// Body: u32 QuestScheduleId, u16 ProcessNo, u16 SequenceNo, u16 BlockNo,
// MtTypedArray<CDataQuestProgressWork> WorkList (14 + 20n bytes).
// packet-id: 11.90.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_PROGRESS_WORK_SAVE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 QuestScheduleId;
    u16 ProcessNo;
    u16 SequenceNo;
    u16 BlockNo;
    MtTypedArray<CDataQuestProgressWork> WorkList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_PROGRESS_WORK_SAVE_NTC packet @ 0x00;
