// 8.35.16 S2C_PAWN_GET_PAWN_TOTAL_SCORE_INFO_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.10 (1.3 for the type).
// PC handler 0x7eb510, reader 0x8128a0: u32, u32, CDataPawnTotalScore 0x772a40 (V). PS4
// CPacket_S2C_GET_PAWN_TOTAL_SCORE_INFO_NTC::ReadPacket 0x19d57b0: u16, u32 m_unCharacterId, u32
// m_unPawnId, CPawnTotalScore m_TotalScore (V; same body). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Walk: 74/74 fit, slack 6-15; PS4 framing fails 74/74.
// Body: u32 CharacterId, u32 PawnId, CDataPawnTotalScore TotalScore (24 + 3n bytes).
// packet-id: 8.35.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PAWN_GET_PAWN_TOTAL_SCORE_INFO_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterId;
    u32 PawnId;
    CDataPawnTotalScore TotalScore;                         // PC 0x772a40
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_PAWN_TOTAL_SCORE_INFO_NTC packet @ 0x00;
