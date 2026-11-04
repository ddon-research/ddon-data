// 62.38.16 S2C_SEASON_DUNGEON_AREA_BUFFS_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.38.16.
// PC handler 0x7f6ad0 (no OnPacket_ string; name G (lead): server S2C_SEASON_DUNGEON_AREA_BUFFS_NTC),
// reader 0x819510: list 0x778e70 {u32, 0x779540 {u32, MtString, u32 x5}} (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 148/148 fit, slack 2-13; 0-5 buffs, BuffId 4, 7-10, Level 1-3.
// Body: list CDataSeasonDungeonBuffEffectParam.
// packet-id: 62.38.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct S2C_SEASON_DUNGEON_AREA_BUFFS_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataSeasonDungeonBuffEffectParam> BuffEffectParamList;  // PC 0x778e70; T005 G (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_AREA_BUFFS_NTC packet @ 0x00;
