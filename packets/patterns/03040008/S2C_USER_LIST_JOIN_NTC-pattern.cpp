// 5.2.16 S2C_USER_LIST_JOIN_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 2 (1, 18 for the types).
// PC handler 0x7fe5e0 (not a function start; read linearly): list 0x76d6f0 (CDataLobbyMemberInfo
// 0x76d7f0), then per element the lobby member add and the entry callback (CharacterID, PawnId) (V).
// PS4 cSeedGameSvConnection::OnPacket_S2C_USER_LIST_JOIN_NTC 0x2de740: u16 m_usError,
// m_LobbyMemberInfoList, cNetGameServer::addLobbyMember + sGame::callbackEntryLobby per element: same
// flow (match V by behaviour and list type). Season 3: the element has 3 u8 after PawnId, PS4 4 (V by
// reader; the PS4 4-u8 element fails 50/148). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Walk: 148/148 fit, slack 0-15; PS4 element fails 50/148, PS4 framing fails 148/148; lists up to 25.
// Body: list CDataLobbyMemberInfo.
// packet-id: 5.2.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_USER_LIST_JOIN_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataLobbyMemberInfo> LobbyMemberInfoList;  // PC 0x76d6f0; Season 3 element (3 u8)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_USER_LIST_JOIN_NTC packet @ 0x00;
