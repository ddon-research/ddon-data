// 31.29.2 S2C_CLAN_CLAN_GET_MY_INFO_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 4. PC handler 0x7cb2b0
// (string 0x1bce704; 31, 29, 2), reader 0x8034d0 (V). PS4
// CPacket_S2C_CLAN_GET_MY_INFO_RES::ReadPacket 0x19db590 reads the same sequence; PS4
// CDataCharacterListElement lacks the Season 3 trailing u8 (V PS4).
// Body: s32 Error [, s32 Result, CDataClanParam, s64 LeaveTime] (P11a G1).
// packet-id: 31.29.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Clan.hexpat"

struct S2C_CLAN_CLAN_GET_MY_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataClanParam CreateParam;         // PC 0x75d730
        s64 LeaveTime;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CLAN_CLAN_GET_MY_INFO_RES packet @ 0x00;
