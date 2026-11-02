// 11.45.16 S2C_QUEST_PLAY_END_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 23 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f3270 and reader 0x817a10 (not functions): Read_s32 into +16 (the RES Error
// slot), read unconditionally, then 0x75ef90 = 7 x u32 + list CDataRewardItemDetail (V); pushes
// cQuestSvNotEndContentsPlayEnd as PS4 OnPacket_S2C_PLAY_END_NOTICE 0x2f0690 (V). Season 3: the
// lead s32 and three u32. Walk: 1/1 fit, slack 12; PS4 body 0/1.
// Body: s32 unk_s32, CDataContentsPlayEnd ContentsPlayEnd (36 + 7n bytes).
// packet-id: 11.45.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_PLAY_END_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T014b V (role); name I: reader 0x817a10 reads it into packet +0x10 (the RES Error slot) with
    // no u16 error before it (...)
    s32 Error;   // read into the RES Error slot (+16), unconditionally (V); role I; server: Unk0 (lead)
    CDataContentsPlayEnd ContentsPlayEnd;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_PLAY_END_NTC packet @ 0x00;
