// 18.0.1 C2S_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 11.
// PC writer 0x82a310 (18, 0, 1): Write_u64 (V). PS4 Send_C2S_GROUP_CHAT_GET_MEMBER_LIST_REQ
// 0x19ca2d0(u64 in_GroupID): same (V).
// Walk: 41/41 fit; GroupID 0 in all.
// Body: u64 GroupID (8 bytes).
// packet-id: 18.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u64 GroupID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_REQ packet @ 0x00;
