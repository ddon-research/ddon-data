// 11.7.16 S2C_QUEST_MOB_HUNT_QUEST_LIST_NUM_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.7.16.
// 006 T005 § 8. PC handler 0x7f2db0 (no name string): packet object (11, 7, 16), reader 0x8176e0 = list
// 0x76eee0 of {u32, u8} (V), no RES header; then it pushes the notice cQuestSvNotQuestMobHuntQuestListNum
// (DTI dti_cQuestSvNotQuestMobHuntQuestListNum) to cQuestSvNoticeManager (V). PS4 counterpart: none (V: no
// MobHunt class or string).
// Name: I (consumer: the notice class the handler pushes), not V (no OnPacket_ string); the raw files keep
// S2C_QUEST_11_7_16_NTC (CLI name).
// Walk: 43/43 fit, slack 14; always 1 element {1, 9}.
// Body: u32 count + count x {u32, u8}.
// packet-id: 11.7.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list 0x76eee0 {u32, u8} (V widths). No PS4 type. Struct name I (notice class).
struct CDataQuestMobHuntQuestListNum {
    u32 unk_u32;   // T003 open, kept unk: 1 in 43/43; no lead
    // T003 G (context: the "ListNum" of the notice class; 9 in 43/43); no lead
    u8 Num;
};

struct S2C_QUEST_MOB_HUNT_QUEST_LIST_NUM_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T003 I (consumer: notice class cQuestSvNotQuestMobHuntQuestListNum); no lead (the server has no structure)
    MtTypedArray<CDataQuestMobHuntQuestListNum> MobHuntQuestListNum;   // PC 0x76eee0 (V)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_MOB_HUNT_QUEST_LIST_NUM_NTC packet @ 0x00;
