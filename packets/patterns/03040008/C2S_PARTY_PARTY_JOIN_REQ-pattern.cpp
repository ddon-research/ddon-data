// 6.8.1 C2S_PARTY_PARTY_JOIN_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 5.
// PC writer 0x831e30 (6, 8, 1): u32 (V). PS4 Send_C2S_PARTY_JOIN_REQ 0x19b27c0(u32 in_PartyId) (V).
// Walk: 1/1 fit, slack 3 (PartyId 3492, the one 6.18.16 delivered 3 s before).
// Body: u32 PartyId (4 bytes).
// packet-id: 6.8.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_PARTY_PARTY_JOIN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 PartyId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PARTY_PARTY_JOIN_REQ packet @ 0x00;
