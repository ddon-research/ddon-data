// 72.2.2 S2C_DAILY_MISSION_REWARD_RECEIVE_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 72.2.2.
// PC handler 0x7d1a50 cSeedGameSvConnection::OnPacket_DAILY_MISSION_REWARD_RECEIVE_RES (V name), reader 0x806580: RES header only (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 8/8 fit, slack 15.
// Body: s32 Error [, s32 Result].
// packet-id: 72.2.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_DAILY_MISSION_REWARD_RECEIVE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_DAILY_MISSION_REWARD_RECEIVE_RES packet @ 0x00;
