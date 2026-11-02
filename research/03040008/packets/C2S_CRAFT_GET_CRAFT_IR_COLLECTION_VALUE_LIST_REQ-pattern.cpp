// 30.15.1 C2S_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 3.
// PC writer 0x8252f0 (30, 15, 1): empty (V). PS4 0x19be820: empty.
// Walk: 2/2 fit.
// Body: none.
// packet-id: 30.15.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_REQ packet @ 0x00;
