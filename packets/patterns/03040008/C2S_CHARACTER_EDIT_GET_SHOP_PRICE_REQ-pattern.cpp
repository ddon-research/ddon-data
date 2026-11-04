// 41.8.1 C2S_CHARACTER_EDIT_GET_SHOP_PRICE_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 41.8.1.
// PC writer 0x821440: WritePacket(0x29, 8, 1), no body writes (V). Name: CLI/server (G (lead)).
// Walk: 4/4 fit, slack 7.
// Body: none.
// packet-id: 41.8.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CHARACTER_EDIT_GET_SHOP_PRICE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHARACTER_EDIT_GET_SHOP_PRICE_REQ packet @ 0x00;
