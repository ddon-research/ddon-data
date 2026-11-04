// 8.37.16 S2C_PAWN_JOIN_PARTY_PAWN_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.12 (1.3 for the type).
// PC handler 0x7ebeb0 (read linearly): ignored while the connection's join flag is clear, else
// reads CDataPartyMember 0x771580 (V). PS4 cSeedGameSvConnection::OnPacket_S2C_JOIN_PARTY_PAWN_NOTICE
// 0x2e63b0: same guard, u16 m_usError, Read_CDataPartyMember_; the only PS4 reader of a single
// CDataPartyMember (V: code name JOIN_PARTY_PAWN_NOTICE). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Season 3: CDataCharacterListElement's trailing u8 (Character.hexpat; the PS4 body fits too, so it
// rests on the PC reader 0x75ccf0). Walk: 9/9 fit, slack 4-7; PS4 framing fails 9/9.
// Body: CDataPartyMember PartyMember.
// packet-id: 8.37.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Character.hexpat"

struct S2C_PAWN_JOIN_PARTY_PAWN_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataPartyMember PartyMember;                           // PC 0x771580
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_JOIN_PARTY_PAWN_NTC packet @ 0x00;
