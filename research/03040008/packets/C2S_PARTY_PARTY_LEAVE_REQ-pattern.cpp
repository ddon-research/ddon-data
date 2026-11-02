// 6.10.1 C2S_PARTY_PARTY_LEAVE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 7.
// PC writer 0x831f10 (6, 10, 1): no body (V). PS4 Send_C2S_PARTY_LEAVE_REQ 0x19b2900: none (V).
// Walk: 43/43 fit, slack 7.
// Body: none (0 bytes).
// packet-id: 6.10.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_PARTY_PARTY_LEAVE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PARTY_PARTY_LEAVE_REQ packet @ 0x00;
