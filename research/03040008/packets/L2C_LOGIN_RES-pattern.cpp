// 0.1.2 L2C_LOGIN_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 3. PC reader 0x889920,
// called at 0x8866a2 from handler code 0x886650 (stores 0, 1, 2; key 0x20001 of the login table
// 0x1bd6270) (V). PS4 cSeedLoginSvConnection::OnPacket_L2C_LOGIN_RES 0x37c800 reads u16, s32,
// MtString (nLoginSession::CPacket_L2C_LOGIN_RES); the PS4 recompilation (LoginSession/L2C.h) has
// the same members {u16 m_usError, s32 m_nResult, MtString m_wstrOnetimeToken}. PC reads Error as
// s32 (G1). The earlier `u8 pad[14]` is dropped: the client reads nothing after the token; the 14
// bytes are the cipher block padding (the token length is 31 in every capture) (V, C). The
// game-server S2C_CONNECTION_LOGIN_RES (reader 0x804a50) shares the id 0.1.2: export with the name
// filter `L2C_LOGIN_RES`, never with `@`.
// Body: s32 Error [, s32 Result, MtString OnetimeToken] (P11a G1).
// packet-id: 0.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct L2C_LOGIN_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtString OnetimeToken;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

L2C_LOGIN_RES packet @ 0x00;
