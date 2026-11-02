// 0.10.16 S2C_CONNECTION_SESSION_STATUS_NTC (client 03040008); CLI name until spec 006 TC2: S2C_CONNECTION_0_10_16_NTC.
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 9.
// Code-backed name: SESSION_STATUS_NTC (V by behaviour, T003 9), carried by the raws and this
// pattern since the CLI relabel of spec 006 TC2; PS4 cSeedGameSvConnection::OnPacket_S2C_SESSION_STATUS_NTC
// 0x2deb90; Arrowgene S2C_CONNECTION_0_10_16_NTC / S2CConnection_10_Ntc (lead).
// PC handler 0x7cec00 (no name string), reader 0x804da0: Read_u32 (+16), Read_u8 (+20), no error
// header (V). The handler finds the lobby member whose CharacterID equals the u32 and stores the
// u8 to its SessionStatus byte (+0x21) (V, 0x7cebb0). PS4 DWARF CPacket_S2C_SESSION_STATUS_NTC
// {u16 m_usError, u32 m_unCharacterID, u8 m_ucSessionStatus}; Season 3 difference: no u16 error (V).
// Walk: 2/2 fit, slack 2.
// Body: u32 CharacterID, u8 SessionStatus.
// packet-id: 0.10.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CONNECTION_SESSION_STATUS_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterID;
    u8 SessionStatus;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONNECTION_SESSION_STATUS_NTC packet @ 0x00;
