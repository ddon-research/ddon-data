// 54.0.1 C2S_CRAFT_RECIPE_GET_CRAFT_RECIPE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 14.
// PC writer 0x8258f0 (54, 0, 1): u8, u32, s32 (V). PS4 CPacket_C2S_GET_CRAFT_RECIPE_REQ::WritePacket
// 0x1a35ae0 {u8 in_Category, u32 in_Offset, s32 in_Num}: same (V).
// Walk: 3/3 fit; Category 1 or 26, Offset 0, Num 100.
// Body: u8 Category, u32 Offset, s32 Num (9 bytes).
// packet-id: 54.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CRAFT_RECIPE_GET_CRAFT_RECIPE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 Category;
    u32 Offset;
    s32 Num;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CRAFT_RECIPE_GET_CRAFT_RECIPE_REQ packet @ 0x00;
