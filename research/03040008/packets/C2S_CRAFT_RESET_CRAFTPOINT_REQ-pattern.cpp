// 30.12.1 C2S_CRAFT_RESET_CRAFTPOINT_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 3.
// PC writer 0x825a00 (30, 12, 1): u32 (V). PS4 Send_C2S_RESET_CRAFTPOINT_REQ 0x19cdd90(u32 in_PawnID) (V).
// Walk: 1/1 fit.
// Body: u32 PawnID (4 bytes).
// packet-id: 30.12.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CRAFT_RESET_CRAFTPOINT_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 PawnID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CRAFT_RESET_CRAFTPOINT_REQ packet @ 0x00;
