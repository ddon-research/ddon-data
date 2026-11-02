// 9.1.2 S2C_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 11.
// PC handler 0x7c6a00 (string "...OnPacket_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES") -> reader
// 0x8015b0: header only (V). PS4 OnPacket_S2C_SET_CHARACTER_BIN_SAVEDATA_RES 0x2e9060: header only (V).
// Request 9.1.1 (C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ, T001b) carries the save blob; the
// response carries none, so of 9.1.1's includes only Packet.hexpat is needed.
// Walk: 47/47 fit (Error 0 in all).
// Body: s32 Error [, s32 Result] (8 bytes).
// packet-id: 9.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES packet @ 0x00;
