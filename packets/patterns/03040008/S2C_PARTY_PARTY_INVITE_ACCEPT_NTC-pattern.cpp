// 6.18.16 S2C_PARTY_PARTY_INVITE_ACCEPT_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 9.
// PC handler 0x7e78d0, reader 0x810b30: u16, u32, u32, u32, u8 (V). PS4
// CPacket_S2C_PARTY_INVITE_ACCEPT_NTC::ReadPacket 0x19d4e90: u16 m_usError, u16 m_usServerId, u32
// m_unPartyId, u32 m_unStageId, u32 m_unPositionId, u8 m_ucMemberIndex: same widths and order after
// the PS4 error; the PartyId it delivers is the one 6.8.1 then sends (match V by code shape and
// capture flow; PC consumer sub_4096F0 not traced). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError. The PS4 framing fits too (slack 8).
// Walk: 1/1 fit, slack 8.
// Body: u16 ServerId, u32 PartyId, u32 StageId, u32 PositionId, u8 MemberIndex (15 bytes).
// packet-id: 6.18.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_PARTY_PARTY_INVITE_ACCEPT_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u16 ServerId;
    u32 PartyId;
    u32 StageId;
    u32 PositionId;
    u8 MemberIndex;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTY_PARTY_INVITE_ACCEPT_NTC packet @ 0x00;
