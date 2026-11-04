// 6.10.16 S2C_PARTY_PARTY_LEAVE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 7.
// PC handler 0x7e8e50 (gate as 6.8.16; read path 0x7e8e80): one u32, then the no-leader information
// and sGame party warp reset (V). PS4 OnPacket_S2C_PARTY_LEAVE_NTC 0x2e1870 {u16 m_usError, u32
// m_unCharacterID}; cNetGameServer::OnPacket_S2C_PARTY_LEAVE_NTC 0x36d780 does the same
// (match V by behaviour). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError. The PS4 framing fits too (slack 3).
// Walk: 43/43 fit, slack 3.
// Body: u32 CharacterID (4 bytes).
// packet-id: 6.10.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_PARTY_PARTY_LEAVE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTY_PARTY_LEAVE_NTC packet @ 0x00;
