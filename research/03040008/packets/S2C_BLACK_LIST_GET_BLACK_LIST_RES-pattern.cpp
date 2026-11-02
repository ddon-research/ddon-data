// 17.0.2 S2C_BLACK_LIST_GET_BLACK_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 12.
// PC handler 0x7c6ba0, reader 0x8016c0: header, list 0x75ebc0 (CDataCommunityCharacterBaseInfo) (V).
// PS4 0x2faa40 {m_BlackList}: same (V).
// Walk: 41/41 fit, slack 11; the list is always empty (element code-only).
// Body: s32 Error [, s32 Result, list CDataCommunityCharacterBaseInfo].
// packet-id: 17.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

struct S2C_BLACK_LIST_GET_BLACK_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCommunityCharacterBaseInfo> BlackList;  // PC 0x75ebc0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_BLACK_LIST_GET_BLACK_LIST_RES packet @ 0x00;
