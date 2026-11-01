// 60.0.1 C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 12. PC writer 0x830cf0:
// WritePacket(0x3C, 0, 1, -1), Write_u32 (V); pairs with the 60.0.2 handler code 0x7e6300 (I). No
// PS4 counterpart (no symbol or DWARF type *NPC_GET_NPC_EXTENDED_FACILITY* in 02020005; none in the
// PS4 recompilation).
// Body: u32 NpcID (name from the earlier pattern / server lead: I).
// packet-id: 60.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 NpcID;   // name not evidenced (I)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ packet @ 0x00;
