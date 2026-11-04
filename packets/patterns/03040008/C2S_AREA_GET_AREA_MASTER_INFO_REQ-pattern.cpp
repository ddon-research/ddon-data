// 23.0.1 C2S_AREA_GET_AREA_MASTER_INFO_REQ (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 18. PC writer 0x81e4c0:
// WritePacket(0x17, 0, 1, -1) + Write_u32, call site 0x81e533 (V). Name by pairing with the 23.0.2
// handler (I). PS4: CPacket_C2S_GET_AREA_MASTER_INFO_REQ.m_unAreaID, sender 0x19c1a60 (same caveat
// as 23.9.1: the match rests on the PC pairing, I).
// Body: u32 AreaID.
// packet-id: 23.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_AREA_GET_AREA_MASTER_INFO_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 AreaID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_AREA_GET_AREA_MASTER_INFO_REQ packet @ 0x00;
