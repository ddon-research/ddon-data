// 62.0.2 S2C_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.0.2.
// PC handler 0x7f78c0 cSeedGameSvConnection::OnPacket_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_RES (V name),
// reader 0x819c00: RES header, u32 (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 4/4 fit, slack 11.
// Body: s32 Error [, s32 Result, u32].
// packet-id: 62.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T005 G (lead; value consistent: 1 distinct; 4/4 sent back by the following 62.1.1 and returned by 62.1.2 as
        // DungeonInfo.DungeonId; 3); server: DungeonId (lead agrees)
        u32 DungeonId;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_RES packet @ 0x00;
