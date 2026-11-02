// 5.3.16 S2C_USER_LIST_LEAVE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 3.
// PC handler 0x7fe7a0: list 0x75e8e0 (CDataCommonU32), then removes each lobby member with that id
// (+8 == id, +0x1c == 0) (V). PS4 0x2dea20: u16 m_usError, m_CharacterList (CDataCommonU32);
// cNetGameServer::OnPacket_S2C_USER_LIST_LEAVE_NTC does the same removal and
// sGame::callbackLeaveLobby (match V by behaviour). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Walk: 162/162 fit, slack 3-15; PS4 framing fails 162/162; lists up to 9.
// Body: list CDataCommonU32.
// packet-id: 5.3.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_USER_LIST_LEAVE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataCommonU32> CharacterList;  // PC 0x75e8e0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_USER_LIST_LEAVE_NTC packet @ 0x00;
