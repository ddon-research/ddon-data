// 6.8.2 S2C_PARTY_PARTY_JOIN_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 5.
// PC handler 0x7e8b20, reader 0x8111a0: header, u8, u64, u32 (V). PS4
// CPacket_S2C_PARTY_JOIN_RES::ReadPacket 0x19d4f50 {u8 m_ucMemberIndex, u64 m_ullContentNumber,
// u32 m_unPartyId}; the PS4 recompilation (S2C.cpp) reads the same: same (V).
// Walk: 1/1 fit, slack 2.
// Body: s32 Error [, s32 Result, u8 MemberIndex, u64 ContentNumber, u32 PartyId].
// packet-id: 6.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_PARTY_PARTY_JOIN_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u8 MemberIndex;
        u64 ContentNumber;
        u32 PartyId;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTY_PARTY_JOIN_RES packet @ 0x00;
