// 59.8.2 S2C_INFINITY_DELIVERY_GET_CATEGORY_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 59.8.2.
// PC handler 0x7d9ac0 cSeedGameSvConnection::OnPacket_INFINITY_DELIVERY_GET_CATEGORY_LIST_RES (V name),
// reader 0x80a2b0: RES header, list 0x76a060 of 0x76a170 {u32, MtString x5, list 0x769bc0 {u32,
// MtString}} (V). No server structure (lead: PacketId only). PS4 counterpart: none (Season 3 group).
// Walk: 1/1 fit, slack 1; 1 capture, 1 event with 1 category.
// Body: s32 Error [, s32 Result, list].
// packet-id: 59.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "InfinityDelivery.hexpat"

// Element of PC list 0x769bc0 {u32 +4, MtString +8} (V). Struct name G (context).
struct CDataInfinityDeliveryCategory {
    u32 CategoryId;         // T004 G (context; value consistent: 1 distinct; 61, the id that 59.4.1 and 59.9.1 then request, 1/1 each)
    MtString CategoryName;  // T004 G (context; value consistent: 1 distinct; "White Dragon Festival delivery", = 59.4.2 Status.CategoryName)
};

// Element of PC list 0x76a060, reader 0x76a170 {u32 +4, MtString +8, +12, +16, +20, +24, list
// 0x769bc0 +28} (V). Struct name G (context).
struct CDataInfinityDeliveryCategoryList {
    u32 EventId;            // T004 G (context; value consistent: 1 distinct; 29 = the 59.0.2 EventId of the same stream, 1/1)
    MtString EventName;     // T004 G (context; value consistent: 1 distinct; = the 59.0.2 EventName)
    MtString unk_str;       // T004 open, kept unk: captured empty
    // T004 G (context; value consistent: 1 distinct; the event's rules text: deliver materials to the NPCs Cameron and Seneca under
    // "bulk delivery" for rewards)
    MtString Description;
    MtString IconUrl;       // T004 G (context; value consistent: 1 distinct; .../lot_icon_190718_00.jpg)
    MtString ImageUrl;      // T004 G (context; value consistent: 1 distinct; .../lot_main_190718_00.jpg)
    MtTypedArray<CDataInfinityDeliveryCategory> DeliveryCategoryList;   // PC 0x769bc0; T004 G (context)
};

struct S2C_INFINITY_DELIVERY_GET_CATEGORY_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataInfinityDeliveryCategoryList> CategoryList;     // PC 0x76a060; T004 G (context)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INFINITY_DELIVERY_GET_CATEGORY_LIST_RES packet @ 0x00;
