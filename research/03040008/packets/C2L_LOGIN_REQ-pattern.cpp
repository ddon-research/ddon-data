// 0.1.1 C2L_LOGIN_REQ (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 2. PC writer 0x88a390
// (login packet block 0x889f40-0x88a980): WritePacket(0, 1, 1, -1), Write_cstr (0x8bca30: u16 BE
// length + bytes, the MtString wire), Write_u8 (V). PS4 cSeedLoginSvConnection::Send_C2L_LOGIN_REQ
// 0x1a3c1f0 writes Write_MT_CSTR, Write_u8; DWARF nLoginSession::CPacket_C2L_LOGIN_REQ
// {m_wstrOnetimeToken, m_ucPlatform} (V PS4). The login-server class attribution of 0x88a390 is I
// (P11b "Left open"). The game-server C2S_CONNECTION_LOGIN_REQ (writer 0x8243b0: cstr, u8, u32)
// shares the id 0.1.1: `// packet-select:` below makes `@` take only the C2L_LOGIN_REQ files
// (imhex-export.sh refuses `@` on a shared id without it; spec 005 R2 F2).
// Body: MtString OnetimeToken, u8 Platform.
// packet-id: 0.1.1
// packet-select: C2L_LOGIN_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2L_LOGIN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtString OnetimeToken;
    u8 Platform;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2L_LOGIN_REQ packet @ 0x00;
