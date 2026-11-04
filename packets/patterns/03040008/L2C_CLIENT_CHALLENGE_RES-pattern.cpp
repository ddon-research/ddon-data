// 1.0.2 L2C_CLIENT_CHALLENGE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 4.
// PC reader 0x8894c0 via handler 0x886970: header, Read_u8, Read_u8, loop Read_u8 x 0x3e
// (0x757da0) (V): s32 Error; Result and the body only when Error == 0 (T002
// section 0.2).
// PS4 CPacket_L2C_CLIENT_CHALLENGE_RES::ReadPacket 0x1a3d360, slot 6; DWARF {u16 m_usError,
// s32 m_nResult, u8 m_ucPasswordSrcSize, u8 m_ucPasswordEncSize, u8 m_ucPasswordEnc[62]}; the
// recompilation L2C.cpp reads the same (Error width aside) (V). The server writes 64 bytes of
// PasswordEnc; the client reads 62 (T002 section 16).
// Walk: 42/42 fit, slack 15; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, u8 PasswordSrcSize, u8 PasswordEncSize, u8 PasswordEnc[62]].
// packet-id: 1.0.2
// packet-select: L2C_CLIENT_CHALLENGE_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct L2C_CLIENT_CHALLENGE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u8 PasswordSrcSize;
        u8 PasswordEncSize;
        u8 PasswordEnc[62];
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

L2C_CLIENT_CHALLENGE_RES packet @ 0x00;
