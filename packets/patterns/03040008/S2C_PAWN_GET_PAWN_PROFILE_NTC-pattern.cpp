// 8.33.16 S2C_PAWN_GET_PAWN_PROFILE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.8 (1.3 for the type).
// PC handler 0x7eb470, reader 0x812820: u32, u32, CDataPawnProfile 0x7727d0 (V). PS4
// OnPacket_S2C_GET_PAWN_PROFILE_NOTICE 0x2e53b0: u16 m_usError, u32 m_unCharacterId, u32 m_unPawnId,
// CPawnProfile m_PawnProfile (V; same body). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Walk: 74/74 fit, slack 1-4; PS4 framing fails 74/74.
// Body: u32 CharacterId, u32 PawnId, CDataPawnProfile PawnProfile.
// packet-id: 8.33.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PAWN_GET_PAWN_PROFILE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterId;
    u32 PawnId;
    CDataPawnProfile PawnProfile;                           // PC 0x7727d0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_PAWN_PROFILE_NTC packet @ 0x00;
