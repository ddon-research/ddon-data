// 1.4.2 S2C_SERVER_GET_REAL_TIME_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 12.
// PC reader 0x81a770 via handler 0x7f95c0: RES header, Read_u64 (+24), Read_u16 (+32) (V). PS4
// OnPacket_S2C_GET_REAL_TIME_RES 0x2de130 reads u16, u64, u16; DWARF {u16 m_usError,
// u64 m_ullRealTime, u16 m_usMilliseconds}. Season 3 difference (V): PC reads a Result after the
// Error (standard RES header), PS4 none.
// Walk: 87/87 fit, slack 5; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, u64 RealTime (Unix seconds), u16 Milliseconds].
// packet-id: 1.4.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_SERVER_GET_REAL_TIME_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u64 RealTime;                                       // Unix time, seconds (capture: 2019-07-06)
        u16 Milliseconds;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SERVER_GET_REAL_TIME_RES packet @ 0x00;
