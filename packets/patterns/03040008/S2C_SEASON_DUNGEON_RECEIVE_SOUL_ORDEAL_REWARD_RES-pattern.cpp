// 62.34.2 S2C_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 62.34.2.
// PC handler 0x7f82a0 cSeedGameSvConnection::OnPacket_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_RES
// (V name), reader 0x81a240: RES header, list 0x769240 {u32, u32} (V). PS4 counterpart: none.
// Walk: 21/21 fit, slack 3-11; 2 or 3 rewards, Amount 0.
// Body: s32 Error [, s32 Result, list CDataSoulOrdealRewardItem].
// packet-id: 62.34.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct S2C_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataSoulOrdealRewardItem> RewardList;     // PC 0x769240; server name (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_RES packet @ 0x00;
