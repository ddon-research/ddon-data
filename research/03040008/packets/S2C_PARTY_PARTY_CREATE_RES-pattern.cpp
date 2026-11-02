// 6.0.2 S2C_PARTY_PARTY_CREATE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 4.
// PC handler 0x7e7790, reader 0x810a10: header, u32, u64 (V). PS4 OnPacket_S2C_PARTY_CREATE_RES
// 0x2df970 {u32 m_unPartyId, u64 m_ullContentNumber}: same (V).
// Walk: 42/42 fit, slack 3.
// Body: s32 Error [, s32 Result, u32 PartyId, u64 ContentNumber].
// packet-id: 6.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_PARTY_PARTY_CREATE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 PartyId;
        u64 ContentNumber;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTY_PARTY_CREATE_RES packet @ 0x00;
