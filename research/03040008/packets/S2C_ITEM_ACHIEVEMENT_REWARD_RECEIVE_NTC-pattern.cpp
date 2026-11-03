// 10.14.16 S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 10.14.16.
// PC handler 0x7de260 (no OnPacket_ string; name G (lead)), reader 0x80cca0: Read_u16, list 0x76cc70
// {u8, u32} (V). The server writes one fixed element (u16, u32 1, u8, u32): the same bytes for one entry.
// PS4 counterpart: none matched (spec 006 T008 § 3).
// Walk: 1/1 fit, slack 12.
// Body: u16, list {u8, u32}.
// packet-id: 10.14.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list reader 0x76cc70 {u8 +4, u32 +8} (V). Struct name G (context).
struct CDataItemAchievementReward {
    u8 unk_u8;          // T005 open: 7 in 1/1; server: Unk2 (lead)
    // T005 V (consumer): handler 0x7de260 passes element +8 to the sItemManager lookup 0xb98c80 and,
    // when found, posts chat message 0x85 with the item (specs/008-remaining-packets/research/
    // T006-adversarial.md F1; T007); value, 1 distinct: 16227, an itemlist ItemId (craft recipe);
    // server: ItemId (lead agrees)
    u32 ItemId;
};

struct S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u16 unk_u16;        // T005 open: 2 in 1/1; server: Unk0 (lead)
    MtTypedArray<CDataItemAchievementReward> unk_list;  // PC 0x76cc70; T005 open (server writes the count as Unk1)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC packet @ 0x00;
