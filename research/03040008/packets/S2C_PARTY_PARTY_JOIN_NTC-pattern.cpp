// 6.8.16 S2C_PARTY_PARTY_JOIN_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 6 (1, 18 for the types).
// PC handler 0x7e8a30 (gate sub_407AC0; read path 0x7e8a6f read instruction by instruction), reader
// 0x811120: u32, u32, list 0x7714c0 (CDataPartyMember 0x771580) (V). PS4 OnPacket_S2C_PARTY_JOIN_NTC
// 0x2e1410: u16 m_usError, u32 m_unLeaderCharacterID, u32 m_unHostCharacterID, m_PartyMember;
// cNetGameServer::OnPacket_S2C_PARTY_JOIN_NTC 0x36d330 adds the members and sets the party member
// info list (match V by behaviour). Season 3 only through CDataCharacterListElement's trailing u8
// (the PS4 element fits 43/43 too: every list holds one member; the reader decides). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Walk: 43/43 fit, slack 2-4; PS4 framing fails 43/43.
// Body: u32 LeaderCharacterID, u32 HostCharacterID, list CDataPartyMember.
// packet-id: 6.8.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_PARTY_PARTY_JOIN_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 LeaderCharacterID;
    u32 HostCharacterID;
    MtTypedArray<CDataPartyMember> PartyMember;  // PC 0x7714c0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTY_PARTY_JOIN_NTC packet @ 0x00;
