// 13.17.2 S2C_INSTANCE_TREASURE_POINT_GET_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 13.17.2.
// PC handler 0x7dc590 cSeedGameSvConnection::OnPacket_INSTANCE_TREASURE_POINT_GET_LIST_RES (V name),
// reader 0x80bed0: RES header, u32, list 0x77b580 {u32, MtString, bool} (V).
// PS4 counterpart: none matched (spec 006 T004 § 10).
// Walk: 1/1 fit, slack 10; 5 points.
// Body: s32 Error [, s32 Result, u32, list CDataTreasurePoint].
// packet-id: 13.17.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list reader 0x77b580 {u32 +4, MtString +8, bool +12} (V). Struct name: server (lead).
struct CDataTreasurePoint {
    // T005 I (value, 5 distinct: 0-4, and Name ends in 《Index + 1》 5/5); server: Index (lead agrees)
    u32 Index;
    MtString Name;      // T005 I (value, 5 distinct: "古墓解きし手がかり《1》" .. 《5》); server: Name (lead agrees)
    bool unk_bool;      // T005 open: true in 5/5; server: Unk2 (lead)
};

struct S2C_INSTANCE_TREASURE_POINT_GET_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 CategoryId;     // T005 G (lead; value consistent: 1 distinct; 1/1 = the 13.17.1 CategoryId); server: CategoryId (lead agrees)
        MtTypedArray<CDataTreasurePoint> TreasurePointList;   // PC 0x77b580; T005 G (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_TREASURE_POINT_GET_LIST_RES packet @ 0x00;
