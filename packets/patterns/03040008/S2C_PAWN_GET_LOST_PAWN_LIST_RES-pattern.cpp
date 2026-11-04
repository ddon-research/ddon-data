// 8.20.2 S2C_PAWN_GET_LOST_PAWN_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.5 (1.2 for the type).
// PC handler 0x7ea870, reader 0x8122d0: RES header, list 0x76d980 (CDataLostPawnList) (V). PS4
// OnPacket_S2C_GET_LOST_PAWN_LIST_RES 0x2e7470: m_PawnList (V). No Season 3 change. Walk: 20/20 fit,
// slack 11; the list is never non-empty (element code-only).
// Body: s32 Error [, s32 Result, list CDataLostPawnList].
// packet-id: 8.20.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PAWN_GET_LOST_PAWN_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataLostPawnList> PawnList;              // PC 0x76d980
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_LOST_PAWN_LIST_RES packet @ 0x00;
