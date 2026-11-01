// 11.37.2 S2C_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 12. PC handler 0x7f1080
// (string 0x1bc94e0; on-stack 11, 37, 2), reader 0x816010 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_CYCLE_CONTENTS_STATE_LIST_RES 0x2ee2f0, CDataCycleContentsStateList, identical.
// Enums: nQuest::CYCLE_CONTENTS_CATEGORY / _SUB_CATEGORY (PS4 DWARF, Quest.hexpat); the enum
// views over the u8 / u32 are display only.
// Body: s32 Error [, s32 Result, list] (P11a G1).
// packet-id: 11.37.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

// PC list 0x762100 {u32, u8, u32, u8}.
struct CDataCycleContentsStateList {
    u32 CycleContentsScheduleId;
    u8 Category;
    CYCLE_CONTENTS_CATEGORY CategoryName = Category [[export]];
    u32 CategoryType;
    CYCLE_CONTENTS_SUB_CATEGORY CategoryTypeName = CategoryType [[export]];
    u8 State;
};

struct S2C_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCycleContentsStateList> CycleContentsStateList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_RES packet @ 0x00;
