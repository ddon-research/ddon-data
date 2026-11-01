// 31.17.2 S2C_CLAN_CLAN_SETTING_UPDATE_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 5. PC handler 0x7cd0e0
// (string 0x1bceadc; 31, 17, 2), reader 0x8043c0 (V). PS4 OnPacket_S2C_CLAN_SETTING_UPDATE_RES
// 0x31ab10 reads u16, s32 (V PS4); the PS4 recompilation (UserSession/S2C.h) has {u16 m_usError,
// s32 m_nResult}. The earlier stub derived from an undefined CPacketDataBase and had no placement.
// Body: s32 Error [, s32 Result] (P11a G1).
// packet-id: 31.17.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CLAN_CLAN_SETTING_UPDATE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CLAN_CLAN_SETTING_UPDATE_RES packet @ 0x00;
