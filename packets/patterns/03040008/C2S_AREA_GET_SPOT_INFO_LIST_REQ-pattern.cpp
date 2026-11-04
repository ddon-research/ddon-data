// 23.11.1 C2S_AREA_GET_SPOT_INFO_LIST_REQ (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 8. PC writer 0x81e930:
// WritePacket(0x17, 11, 1, -1), Write_u32 (V); pairs with 23.11.2 (I). PS4
// Send_C2S_GET_SPOT_INFO_LIST_REQ 0x19c2330: header + u32 m_unAreaID (V PS4).
// Body: u32 AreaID.
// packet-id: 23.11.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_AREA_GET_SPOT_INFO_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 AreaID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_AREA_GET_SPOT_INFO_LIST_REQ packet @ 0x00;
