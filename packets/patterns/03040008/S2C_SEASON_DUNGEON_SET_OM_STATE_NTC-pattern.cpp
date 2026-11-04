// 62.26.16 S2C_SEASON_DUNGEON_SET_OM_STATE_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 62.26.16.
// PC handler 0x7f8970 (no OnPacket_ string): reader 0x766790 {u32, u8, u32, u32, u8} is the whole
// body (V widths). Packet name G (lead: server S2C_SEASON_DUNGEON_SET_OM_STATE_NTC).
// PS4 counterpart: none (Season 3 group).
// Walk: 428/428 fit, slack 9.
// Body: CDataSeasonDungeonOmState (SeasonDungeon.hexpat).
// packet-id: 62.26.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct S2C_SEASON_DUNGEON_SET_OM_STATE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T004 I (same structure: 0x766790 is also the body of 62.15.16's OmState); server writes
    // LayoutId, PosId, State flat (lead agrees)
    CDataSeasonDungeonOmState OmState;     // PC 0x766790
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_SET_OM_STATE_NTC packet @ 0x00;
