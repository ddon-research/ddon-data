// 23.9.2 S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 13. PC handler 0x7c4330
// (string 0x1bcda68; group-23 table key 2/9), ctor 0x785d10 (23, 9, 2), reader 0x7ffe90 (V). PS4
// counterpart by code: OnPacket_S2C_GET_AREA_QUEST_HINT_LIST_RES 0x303220, CDataAreaQuestHint,
// identical.
// Body: s32 Error [, s32 Result, list] (P11a G1).
// packet-id: 23.9.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC list 0x7591c0 {u32, u32, bool}.
struct CDataAreaQuestHint {
    u32 ScheduleID;
    u32 Price;
    bool IsSold;
};

struct S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataAreaQuestHint> AreaQuestHintList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES packet @ 0x00;
