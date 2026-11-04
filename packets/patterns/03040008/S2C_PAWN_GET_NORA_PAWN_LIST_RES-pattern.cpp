// 8.30.2 S2C_PAWN_GET_NORA_PAWN_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 14. PC handler 0x7eacd0
// (string 0x1bc7990; 8, 30, 2), reader 0x812500; list 0x776610 of CDataRegisterdPawnList 0x7766d0
// (V). PS4 OnPacket_S2C_GET_NORA_PAWN_LIST_RES 0x2e8a20 via Read_CDataRegisterdPawnList_: identical
// (V PS4). The PS4 recompilation has no class for the packet.
// Body: s32 Error [, s32 Result, list CDataRegisterdPawnList] (P11a G1).
// packet-id: 8.30.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Pawn.hexpat"

struct S2C_PAWN_GET_NORA_PAWN_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataRegisterdPawnList> NoraPawnList;   // PC 0x776610
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_NORA_PAWN_LIST_RES packet @ 0x00;
