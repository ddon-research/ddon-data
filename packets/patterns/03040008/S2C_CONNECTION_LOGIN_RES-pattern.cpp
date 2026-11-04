// 0.1.2 S2C_CONNECTION_LOGIN_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 3.
// PC reader 0x804a50 via handler 0x7ce490 ("OnPacket_CONNECTION_LOGIN_RES"): RES header,
// Read_bool (+24), Read_MtString (+28) (V). PS4 OnPacket_S2C_LOGIN_RES 0x2dcde0 u16, s32, bool,
// MtString; DWARF {u16 m_usError, s32 m_nResult, b8 m_bIsCogLogin, MtString m_wstrOnetimeToken} (V).
// Server lead misplacement: IsCogLogin is 1 byte, not u16 (capture-confirmed, T003 3, 19).
// The login server's L2C_LOGIN_RES shares the id 0.1.2: `// packet-select:` below.
// Walk: 42/42 fit, slack 13; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, bool IsCogLogin, MtString OnetimeToken].
// packet-id: 0.1.2
// packet-select: S2C_CONNECTION_LOGIN_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CONNECTION_LOGIN_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        bool IsCogLogin;
        MtString OnetimeToken;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONNECTION_LOGIN_RES packet @ 0x00;
