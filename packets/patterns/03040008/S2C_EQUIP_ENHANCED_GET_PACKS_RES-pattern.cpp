// 65.3.2 S2C_EQUIP_ENHANCED_GET_PACKS_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 65.3.2.
// PC handler 0x7d5030 cSeedGameSvConnection::OnPacket_EQUIP_ENHANCED_GET_PACKS_RES (V name), reader
// 0x807e10: RES header, list 0x765cc0 (element 0x765d90 {u16, u8, MtString, u16, u16, list 0x77c5a0,
// list 0x7731b0, list 0x77c5a0, list 0x7731b0, list 0x75e9b0, list 0x7650c0 {u8, list 0x764fc0
// {u16, u16, u8}}}) (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 2/2 fit, slack 9; 19 options per list.
// Body: s32 Error [, s32 Result, list CDataEquipEnhanceLotteryOption].
// packet-id: 65.3.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Instance.hexpat"

// Element of PC list reader 0x764fc0 {u16 +4, u16 +6, u8 +8} (V). Struct name neutral; server:
// CDataS2CEquipEnhancedGetPacksResUnk0Unk10Unk1 (lead).
struct CDataEquipEnhanceLotteryOption_unk_1 {
    u16 unk_u16_0;      // T005 open: 3, 23, 931-947 (equal to Index only for Index 3)
    u16 unk_u16_1;      // T005 open: 100 in 38/38
    u8 unk_u8;          // T005 open: 1 in 38/38
};

// Element of PC list reader 0x7650c0 {u8 +4, list 0x764fc0 +8} (V). Struct name neutral; server:
// CDataS2CEquipEnhancedGetPacksResUnk0Unk10 (lead).
struct CDataEquipEnhanceLotteryOption_unk_0 {
    u8 unk_u8;          // T005 open: 1 in 38/38
    MtTypedArray<CDataEquipEnhanceLotteryOption_unk_1> unk_list;
};

// Element of PC list reader 0x765cc0, reader 0x765d90 (V widths and order). Struct name: server (lead).
struct CDataEquipEnhanceLotteryOption {
    u16 Index;          // T005 G (lead): server Index; 19 distinct values 3-47
    u8 Category;        // T005 G (lead): server Category; 1-110
    // T005 I (value, 19 distinct: option titles, e.g. "【追加ステータス】亜人　の特質錬石"); server: RowTitle (lead agrees)
    MtString RowTitle;
    u16 unk_u16_0;      // T005 open: 0 in 38/38; server: RetryLimited (lead)
    u16 unk_u16_1;      // T005 open: 1 in 38/38; server: AttemptModifier (lead)
    // T005 V (same reader 0x77c5a0: CDataWalletPoint); name G (lead); empty in 38/38
    MtTypedArray<CDataWalletPoint> WalletPointCost;
    // T005 V (same reader 0x7731b0: Instance.hexpat GatheringItemListRes_unk_1 {u32, u16}, named
    // ItemId, Num there since T007, both G (value consistent)); name G (lead: server ItemCost); captured:
    // ItemId an itemlist ItemId in 38/38 (19 distinct, chance 0.21; materials 17875-21291), Num 1
    MtTypedArray<GatheringItemListRes_unk_1> ItemCost;
    MtTypedArray<CDataWalletPoint> unk_WalletPointList;     // T005 open: empty; server: Unk7 (lead)
    MtTypedArray<GatheringItemListRes_unk_1> unk_ItemList;  // T005 open: empty; server: Unk8 (lead)
    // T005 V (same reader 0x75e9b0: CDataCommonU8); name G (lead: server ShopTypeListings); 1 in 38/38
    MtTypedArray<CDataCommonU8> ShopTypeList;
    // T005 open: one entry in 38/38; server: MainSuccessExample (lead)
    MtTypedArray<CDataEquipEnhanceLotteryOption_unk_0> unk_list;
};

struct S2C_EQUIP_ENHANCED_GET_PACKS_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataEquipEnhanceLotteryOption> ParamList;   // PC 0x765cc0; T005 G (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_EQUIP_ENHANCED_GET_PACKS_RES packet @ 0x00;
