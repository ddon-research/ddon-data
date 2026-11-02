// 10.0.1 C2S_ITEM_USE_BAG_ITEM_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.1.
// PC writer 0x82d700 (10, 0, 1): Write_cstr (MtString), u32 (V). PS4 Send_C2S_USE_BAG_ITEM_REQ
// 0x19b6310: Write_MT_CSTR in_strUID, u32 in_Num (V). Walk: 18/18 fit, slack 9.
// Body: MtString UID, u32 Num (6 + length bytes).
// packet-id: 10.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_ITEM_USE_BAG_ITEM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtString UID;
    u32 Num;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ITEM_USE_BAG_ITEM_REQ packet @ 0x00;
