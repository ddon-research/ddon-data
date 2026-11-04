// 62.10.1 C2S_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.10.1.
// PC writer 0x83aca0: WritePacket(0x3e, 10, 1), Write_u32, list writer 0x77fd30 {Write_MtString +4,
// Write_u32 +8}, Write_bool (V; 008 T002). Name: CLI/server (G (lead)).
// PS4 counterpart: none (Season 3 group).
// Walk: 6/6 fit, slack 4 or 6; 3 or 4 items of 8-hex-digit UIDs, Num summing to 240 each time.
// Body: u32, list CDataItemUIDList, bool.
// packet-id: 62.10.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

struct C2S_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 EpitaphId;      // T005 I (value, 6 distinct: 6/6 = the preceding 62.8.2 EpitaphId); server: EpitaphId (lead agrees)
    // T005 I (same structure: writer 0x77fd30 = Quest.hexpat CDataItemUIDList {UID, Num}, PS4 names; value, 19 distinct:
    // the Num of each list sums to the 240 the preceding 62.9.2 requires, 6/6); list name G (lead:
    // server ItemList)
    MtTypedArray<CDataItemUIDList> ItemList;
    bool unk_bool;      // T005 open: false in 6/6; server: Unk0 (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_REQ packet @ 0x00;
