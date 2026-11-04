// 44.0.2 S2C_CERT_CLIENT_CHALLENGE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 16.
// PC reader 0x8019e0 via handler 0x7c70c0 ("OnPacket_CERT_CLIENT_CHALLENGE_RES"): RES header,
// Read_u8 (+24), Read_u8 (+25), loop Read_u8 x 62 (0x757da0) (V) = login 1.0.2. PS4
// OnPacket_S2C_CLIENT_CHALLENGE_RES 0x330470 -> ReadPacket 0x19df0e0; DWARF {..., u8
// m_ucPasswordSrcSize, u8 m_ucPasswordEncSize, u8 m_ucPasswordEnc[62]}; recompilation S2C.cpp:2002
// agrees except the PC Error width (V). The server writes 64 bytes of PasswordEnc; the client
// reads 62 (T003 19).
// Walk: 83/83 fit, slack 15; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, u8 PasswordSrcSize, u8 PasswordEncSize, u8 PasswordEnc[62]].
// packet-id: 44.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CERT_CLIENT_CHALLENGE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u8 PasswordSrcSize;
        u8 PasswordEncSize;
        u8 PasswordEnc[62];                                 // Blowfish-ECB, 16 B + server residue
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CERT_CLIENT_CHALLENGE_RES packet @ 0x00;
