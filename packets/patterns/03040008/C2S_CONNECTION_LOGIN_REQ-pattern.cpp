// 0.1.1 C2S_CONNECTION_LOGIN_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 3.
// PC writer 0x8243b0: WritePacket(p, 0, 1, 1, -1), Write_cstr, Write_u8, Write_u32 (V). PS4
// CPacket_C2S_LOGIN_REQ::WritePacket 0x1a3aa40 MT_CSTR, u8, u32; DWARF {MtString m_wstrSessionKey,
// u8 m_ucPlatform, u32 m_unClientVersion} (V); recompilation stub signature agrees.
// Server lead misplacement: C2SConnectionLoginReq stops after Platform (4 bytes unread, T003 19).
// The login server's C2L_LOGIN_REQ shares the id 0.1.1: `// packet-select:` below.
// Walk: 42/42 fit, slack 1.
// Body: MtString SessionKey, u8 Platform, u32 ClientVersion.
// packet-id: 0.1.1
// packet-select: C2S_CONNECTION_LOGIN_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CONNECTION_LOGIN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtString SessionKey;
    u8 Platform;
    u32 ClientVersion;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONNECTION_LOGIN_REQ packet @ 0x00;
