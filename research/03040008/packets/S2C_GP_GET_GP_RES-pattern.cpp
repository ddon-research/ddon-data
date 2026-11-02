// 28.0.2 S2C_GP_GET_GP_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 2.
// PC handler 0x7d73b0, reader 0x808f70: u32, s64, u64, u16 (V). PS4
// CPacket_S2C_GET_GP_RES::ReadPacket 0x19d7af0 {u32 m_unGP, s64 m_llUseLimit, u64 m_ullRealTime,
// u16 m_usMilliseconds}: same (V); the PS4 recompilation (S2C.cpp) agrees.
// Walk: 4/4 fit, slack 9.
// Body: s32 Error [, s32 Result, u32 GP, s64 UseLimit, u64 RealTime, u16 Milliseconds].
// packet-id: 28.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_GP_GET_GP_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 GP;
        s64 UseLimit;
        u64 RealTime;
        u16 Milliseconds;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_GET_GP_RES packet @ 0x00;
