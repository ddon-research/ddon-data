// 13.22.1 C2S_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 12 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x82c110 (13, 22, 1), no body (V). PS4 Send_C2S_GET_OM_INSTANT_KEY_VALUE_ALL_REQ
// 0x19bb870 (header only, V). Walk: 150/150 fit, slack 7 (a 16-byte raw fits any body of 0-7
// bytes, so the emptiness rests on the writer).
// Body: none.
// packet-id: 13.22.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_REQ packet @ 0x00;
