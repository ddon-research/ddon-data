// 31.53.2 S2C_CLAN_GET_FURNITURE_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 31.53.2.
// 006 T010 § 22. PC handler 0x7cdd80 cSeedGameSvConnection::OnPacket_CLAN_GET_FURNITURE_RES (V name),
// reader 0x8048c0: RES header, list 0x766f90 CDataFurnitureLayout {u32, u32, u8} (V; the reader the MY_ROOM
// furniture list 52.1.2 uses, include/Furniture.hexpat). PS4 counterpart: none (V).
// Walk: 27/27 fit, slack 3; 8 elements each.
// Body: s32 Error [, s32 Result, list {u32, u32, u8}].
// packet-id: 31.53.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Furniture.hexpat"

struct S2C_CLAN_GET_FURNITURE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 I (same structure: PC list 0x766f90 = CDataFurnitureLayout, Furniture.hexpat; value, 8 distinct, chance 0.62: 8/8
        // distinct ItemID values (216 elements) are ITEM_CATEGORY_CLAN_FURNITURE items in
        // client/03040008/base/etc/itemlist.ipa.json, e.g. 21129 "Christmas Tree"); server: FurnitureLayouts (lead agrees)
        MtTypedArray<CDataFurnitureLayout> FurnitureLayouts;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CLAN_GET_FURNITURE_RES packet @ 0x00;
