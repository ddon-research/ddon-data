// 11.122.2 S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.122.2.
// 006 T005 § 41. PC handler 0x7f07d0
// cSeedGameSvConnection::OnPacket_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_RES (V name), reader 0x815a20: RES
// header, list 0x758bc0 of {u8, CDataQuestOrderList 0x774a70 (include/Quest.hexpat), bool, bool, u32} (V
// widths). PS4 counterpart: none (V).
// Walk: 45/45 fit, slack 4-15, 7-20 elements.
// Body: s32 Error [, s32 Result, list].
// packet-id: 11.122.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

// Element of PC list 0x758bc0 {u8, 0x774a70, bool, bool, u32} (V widths). No PS4 type. Struct and
// field names: server CDataQuestAdventureGuideList (lead).
struct CDataQuestAdventureGuideList {
    // T003 G (lead): server Category (QuestAdventureGuideCategory); values 1, 3, 4, 5, 7, 8
    u8 Category;
    // T003 I (same structure): PC reader 0x774a70 = CDataQuestOrderList (Quest.hexpat); server: Param (lead)
    CDataQuestOrderList Param;
    bool Important;   // T003 G (lead): server Important; 1 in 428 of 585 elements
    bool unk_bool;    // T003 open, kept unk: 1 in 585/585; server: Unk2 (lead)
    // T003 G (lead): server QuestOrderBackgroundImage; values 0 (360) and 1006-1025
    u32 QuestOrderBackgroundImage;
};

struct S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 G (lead): server QuestList
        MtTypedArray<CDataQuestAdventureGuideList> QuestList;   // PC 0x758bc0 (V)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_RES packet @ 0x00;
