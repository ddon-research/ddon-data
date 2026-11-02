// 8.34.16 S2C_PAWN_GET_PAWN_HISTORY_INFO_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.9 (1.2 for the type).
// PC handler 0x7eafc0, reader 0x8126a0: u32, u32, list 0x772020 (V). PS4
// OnPacket_S2C_GET_PAWN_HISTORY_INFO_NTC 0x2e5740: u16, u32 m_unCharacterId, u32 m_unPawnId,
// m_PawnHistoryList (V; same body). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Walk: 74/74 fit, slack 3-13; PS4 framing fails 73/74.
// Body: u32 CharacterId, u32 PawnId, list CDataPawnHistory.
// packet-id: 8.34.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PAWN_GET_PAWN_HISTORY_INFO_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterId;
    u32 PawnId;
    MtTypedArray<CDataPawnHistory> PawnHistoryList;        // PC 0x772020
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_PAWN_HISTORY_INFO_NTC packet @ 0x00;
