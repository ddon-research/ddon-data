// 25.5.2 S2C_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 8.
// PC handler 0x7e64d0 (not a function in the database), reader 0x810120: header, 0x7701c0 (13 x u16)
// (V). PS4 0x305320: header, Read_CDataOrbGainExtendParam_ 0x1a04c60 (m_ExtendParam): same (V).
// Walk: 43/43 fit, slack 5.
// Body: s32 Error [, s32 Result, CDataOrbGainExtendParam (26 bytes)].
// packet-id: 25.5.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Pawn.hexpat"

struct S2C_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataOrbGainExtendParam ExtendParam;   // PC 0x7701c0 (Pawn.hexpat)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_RES packet @ 0x00;
