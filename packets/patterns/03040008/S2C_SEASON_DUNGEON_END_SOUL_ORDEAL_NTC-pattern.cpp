// 62.15.16 S2C_SEASON_DUNGEON_END_SOUL_ORDEAL_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 62.15.16.
// PC handler 0x7f8630 (no OnPacket_ string), reader 0x81a3c0: Read_u8, 0x766790, Read_u32 (V).
// Packet name G (lead). PS4 counterpart: none (Season 3 group).
// Walk: 28/28 fit, slack 4.
// Body: u8, CDataSeasonDungeonOmState, u32.
// packet-id: 62.15.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct S2C_SEASON_DUNGEON_END_SOUL_ORDEAL_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T004 G (lead): server EndState (SoulOrdealEndState: 0 cancel, 1 success, 2 failed); captured 1 (21),
    // 2 (7); all 7 failures carry an all-zero OmState, all 21 successes OmState.State 5
    u8 EndState;
    // T004 I (same structure as 62.26.16, PC 0x766790); server: LayoutId, PosId, EpitaphState flat (lead)
    CDataSeasonDungeonOmState OmState;
    // T004 I (value, 13 distinct: equals the TrialId of the preceding 62.14.16/62.24.1 in 28/28); server: Unk3 (lead; replaced)
    u32 TrialId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_END_SOUL_ORDEAL_NTC packet @ 0x00;
