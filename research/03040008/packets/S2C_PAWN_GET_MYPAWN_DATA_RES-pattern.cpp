// 8.3.2 S2C_PAWN_GET_MYPAWN_DATA_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.2 (1.1 for CDataPawnInfo).
// PC handler 0x7ea9d0, reader 0x812350: RES header, u32, CDataPawnInfo 0x772180 (V). PS4
// OnPacket_S2C_GET_MYPAWN_DATA_RES 0x2e3350: u32 m_unPawnID, CPawnInfo m_PawnInfo (V). Season 3:
// CDataPawnInfo (Pawn.hexpat; the PS4 body fails 72/72). Walk: 72/72 fit, slack 9-15.
// Body: s32 Error [, s32 Result, u32 PawnId, CDataPawnInfo PawnInfo].
// packet-id: 8.3.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PAWN_GET_MYPAWN_DATA_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 PawnId;
        CDataPawnInfo PawnInfo;                                 // PC 0x772180
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_MYPAWN_DATA_RES packet @ 0x00;
