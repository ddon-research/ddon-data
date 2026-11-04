// 59.9.2 S2C_INFINITY_DELIVERY_GET_CATEGORY_INFO_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 59.9.2.
// PC handler 0x7d99e0 cSeedGameSvConnection::OnPacket_INFINITY_DELIVERY_GET_CATEGORY_INFO_RES (V name),
// reader 0x80a230: RES header, 0x769b10 {0x769fe0, u8, list 0x76a8d0 {u32, u16, u32}, 0x769de0,
// MtString, list 0x76a390 {u8, u32, u8, u32, list 0x7699f0}, list 0x76a620 {u8, u32, u32, list
// 0x7699f0}, bool} with 0x7699f0 {u32 x4} (V). No server structure (lead: PacketId only). PS4 counterpart: none (Season 3 group).
// Walk: 1/1 fit, slack 10; 1 capture: 27 delivery items, 22 point rewards, 4 rank rewards.
// Body: s32 Error [, s32 Result, CDataInfinityDeliveryCategoryInfo].
// packet-id: 59.9.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "InfinityDelivery.hexpat"

// Element of PC list 0x76a8d0 {u32 +4, u16 +8, u32 +12} (V). Struct name G (context).
struct CDataInfinityDeliveryItem {
    u32 ItemId;     // T004 G (context; value consistent: 27 distinct, chance 0.071; 27/27 item ids of base/etc/itemlist.ipa.json, all ITEM_CATEGORY_MATERIAL)
    u16 MaxNum;     // T004 G (context: 999 in 27/27, the stack limit)
    u32 Point;      // T004 G (context: 40-800 points per item, unit "pt")
};

// Element of PC list 0x7699f0 {u32 +4, +8, +12, +16} (V). Struct name G (context).
struct CDataInfinityDeliveryRewardItem {
    u32 ItemId;     // T004 G (context; value consistent: 30 distinct, chance 0.094; 107/107 item ids of base/etc/itemlist.ipa.json)
    u32 Num;        // T004 G (context: 1-15 beside an item id)
    u32 unk_u32_0;  // T004 open, kept unk: captured 0
    u32 unk_u32_1;  // T004 open, kept unk: captured 0
};

// Element of PC list 0x76a390 {u8 +4, u32 +12, u8 +16, u32 +20, list 0x7699f0 +24} (V). Struct name G (context).
struct CDataInfinityDeliveryPointReward {
    u8 unk_u8_0;            // T004 open, kept unk: captured 1
    u32 RewardId;           // T004 G (context: consecutive ids 439-460)
    u8 unk_u8_1;            // T004 open, kept unk: captured 1
    // T004 G (context: descending 100000 .. 300, read with RequiredPointSuffix "or more")
    u32 RequiredPoint;
    MtTypedArray<CDataInfinityDeliveryRewardItem> ItemList;     // PC 0x7699f0
};

// Element of PC list 0x76a620 {u8 +4, u32 +12, u32 +16, list 0x7699f0 +20} (V). Struct name G (context).
struct CDataInfinityDeliveryRankingReward {
    u8 unk_u8;              // T004 open, kept unk: captured 1
    u32 RewardId;           // T004 G (context: consecutive ids 69-72)
    u32 Rank;               // T004 I (value, 4 distinct: 10, 100, 1000, 3000, the bracket ranks of the RankingList, 4/4)
    MtTypedArray<CDataInfinityDeliveryRewardItem> ItemList;     // PC 0x7699f0
};

// PC reader 0x769b10 {0x769fe0 +8, u8 +56, list 0x76a8d0 +60, 0x769de0 +80, MtString +192, list
// 0x76a390 +196, list 0x76a620 +216, bool +236} (V). Struct name G (context).
struct CDataInfinityDeliveryCategoryInfo {
    CDataInfinityDeliveryEvent Event;   // PC 0x769fe0; T004 I (same structure as 59.0.2; value, 1 distinct: same event)
    u8 unk_u8;              // T004 open, kept unk: captured 3
    MtTypedArray<CDataInfinityDeliveryItem> DeliveryItemList;   // PC 0x76a8d0; T004 G (context)
    CDataInfinityDeliveryCategoryStatus Status;     // PC 0x769de0; T004 I (same structure as 59.4.2)
    MtString RequiredPointSuffix;   // T004 G (context: "or more" in Japanese)
    MtTypedArray<CDataInfinityDeliveryPointReward> PointRewardList;     // PC 0x76a390; T004 G (context)
    MtTypedArray<CDataInfinityDeliveryRankingReward> RankingRewardList; // PC 0x76a620; T004 G (context)
    bool unk_bool;          // T004 open, kept unk: captured 1
};

struct S2C_INFINITY_DELIVERY_GET_CATEGORY_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataInfinityDeliveryCategoryInfo Info;     // PC 0x769b10
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INFINITY_DELIVERY_GET_CATEGORY_INFO_RES packet @ 0x00;
