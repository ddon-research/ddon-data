// 31.4.2 S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 6. PC handler 0x7cb470
// (string 0x1bce618; 31, 4, 2), reader 0x8035e0; list reader 0x75d580 of CDataClanMemberInfo
// 0x75d640 (V). PS4 OnPacket_S2C_GET_MY_MEMBER_LIST_RES 0x317210: u16, s32,
// Read_CDataClanMemberInfo_ (V PS4).
// Body: s32 Error [, s32 Result, list CDataClanMemberInfo] (P11a G1).
// packet-id: 31.4.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Clan.hexpat"

struct S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataClanMemberInfo> MemberList;   // PC 0x75d580
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES packet @ 0x00;
