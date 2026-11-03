// 62.39.16 S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.39.16.
// Raw/CLI name S2C_SEASON_62_39_16_NTC; pattern name G (context; value): a CharacterId plus the
// (BuffId, Level) pairs of the 62.38.16 area buffs sent within 3 packets (148/148, of which 121 empty lists;
// 27 non-empty, 21 distinct lists; T007). No OnPacket_ string.
// PC handler 0x7f6e40, reader 0x819570: u32, list 0x778fa0 {u32, u32} (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 148/148 fit, slack 7 or 15.
// Body: u32, list CDataSeasonDungeonBuffLevel.
// packet-id: 62.39.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T005 G (lead; value consistent: 3 distinct; the 41 (stream, value) pairs are each a CharacterId field in another JSON of the
    // same stream, 41/41; 3 distinct ids); server: CharacterId (lead agrees)
    u32 CharacterId;
    MtTypedArray<CDataSeasonDungeonBuffLevel> BuffList;   // PC 0x778fa0; T005 G (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC packet @ 0x00;
