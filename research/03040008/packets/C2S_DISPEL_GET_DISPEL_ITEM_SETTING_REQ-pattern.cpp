// 51.2.1 C2S_DISPEL_GET_DISPEL_ITEM_SETTING_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 10.
// PC writer 0x826750 (51, 2, 1): u32 (V). PS4 Send_C2S_GET_DISPEL_ITEM_SETTING_REQ 0x19cd9d0: empty;
// match V by the RES string pair, Season 3 adds the u32. The empty PS4 body fits too (slack): the PC
// writer decides. Walk: 1/1 fit; value 23.
// Body: u32 unk_u32 (4 bytes).
// packet-id: 51.2.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_DISPEL_GET_DISPEL_ITEM_SETTING_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 unk_u32;   // Season 3, no PS4 member; server: ShopType (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_DISPEL_GET_DISPEL_ITEM_SETTING_REQ packet @ 0x00;
