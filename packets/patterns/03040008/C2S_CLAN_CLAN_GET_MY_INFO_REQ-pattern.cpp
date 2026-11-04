// 31.29.1 C2S_CLAN_CLAN_GET_MY_INFO_REQ (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 1. PC writer 0x822af0:
// WritePacket(0x1F, 29, 1, -1), no body (V). Name by pairing with the 31.29.2 handler 0x7cb2b0 (I).
// PS4 cSeedGameSvConnection::Send_C2S_CLAN_GET_MY_INFO_REQ 0x19c43a0 writes only the header; DWARF
// CPacket_C2S_CLAN_GET_MY_INFO_REQ has no wire member (V PS4).
// Body: empty.
// packet-id: 31.29.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CLAN_CLAN_GET_MY_INFO_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CLAN_CLAN_GET_MY_INFO_REQ packet @ 0x00;
