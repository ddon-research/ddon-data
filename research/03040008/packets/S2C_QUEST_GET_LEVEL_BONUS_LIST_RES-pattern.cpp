// 11.121.2 S2C_QUEST_GET_LEVEL_BONUS_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.121.2.
// 006 T005 § 40. PC handler 0x7f1320 cSeedGameSvConnection::OnPacket_QUEST_GET_LEVEL_BONUS_LIST_RES (V
// name), reader 0x8161c0: RES header, list 0x75a600 of {u32, list 0x76cf70 of 0x76d050 {u32, u32, u16, u16,
// u16, u16}} (V widths). The handler keeps the packet object in a connection slot (consumer not traced).
// PS4 counterpart: none (V).
// Walk: 182/182 fit, slack 3; always 1 x {28, 1 x {1, 89, 100, 2000, 100, 100}}.
// Body: s32 Error [, s32 Result, list].
// packet-id: 11.121.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list 0x76cf70, reader 0x76d050 {u32, u32, u16 x4} (V widths). No PS4 type. Names:
// server CDataLevelBonusElement (lead; "MinLevel // Maybe?"). The captured element (1, 89, 100,
// 2000, 100, 100) in 182/182 reads as a level range and four percentages (100 = unchanged): G (lead).
struct CDataLevelBonusElement {
    u32 MinLevel;         // T003 G (lead): 1 in 182/182
    u32 MaxLevel;         // T003 G (lead): 89 in 182/182
    u16 GoldRatio;        // T003 G (lead): 100
    u16 ExpRatio;         // T003 G (lead): 2000
    u16 RimRatio;         // T003 G (lead): 100
    u16 AreaPointRatio;   // T003 G (lead): 100
};

// Element of PC list 0x75a600 {u32, list 0x76cf70} (V widths). No PS4 type. Struct name: server (lead).
struct CDataLevelBonus {
    u32 unk_u32;   // T003 open, kept unk: 28 in 182/182; server: Unk0 (lead)
    MtTypedArray<CDataLevelBonusElement> BonusList;   // T003 G (lead): server BonusList
};

struct S2C_QUEST_GET_LEVEL_BONUS_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 G (lead): server LevelBonusList
        MtTypedArray<CDataLevelBonus> LevelBonusList;   // PC 0x75a600 (V)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_LEVEL_BONUS_LIST_RES packet @ 0x00;
