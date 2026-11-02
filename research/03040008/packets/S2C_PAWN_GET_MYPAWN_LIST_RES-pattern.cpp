// 8.2.2 S2C_PAWN_GET_MYPAWN_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.1 (1.2, 1.3 for the types).
// PC handler 0x7eab80, reader 0x8123e0: RES header, list 0x7725c0 (CDataPawnList), 0x7710a0
// (CDataPartnerPawnData) (V). PS4 CPacket_S2C_GET_MYPAWN_LIST_RES::ReadPacket 0x19d5460: m_PawnList,
// CPartnerPawnData m_PartnerInfo (V). Season 3: three trailing u32 per CDataPawnList element (V; the
// PS4 element fails 119/119). Walk: 119/119 fit, slack 1-11.
// Body: s32 Error [, s32 Result, list CDataPawnList, CDataPartnerPawnData PartnerInfo].
// packet-id: 8.2.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PAWN_GET_MYPAWN_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataPawnList> PawnList;                  // PC 0x7725c0
        CDataPartnerPawnData PartnerInfo;                       // PC 0x7710a0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_MYPAWN_LIST_RES packet @ 0x00;
