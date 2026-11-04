// 62.18.2 S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 62.18.2.
// PC handler 0x7f7a50 cSeedGameSvConnection::OnPacket_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_RES
// (V name), reader 0x819d20: RES header, Read_u8, list 0x7791d0 {u32, MtString, list 0x779330 {u32, u16},
// list 0x779870 {u32, list 0x7796e0 of 0x7797d0 {u32 x3, u8, u8, bool x3}}}, Read_bool, Read_u8,
// Read_bool, Read_u8 (V). PS4 counterpart: none (Season 3 group).
// Server: S2CSeasonDungeonGetSoulOrdealListfromOmRes, same order and widths (lead).
// Walk: 61/61 fit, slack 1-10; ElementParamList holds 0-2 trials, each with 11 or 14 reward sets.
// Body: s32 Error [, s32 Result, u8, list, bool, u8, bool, u8].
// packet-id: 62.18.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

// Element of PC list 0x779330 {u32 +4, u16 +8} (V). Struct name: server CDataSoulOrdealItem (lead),
// renamed CDataSoulOrdealTrialCostItem by T007: SeasonDungeon.hexpat declares CDataSoulOrdealItem (reader
// 0x777c80, 62.9.2) since T005, and the duplicate type broke this pattern's compile.
struct CDataSoulOrdealTrialCostItem {
    // T004 G (lead; value consistent: 1 distinct, chance 1; 26/26 are item 18659 of base/etc/itemlist.ipa.json, ITEM_CATEGORY_MATERIAL);
    // server: ItemId (lead agrees)
    u32 ItemId;
    u16 Num;            // T004 G (lead): server Num; captured 20, 30, 40
};

// Element of PC list 0x7796e0, reader 0x7797d0 {u32 +4, u32 +8, u32 +12, u8 +16, u8 +17, bool +18,
// bool +19, bool +20} (V). Struct name: server CDataSoulOrdealUnk1 (lead) renamed for its role.
struct CDataSoulOrdealRewardEntry {
    // T004 I (value, 146 distinct, chance 3.7e-06: 1,033/1,033 are item ids of base/etc/itemlist.ipa.json, 793 material, 186
    // equipment, 54 use); server: ItemId (lead agrees)
    u32 ItemId;
    u32 Num;            // T004 G (context: 1-80, mostly 1-8, beside an item id); server: Unk1 (lead)
    u32 unk_u32_1;      // T004 open, kept unk: captured 100 (534), 2, 1, 50, 9, ...; server: Unk2 (lead)
    u8 unk_u8_0;        // T004 open, kept unk: captured 0-23; server: Unk3 (lead)
    u8 unk_u8_1;        // T004 open, kept unk: captured 0-4; server: Unk4 (lead)
    bool unk_bool_0;    // T004 open, kept unk; server: Unk5 (lead)
    bool unk_bool_1;    // T004 open, kept unk; server: Unk6 (lead)
    bool unk_bool_2;    // T004 open, kept unk; server: Unk7 (lead)
};

// Element of PC list 0x779870 {u32, list 0x7796e0} (V). Struct name: server CDataSoulOrdealUnk0 (lead)
// renamed for its role.
struct CDataSoulOrdealRewardSet {
    u32 unk_u32;        // T004 open, kept unk: captured 0, 2, 10, 11, 20-23, ...; server: Unk0 (lead)
    MtTypedArray<CDataSoulOrdealRewardEntry> RewardList;    // PC 0x7796e0; T004 G (context); server: Unk1List (lead)
};

// Element of PC list 0x7791d0 {u32 +4, MtString +8, list 0x779330 +12, list 0x779870 +32} (V).
// Struct name: server CDataSoulOrdealElementParam (lead).
struct CDataSoulOrdealElementParam {
    // T004 I (value, 25 distinct: 28/28 62.24.1 and 28/28 62.20.1 requests name a TrialId of the preceding list);
    // server: TrialId (lead agrees)
    u32 TrialId;
    MtString TrialName;     // T004 G (lead; value consistent: 2 distinct; trial names); server: TrialName (lead agrees)
    MtTypedArray<CDataSoulOrdealTrialCostItem> TrialCost;            // PC 0x779330; T004 G (lead)
    MtTypedArray<CDataSoulOrdealRewardSet> TrialRewards;    // PC 0x779870; T004 G (lead)
};

struct S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T004 G (lead): server Type (SoulOrdealOrderState: 0 get list, 4 get rewards, 5 completed, 6 unlock);
        // captured 0 (28), 4 (21), 6 (7), 5 (5)
        u8 Type;
        MtTypedArray<CDataSoulOrdealElementParam> ElementParamList;     // PC 0x7791d0; server name (lead)
        bool unk_bool_0;       // T004 open, kept unk: captured 0/1; server: Unk2 (lead)
        u8 unk_u8_0;           // T004 open, kept unk: captured 0; server: Unk3 (lead)
        bool unk_bool_1;       // T004 open, kept unk: captured 0/1; server: Unk4 (lead)
        u8 unk_u8_1;           // T004 open, kept unk: captured 0; server: Unk5 (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_RES packet @ 0x00;
