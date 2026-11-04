// 62.8.2 S2C_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.8.2.
// PC handler 0x7f75d0 cSeedGameSvConnection::OnPacket_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_RES (V
// name), reader 0x8199d0: RES header, u32 (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 7/7 fit, slack 11.
// Body: s32 Error [, s32 Result, u32].
// packet-id: 62.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T005 I (value, 6 distinct: the following 62.9.1 7/7 and 62.10.1 6/6 send it back; 119-124, one per
        // 62.8.1 GroupId); server: EpitaphId (lead agrees)
        u32 EpitaphId;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_RES packet @ 0x00;
