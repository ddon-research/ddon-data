// Group 59 INFINITY_DELIVERY ("bulk delivery" event) CData of client 03040008 (PC, Season 3),
// shared by the infinity delivery packet patterns (59.0.2, 59.4.2, 59.9.2).
//
// Source: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 3 and § 4. "PC 0x..." is the
// reader VA in the PC 03040008 database (image base 0x400000). No PS4 02020005 type and no server
// (Arrowgene) structure exists: every name is the T004 one, marked I (value correlation in the one
// captured session, stream85 tcp-stream-11, and client/03040008 data) or G (context: the event's
// own texts and client/03040008/infinity_delivery/ui/00_message/ui/infinity_delivery.gmd.json).
// Comments read `// T004 <mark>: <basis>`. Field consumers were not traced.
// Includes Packet.hexpat only.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataInfinityDeliveryEvent: PC reader 0x769fe0 {u32 +4, MtString +8, s64 +16, +24, +32, +40} (V).
// Users: 59.0.2 (list 0x769ed0), 59.9.2 (inside 0x769b10). Struct name G (context).
struct CDataInfinityDeliveryEvent {
    // T004 I (value: 29 = the EventId of the 59.8.2 category list, 1/1)
    u32 EventId;
    MtString EventName;     // T004 I (value: "White Dragon Festival ~Offering~" in Japanese)
    // T004 G (context: Unix seconds 2019-11-07 02:00 and 2019-11-21 01:00 UTC, the capture
    // (2019-11-18) lies inside)
    s64 StartDate;
    s64 EndDate;            // T004 G (context: see StartDate)
    // T004 open, kept unk: captured = StartDate; with unk_s64_1 a first week inside the event
    // (2019-11-07 to 2019-11-14), perhaps the delivery or a ranking period
    s64 unk_s64_0;
    s64 unk_s64_1;          // T004 open, kept unk: see unk_s64_0
};

// CDataInfinityDeliveryRanking: PC element reader 0x76a850 of list 0x76a760 {u32 +4, u32 +8,
// MtString +12, u32 +16, u32 +20, MtString +24} (V). Struct name G (context: uGUIInfinityDeliveryRanking).
struct CDataInfinityDeliveryRanking {
    u32 Rank;               // T004 I (value: 1-10, 100, 1000, 3000 in list order; the rank rewards name 10, 100, 1000, 3000)
    u32 CharacterId;        // T004 G (context: 6-7 digit ids beside a character name)
    MtString CharacterName; // T004 I (value: "<first> <last>" character names)
    u32 Point;              // T004 I (value: non-increasing with Rank, 24/24; the unit is PointUnit "pt")
    u32 ClanId;             // T004 I (value: 0 exactly when ClanName is empty, 26/26)
    MtString ClanName;      // T004 I (value: clan names)
};

// CDataInfinityDeliveryCategoryStatus: PC reader 0x769de0 {MtString +4, u64 +8, u64 +16, MtString
// +24, list 0x76a760 +28, MtString +48, u32 +52, +56, +60, s64 +64, list 0x75e8e0 +72, list
// 0x75e8e0 +92} (V). Users: 59.4.2, 59.9.2. Struct name G (context).
struct CDataInfinityDeliveryCategoryStatus {
    // T004 I (value: equals the CategoryName of the requested category in 59.8.2, 1/1)
    MtString CategoryName;
    u64 unk_u64_0;          // T004 open, kept unk: captured 1475944980 (2016-10-08) in both packets
    u64 unk_u64_1;          // T004 open, kept unk: captured = unk_u64_0
    MtString PointUnit;     // T004 G (context: "pt")
    MtTypedArray<CDataInfinityDeliveryRanking> RankingList;     // PC 0x76a760; T004 G (context)
    MtString unk_str;       // T004 open, kept unk: captured empty
    u32 unk_u32_0;          // T004 open, kept unk: captured 0 (perhaps the viewer's own rank or points)
    u32 unk_u32_1;          // T004 open, kept unk: captured 0
    u32 unk_u32_2;          // T004 open, kept unk: captured 0
    // T004 G (context: Unix seconds 2019-11-18 17:59 UTC, minutes before the capture; gmd
    // update_time "(Tallied at %s %d:%02d)")
    s64 TallyDate;
    MtTypedArray<CDataCommonU32> unk_list_0;    // PC 0x75e8e0; T004 open, kept unk: captured empty
    MtTypedArray<CDataCommonU32> unk_list_1;    // PC 0x75e8e0; T004 open, kept unk: captured empty
};
