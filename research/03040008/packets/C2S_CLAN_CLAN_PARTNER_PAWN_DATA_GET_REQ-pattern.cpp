// 31.40.1 C2S_CLAN_CLAN_PARTNER_PAWN_DATA_GET_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 21.
// PC writer 0x823090: WritePacket(31, 40, 1), Write_u32 (V). PS4 DWARF
// nUserSession::CPacket_C2S_CLAN_PARTNER_PAWN_DATA_GET_REQ {u16 m_usError, u32 m_unPawnID} (V; the
// PS4 writer was not located). The triage's Season 3-exclusive mark is contradicted (C).
// Walk: 28/28 fit, slack 3.
// Body: u32 PawnID (4 bytes).
// packet-id: 31.40.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CLAN_CLAN_PARTNER_PAWN_DATA_GET_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 PawnID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CLAN_CLAN_PARTNER_PAWN_DATA_GET_REQ packet @ 0x00;
