// 26.1.1 C2S_PROFILE_GET_MY_CHARACTER_PROFILE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 14.
// PC writer 0x835960 (26, 1, 1): no body (V). PS4 0x19b08f0: none (V).
// Walk: 4/4 fit, slack 7.
// Body: none (0 bytes).
// packet-id: 26.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_PROFILE_GET_MY_CHARACTER_PROFILE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PROFILE_GET_MY_CHARACTER_PROFILE_REQ packet @ 0x00;
