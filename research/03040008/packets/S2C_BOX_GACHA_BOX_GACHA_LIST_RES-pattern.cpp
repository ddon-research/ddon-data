// 57.0.2 S2C_BOX_GACHA_BOX_GACHA_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 8. PC handler 0x7c6f40
// (string 0x1bd2d68; inline 57, 0, 2), reader 0x8018e0 (V). PS4 counterpart by code:
// OnPacket_S2C_BOX_GACHA_LIST_RES 0x337c40 (DWARF CDataBoxGachaInfo / SettlementInfo / ItemInfo),
// which lacks the two Season 3 fields marked below.
// Body: s32 Error [, s32 Result, list] (P11a G1).
// packet-id: 57.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC list 0x75acd0 {u32 x4, u8, u8, u32 x4, u32}.
struct CDataBoxGachaSettlementInfo {
    u32 DrawId;
    u32 Id;
    u32 Price;
    u32 BasePrice;
    u8 DrawNum;
    u8 BonusNum;
    u32 PurchaseNum;
    u32 PurchaseMaxNum;
    u32 SpecialPriceNum;
    u32 SpecialPriceMaxNum;
    // T014b V (flow); I (name): PC 0xd9fef0 box path (getter 0x869100, conn sub +0x468) passes box
    // settlement +40 (reader 0x75ade0: +4 DrawId . (...)
    u32 ChargeId;               // Season 3; position I: PC reads 5 u32s here, PS4 4 (R2 F5)
};

// PC list 0x75ab40 {u32 x5, f64, u16}.
struct CDataBoxGachaItemInfo {
    u32 ItemId;
    u32 ItemNum;
    u32 ItemStock;
    u32 Rank;
    u32 Effect;
    double Probability;
    u16 DrawNum;
};

// PC list 0x75a970.
struct CDataBoxGachaInfo {
    u32 Id;
    s64 Begin;
    s64 End;
    // T014b open (not read), kept unk: box info +24 (reader 0x75aa30: +4 Id, +8/+16 s64, +24 bool,
    // +28 Name). The only access to the list is the getter 0x869100 (19 call sites in 0x558410 and
    // 0xd9df40..0xda6410) (...)
    bool unk_bool;             // Season 3
    MtString Name;
    MtString Description;
    MtString Detail;
    u8 WeightDispType;
    MtString FreeSpaceText;
    MtString ListAddr;
    MtString ImageAddr;
    MtTypedArray<CDataBoxGachaSettlementInfo> SettlementList;
    MtTypedArray<CDataBoxGachaItemInfo> BoxGachaSets;
};

struct S2C_BOX_GACHA_BOX_GACHA_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataBoxGachaInfo> BoxGachaList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_BOX_GACHA_BOX_GACHA_LIST_RES packet @ 0x00;
