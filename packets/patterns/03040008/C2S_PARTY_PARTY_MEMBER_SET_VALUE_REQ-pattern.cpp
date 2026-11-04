// 6.15.1 C2S_PARTY_PARTY_MEMBER_SET_VALUE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 8.
// PC writer 0x8320b0 (6, 15, 1): u8, u8 (V). PS4 Send_C2S_PARTY_MEMBER_SET_VALUE_REQ
// 0x19b2160(u8 in_Index, u8 in_Value) (V).
// Walk: 6/6 fit, slack 5 (Index 2 in 6/6, Value 0 or 1).
// Body: u8 Index, u8 Value (2 bytes).
// packet-id: 6.15.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_PARTY_PARTY_MEMBER_SET_VALUE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 Index;
    u8 Value;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PARTY_PARTY_MEMBER_SET_VALUE_REQ packet @ 0x00;
