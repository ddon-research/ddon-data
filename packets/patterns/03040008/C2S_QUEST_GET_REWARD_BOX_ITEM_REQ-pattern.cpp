// 11.64.1 C2S_QUEST_GET_REWARD_BOX_ITEM_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 27 (section 44 for the shared types in include/Quest.hexpat).
// PC writer 0x838720 (11, 64, 1): u32, 0x77faf0 = u32 count + Write_MtString each (V). PS4
// CPacket_C2S_GET_REWARD_BOX_ITEM_REQ::WritePacket 0x1a37500 (V). Walk: 6/6 fit, slack 1-7.
// Body: u32 ListNo, MtTypedArray<CDataGetRewardBoxItem> UIDList (8 + var bytes).
// packet-id: 11.64.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct C2S_QUEST_GET_REWARD_BOX_ITEM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 ListNo;
    MtTypedArray<CDataGetRewardBoxItem> UIDList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_QUEST_GET_REWARD_BOX_ITEM_REQ packet @ 0x00;
