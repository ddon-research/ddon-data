// 11.10.2 S2C_QUEST_GET_END_CONTENTS_GROUP_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 10 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f1180, reader 0x816090: RES header, u32, u32, 0x764fa0 -> list 0x77afb0 of
// 0x77b080 (V). PS4 ReadPacket 0x19d6230 {u32 m_unGroupID, u32 m_unEndContentsType,
// CEndContentsGroup {MtTypedArray<CDataTimeGainQuestList>}} (V). Season 3: element +bool and two
// members. Walk: 3/3 fit, slack 10; PS4 body 0/3.
// Body: s32 Error [, s32 Result, u32 GroupId, u32 EndContentsType, MtTypedArray<CDataTimeGainQuestList>
// TimeGainQuestList].
// packet-id: 11.10.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma pattern_limit 3200000
#pragma array_limit 3200000
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_GET_END_CONTENTS_GROUP_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 GroupId;
        u32 EndContentsType;
        MtTypedArray<CDataTimeGainQuestList> TimeGainQuestList;   // PS4 CEndContentsGroup member
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_END_CONTENTS_GROUP_RES packet @ 0x00;
