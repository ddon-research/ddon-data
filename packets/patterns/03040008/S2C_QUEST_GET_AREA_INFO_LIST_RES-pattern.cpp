// 11.56.2 S2C_QUEST_GET_AREA_INFO_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 11. PC handler 0x7f0a10
// (string 0x1bc6a78), ctor 0x78b290 (11, 56, 2), reader 0x815ba0 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_AREA_INFO_LIST_RES 0x2f27d0, CDataAreaInfoList, identical.
// Body: s32 Error [, s32 Result, list] (P11a G1).
// packet-id: 11.56.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC list 0x759090 {u32, u8, u8, u8, bool}.
struct CDataAreaInfoList {
    u32 AreaId;
    u8 Weather;
    u8 UndiscoveredQuestNum;
    u8 HighDiffcultyQuestNum;
    bool IsBonus;
};

struct S2C_QUEST_GET_AREA_INFO_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataAreaInfoList> AreaInfoList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_AREA_INFO_LIST_RES packet @ 0x00;
