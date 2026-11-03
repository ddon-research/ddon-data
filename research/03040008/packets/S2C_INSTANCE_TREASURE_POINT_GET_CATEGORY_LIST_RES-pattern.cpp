// 13.16.2 S2C_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 13.16.2.
// PC handler 0x7dc450 cSeedGameSvConnection::OnPacket_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES (V
// name), reader 0x80bdc0: RES header, list 0x77b470 {u32, MtString, u8} (V).
// PS4 counterpart: none matched (spec 006 T004 § 10).
// Walk: 1/1 fit, slack 3; 4 categories 11-14.
// Body: s32 Error [, s32 Result, list CDataTreasurePointCategory].
// packet-id: 13.16.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list reader 0x77b470 {u32 +4, MtString +8, u8 +12} (V). Struct name: server (lead).
struct CDataTreasurePointCategory {
    // T005 I (value: the following 13.17.1 asks for one of them, 1/1); server: CategoryId (lead agrees)
    u32 CategoryId;
    // T005 I (value: category texts, e.g. "古墓解きし手がかり"); server: CategoryName (lead agrees)
    MtString CategoryName;
    // T005 I (value: 5 = the entry count 13.17.2 returns for that category, 1/1); server: EntryCount (lead agrees)
    u8 EntryCount;
};

struct S2C_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataTreasurePointCategory> CategoryList;   // PC 0x77b470; T005 G (lead: server TreasurePointCategories)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES packet @ 0x00;
