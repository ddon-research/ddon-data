// 11.0.2 S2C_QUEST_GET_LIGHT_QUEST_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 2 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f13d0 (not a function), reader 0x816240: RES header, u32, list 0x76d250 of
// {CDataQuestList, CDataLightQuestDetail, CDataQuestContents}, u8, u8, bool (V). PS4
// CPacket_S2C_GET_LIGHT_QUEST_LIST_RES::ReadPacket 0x19d6170 (V). Season 3: QuestList, detail
// +u32, contents +2 u16. Walk: 1/1 fit, slack 6; the PS4 body fits 0/1.
// Body: s32 Error [, s32 Result, u32 BaseId, MtTypedArray<CDataLightQuestList> LightQuestList, u8
// NotCompleteQuestNum, u8 GpCompletePriceGp, bool GpCompleteEnable].
// packet-id: 11.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma pattern_limit 3200000
#pragma array_limit 3200000
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_GET_LIGHT_QUEST_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 BaseId;
        MtTypedArray<CDataLightQuestList> LightQuestList;
        u8 NotCompleteQuestNum;
        u8 GpCompletePriceGp;
        bool GpCompleteEnable;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_LIGHT_QUEST_LIST_RES packet @ 0x00;
