// 62.16.16 S2C_SEASON_DUNGEON_UPDATE_SOUL_ORDEAL_OBJECTIVES_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 62.16.16.
// PC handler 0x7f8c60 (no OnPacket_ string), reader 0x81a530: list 0x779090 (V). Packet name G (lead).
// PS4 counterpart: none (Season 3 group).
// Walk: 53/53 fit, slack 10-12; 3 objectives in 53/53.
// Body: list CDataSoulOrdealObjective.
// packet-id: 62.16.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct S2C_SEASON_DUNGEON_UPDATE_SOUL_ORDEAL_OBJECTIVES_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataSoulOrdealObjective> Objectives;     // PC 0x779090; T004 G (lead): server Objectives
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_UPDATE_SOUL_ORDEAL_OBJECTIVES_NTC packet @ 0x00;
